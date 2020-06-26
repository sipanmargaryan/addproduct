from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, F
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views import generic

import ads.filters
import ads.forms
import ads.mixins
import ads.models
import ads.utils
import core.models
import core.utils

__all__ = (
    'AdDetailView',
    'DeleteAdView',
    'RePublishAdView',
    'ToggleAdStatusView',
    'AddAnAdView',
    'EditAnAdView',
    'AddCommentView',
)


class AdDetailView(ads.mixins.RelatedDataMixin, generic.DetailView):
    template_name = 'ads/ad_detail.html'
    context_object_name = 'ad'
    queryset = ads.models.Ad.objects.active()

    def get_queryset(self):
        self.queryset = ads.models.AdImage.primary_image(self.queryset)
        if self.request.user.is_authenticated:
            self.queryset = ads.models.FavoriteAd.is_favorite(self.queryset, self.request.user)

        return self.queryset.select_related('city', 'user')

    def get_context_data(self, **kwargs):
        context = super(AdDetailView, self).get_context_data(**kwargs)
        context['images'] = self.ad_images()
        context['comments'] = self.ad_comments()
        context['review_metrics'] = self.review_metrics()
        context['recommended_ads'] = self.recommended()
        context['contact_detail'] = ads.models.ContactDetail.objects.filter(ad=context['ad']).first()
        related_data = self.get_related_data(context['ad'])
        if related_data:
            context['related_data'] = {
                k.replace('_', ' ').capitalize(): str(v).replace('_', ' ').capitalize()
                for k, v in related_data.items()
                if 'id' not in k and v
            }
        return context

    def get(self, request, *args, **kwargs):
        # noinspection PyAttributeOutsideInit
        self.object = self.get_object()

        if self.object.slug != self.kwargs.pop('slug', None):
            return redirect(self.object.get_absolute_url(), permanent=True)

        self.view_ad()

        return super().get(request, *args, **kwargs)

    def ad_images(self):
        return ads.models.AdImage.select_images(self.get_object().pk)

    def ad_comments(self):
        return ads.models.Comment.objects.filter(ad=self.get_object().pk).order_by('-created')

    def view_ad(self):
        self.queryset.filter(pk=self.object.pk).update(views=F('views') + 1)

    def review_metrics(self):
        queryset = ads.models.AdReview.objects.filter(ad=self.get_object().pk)
        return dict(
            count=queryset.count(),
            average=queryset.aggregate(avg=Avg('rating'))['avg'],
        )

    def recommended(self):
        queryset = ads.models.AdImage.primary_image(
            ads.models.Ad.objects.active()
            .exclude(pk=self.get_object().pk)
            .order_by('-publish_date')
        )

        if self.request.user.is_authenticated:
            queryset = ads.models.FavoriteAd.is_favorite(queryset, self.request.user)

        top_ad_list = list(
            queryset
            .filter(
                premium_until__gte=timezone.now(),
                category=self.get_object().category
            )
            .order_by('?')[:6]
        )

        if len(top_ad_list) < 6:
            top_ad_list.extend(
                queryset
                .filter(premium_until__gte=timezone.now())
                .exclude(pk__in=[ad.pk for ad in top_ad_list])
                .order_by('?')
                [:6 - len(top_ad_list)]
            )

        if len(top_ad_list) < 6:
            top_ad_list.extend(
                queryset
                .exclude(pk__in=[ad.pk for ad in top_ad_list])
                .order_by('-publish_date')
                [:6 - len(top_ad_list)]
            )

        return top_ad_list


class DeleteAdView(LoginRequiredMixin, generic.View):
    model = ads.models.Ad

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):
        ad_id = request.POST.get('ad_id')
        self.model.objects.filter(pk=ad_id, user=request.user).delete()
        return HttpResponse(status=204)


class RePublishAdView(LoginRequiredMixin, generic.View):
    model = ads.models.Ad

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):
        ad_id = request.POST.get('ad_id')
        ad = self.model.objects.filter(pk=ad_id, user=request.user).first()

        if not ad:
            raise Http404

        ad.republish()

        return JsonResponse({'publish_date': ad.publish_date.strftime('%d.%m.%Y')})


class ToggleAdStatusView(LoginRequiredMixin, generic.View):
    model = ads.models.Ad

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):
        ad_id = request.POST.get('ad_id')
        ad = self.model.objects.filter(pk=ad_id, user=request.user).first()

        if not ad:
            raise Http404

        ad.toggle_status()

        return JsonResponse({'is_active': bool(ad.status)})


class AddCommentView(LoginRequiredMixin, generic.FormView):
    form_class = ads.forms.CommentForm

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.user = self.request.user
        comment.save()

        return redirect(comment.ad.get_absolute_url())

    def form_invalid(self, form):
        return HttpResponse(form.errors, status=400)


class AddAnAdView(LoginRequiredMixin, ads.mixins.AdMixin, generic.TemplateView):
    template_name = 'ads/add_edit.html'
    form = ads.forms.AdForm
    contact_form = ads.forms.ContactDetailForm
    car_ad_form = ads.forms.CarAdForm
    estate_ad_form = ads.forms.RealEstateAdForm

    def get_context_data(self, **kwargs):
        context = super(AddAnAdView, self).get_context_data(**kwargs)
        context['form'] = self.form()
        context['contact_form'] = self.contact_form(initial=self.get_contact_form_data())
        context['car_ad_form'] = self.car_ad_form()
        context['estate_ad_form'] = self.estate_ad_form()
        context['price_per_day'] = ads.utils.get_kwd_for_one_day()

        context['makes'] = ads.models.CarMakeCategory.objects.all()
        context['brands'] = ads.models.MobileBrandCategory.objects.all()

        return context

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):
        form, contact_form, errors = self.validate_request(request)

        if len(errors):
            return JsonResponse(errors, status=400)

        images = list(request.FILES.values())

        if not len(images):
            return HttpResponse(status=204)

        ad = form.save(commit=False)
        ad.city = core.models.City.objects.get(pk=form.cleaned_data['city'])
        ad.category = ads.models.Category.objects.get(pk=form.cleaned_data['category'])
        ad.user = request.user
        ad.save()

        contact_detail = contact_form.save(commit=False)
        contact_detail.ad = ad
        contact_detail.save()

        ads.models.AdImage.attach_to_ad(ad, images)

        self.create_subcategories(request, ad)

        payment_url = self.ad_payment(request, ad)
        next_url = payment_url or ad.get_absolute_url()

        return JsonResponse({'next_url': next_url}, status=201)


class EditAnAdView(LoginRequiredMixin, ads.mixins.AdMixin, generic.DetailView):
    queryset = ads.models.Ad.objects.all()
    form = ads.forms.AdForm
    contact_form = ads.forms.ContactDetailForm
    car_ad_form = ads.forms.CarAdForm
    estate_ad_form = ads.forms.RealEstateAdForm
    template_name = 'ads/add_edit.html'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(EditAnAdView, self).get_context_data(**kwargs)

        # noinspection PyAttributeOutsideInit
        self.object = self.get_object()

        context['ad'] = self.object
        context['related'] = self.object.get_related_object()
        context['form'] = self.form(instance=self.object)
        context['images'] = self.ad_images(self.object.pk)
        context['contact_form'] = self.contact_form(initial=self.get_contact_form_data())
        context['price_per_day'] = ads.utils.get_kwd_for_one_day()

        context['car_ad_form'] = self.car_ad_form(
            instance=context['related'] if isinstance(context['related'], ads.models.CarAd) else None
        )
        context['estate_ad_form'] = self.estate_ad_form(
            instance=context['related'] if isinstance(context['related'], ads.models.RealEstateAd) else None
        )

        context['makes'] = ads.models.CarMakeCategory.objects.all()
        context['brands'] = ads.models.MobileBrandCategory.objects.all()

        return context

    @staticmethod
    def ad_images(pk):
        return ads.models.AdImage.objects.filter(ad=pk).order_by('-is_primary')

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):

        # noinspection PyAttributeOutsideInit
        self.object = self.get_object()

        form, contact_form, errors = self.validate_request(request)

        if len(errors):
            return JsonResponse(errors, status=400)

        images = list(request.FILES.values())
        existing_images = list(filter(lambda x: x, [request.POST.get(f'image-{i}') for i in range(5)]))
        existing_images = ads.models.AdImage.objects.filter(ad=self.object, pk__in=existing_images)[:]

        if not len(images) and not len(existing_images):
            return HttpResponse(status=204)

        ad = form.save(commit=False)
        ad.city = core.models.City.objects.get(pk=form.cleaned_data['city'])
        ad.category = ads.models.Category.objects.get(pk=form.cleaned_data['category'])
        ad.save()

        contact_detail = contact_form.save(commit=False)
        contact_detail.ad = ad
        contact_detail.save()

        old_images = ads.models.AdImage.objects.filter(ad=ad)
        if len(existing_images):
            old_images = old_images.exclude(pk__in=[img.pk for img in existing_images])
        old_images.delete()

        if len(images):
            ads.models.AdImage.attach_to_ad(ad, images, primary=all([not img.is_primary for img in existing_images]))

        self.create_subcategories(request, ad)

        payment_url = self.ad_payment(request, ad)
        next_url = payment_url or ad.get_absolute_url()

        return JsonResponse({'next_url': next_url}, status=201)
