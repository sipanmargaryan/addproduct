from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Max, Min, OuterRef
from django.http import Http404, JsonResponse
from django.shortcuts import render_to_response
from django.utils import timezone
from django.views import generic

import ads.filters
import ads.forms
import ads.models
import common.models
import core.models
import core.utils
import events.models
import messaging.models

__all__ = (
    'FavoriteAdsView',
    'AddRemoveFavorite',
    'MyAdsView',
    'HomeAdsView',
    'AdsView',
    'SellerView',
    'SaveSearchView',
)


class FavoriteAdsView(LoginRequiredMixin, generic.ListView):
    template_name = 'ads/favorites.html'
    context_object_name = 'favorites'
    paginate_by = 10

    def get_queryset(self):
        queryset = ads.models.FavoriteAd.objects.filter(user=self.request.user).select_related('ad')
        return ads.models.AdImage.primary_image(queryset, outer_ref='ad__pk')


class AddRemoveFavorite(LoginRequiredMixin, generic.View):
    # noinspection PyMethodMayBeStatic, PyUnusedLocal
    def post(self, request, *args, **kwargs):
        ad = ads.models.Ad.objects.filter(id=request.POST.get('ad_id')).first()
        if ad:
            favorite, created = ads.models.FavoriteAd.objects.get_or_create(
                user=request.user, ad=ad,
            )

            is_favorite = created
            if not is_favorite:
                # Remove from favorites if it's exist
                favorite.delete()

            return JsonResponse({'is_favorite': is_favorite})

        raise Http404


class MyAdsView(LoginRequiredMixin, generic.ListView):
    template_name = 'ads/my.html'
    context_object_name = 'ads'
    paginate_by = None
    queryset = ads.models.Ad.objects.all()

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        filter_by = self.request.GET.get('filter_by', None)
        if filter_by == 'active':
            queryset = queryset.filter(status=1)
        elif filter_by == 'inactive':
            queryset = queryset.filter(status=0)

        queryset = ads.models.AdImage.primary_image(queryset)
        queryset = self.count_messages(queryset)
        return queryset.order_by('-publish_date')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MyAdsView, self).get_context_data(object_list=object_list, **kwargs)
        context['filter_by'] = self.request.GET.get('filter_by')
        return context

    @staticmethod
    def count_messages(queryset):
        """
        Counts all messages for each ad.
        :param queryset:
        :return:
        """
        messages = messaging.models.Message.objects.filter(thread__ad=OuterRef('pk')).only('pk')
        return queryset.annotate(message_count=core.utils.SubqueryCount(messages))


class HomeAdsView(generic.TemplateView):
    template_name = 'ads/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeAdsView, self).get_context_data(**kwargs)
        context['categories'] = self.top_categories()
        context['ads'] = self.top_ads()
        context['events'] = events.models.Event.top_events()
        context['cities'] = core.models.City.objects.order_by('name')
        context['services'] = common.models.Service.objects.order_by('name')
        return context

    @staticmethod
    def top_categories():
        categories = ads.models.Category.objects.values('id', 'name')

        car_makes = cache.get('car_makes')
        if not car_makes:
            car_makes = ads.models.CarMakeCategory.objects.order_by('name').values('id', 'name')
            cache.set('car_makes', car_makes)

        mobile_brands = cache.get('mobile_brands')
        if not mobile_brands:
            mobile_brands = ads.models.MobileBrandCategory.objects.order_by('name').values('id', 'name')
            cache.set('mobile_brands', mobile_brands)

        for category in categories:
            if category['name'] == 'Cars':
                category['subcategories'] = car_makes

            if category['name'] == 'Real Estate':
                category['subcategories'] = []
                for _id, name in ads.models.RealEstateAd.ESTATE_TYPES:
                    category['subcategories'].append(dict(
                        id=_id,
                        name=name,
                    ))

            if category['name'] == 'Mobile':
                category['subcategories'] = mobile_brands

        return categories

    def top_ads(self):
        queryset = ads.models.Ad.objects.select_related('city')
        queryset = ads.models.AdImage.primary_image(queryset)

        if self.request.user.is_authenticated:
            queryset = ads.models.FavoriteAd.is_favorite(queryset, self.request.user)

        top_ad_list = list(queryset.filter(premium_until__gte=timezone.now()).order_by('?')[:6])

        if len(top_ad_list) < 6:
            top_ad_list.extend(
                queryset
                .exclude(pk__in=[ad.pk for ad in top_ad_list])
                .order_by('-publish_date')
                [:6 - len(top_ad_list)]
            )

        return top_ad_list


class AdsView(generic.ListView):
    template_name = 'ads/ads.html'
    paginate_by = 9
    context_object_name = 'ads'
    queryset = ads.models.Ad.objects.active()

    def get_queryset(self):
        # noinspection PyAttributeOutsideInit
        self.filter_data = ads.filters.AdFilter(self.request.GET, queryset=self.queryset)
        queryset = ads.models.AdImage.primary_image(self.filter_data.qs)

        if self.request.user.is_authenticated:
            queryset = ads.models.FavoriteAd.is_favorite(queryset, self.request.user)

        # noinspection PyAttributeOutsideInit
        self.sort_by = self.request.GET.get('sort', '-publish_date')
        return queryset.order_by(self.sort_by)

    def get(self, request, *args, **kwargs):
        if self.request.is_ajax():
            queryset = self.get_queryset()
            page_offset = int(request.GET.get('page'))
            return render_to_response(
                'ads/ads_ajax.html',
                context={'ads': queryset[(page_offset - 1) * 12:page_offset * 12]},
            )

        return super(AdsView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AdsView, self).get_context_data(**kwargs)
        if not self.request.is_ajax():
            context['ads_data'] = self.queryset.aggregate(Min('price'), Max('price'))
            context['ads_count'] = self.queryset.count()
            context['categories_ads'] = self.count_category_ads()
            context['filter_form'] = self.filter_data.form
            context['top_ads'] = self.top_ads()
            context['sort_by'] = self.sort_by
            context['cities'] = core.models.City.objects.all()

        return context

    @staticmethod
    def count_category_ads():
        return ads.models.Category.category_ads_count()

    def top_ads(self):
        queryset = ads.models.Ad.objects.select_related('city')
        queryset = ads.models.AdImage.primary_image(queryset)

        if self.request.user.is_authenticated:
            queryset = ads.models.FavoriteAd.is_favorite(queryset, self.request.user)

        top_ad_list = []

        if self.request.GET.get('category'):
            filter_data = ads.filters.AdFilter({'category': self.request.GET.get('category')}, queryset=queryset)

            top_ad_list = list(
                filter_data
                .qs
                .filter(premium_until__gte=timezone.now())
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

        return top_ad_list


class SellerView(generic.ListView):
    queryset = ads.models.Ad.objects.active()
    template_name = 'ads/seller.html'
    context_object_name = 'ads'
    paginate_by = 12

    def get_queryset(self):
        # noinspection PyAttributeOutsideInit
        self.seller = get_user_model().objects.filter(pk=self.kwargs['user']).first()
        if not self.seller:
            raise Http404

        queryset = self.queryset.filter(user=self.seller).select_related('city')
        queryset = ads.models.AdImage.primary_image(queryset)

        if self.request.user.is_authenticated:
            queryset = ads.models.FavoriteAd.is_favorite(queryset, self.request.user)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SellerView, self).get_context_data(object_list=object_list, **kwargs)
        context['author'] = self.seller
        return context


class SaveSearchView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'ads/save_search.html'

    def get_context_data(self, **kwargs):
        context = super(SaveSearchView, self).get_context_data(**kwargs)
        context['searches'] = ads.models.SavedSearch.objects.filter(user=self.request.user)
        return context

    # noinspection PyMethodMayBeStatic, PyUnusedLocal
    def post(self, request, *args, **kwargs):

        data = dict(
            q=request.POST.get('q'),
            seller_type=request.POST.get('seller_type'),
            city=request.POST.get('city'),
            categories=request.POST.getlist('category'),
            price_min=request.POST.get('price_min'),
            price_max=request.POST.get('price_max'),
            status=request.POST.get('status'),
        )

        if any(data.values()):
            ads.models.SavedSearch.objects.get_or_create(data=data, user=request.user)

        return JsonResponse({'success': True})

    # noinspection PyMethodMayBeStatic, PyUnusedLocal
    def delete(self, request, *args, **kwargs):
        (
            ads.models.SavedSearch
            .objects
            .filter(user=request.user, pk=request.GET.get('pk'))
            .delete()
        )

        return JsonResponse({'success': True})
