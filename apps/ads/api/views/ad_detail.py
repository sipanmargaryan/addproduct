from rest_framework import generics, mixins, permissions, views
from rest_framework.response import Response

from django.http import Http404, JsonResponse

import ads.models
import ads.utils
import core.models
from ads.mixins import AdMixin

from ..serializers import *  # noqa

__all__ = (
    'AdDestroyView',
    'AddAnAdAPIView',
    'UpdateAdStatusAPIView',
    'AdDetailAPIView',
    'AdCommentAPIView',
    'CategoriesAPIView',
    'RemoveFavoriteAdAPIView',
    'AddFavoriteAdAPIView',
    'RePublishAdAPIView',
    'CurrencyAPIView',
)


class AdDestroyView(generics.DestroyAPIView):
    queryset = ads.models.Ad.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AdSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class AddAnAdAPIView(AdMixin, views.APIView):
    serializer_class = AdAnAddInfoSerializer
    permission_classes = (permissions.IsAuthenticated,)

    # noinspection PyUnusedLocal
    def get(self, request):
        return Response({
            'categories': ads.models.Category.objects.all().values('pk', 'name'),
            'cities': core.models.City.objects.all().values('pk', 'name'),
            'is_seller_private': ads.models.Ad.SELLER_TYPES,
            'state': ads.models.Ad.STATES,
            'contact_data': self.get_contact_form_data(),
        })

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):
        """
        Add an Ad endpoint
        Payload for POST request
        - title* (text)
        - description* (text)
        - price* (integer)
        - currency* ('kwd', 'usd')
        - is_seller_private* (boolean)
        - state* ('new', 'used')
        - city*
        - category*
        - premium_days (if payment selected)
        - multiple files for images (at least one image)
        --- Contact Details
        - email*
        - phone_number*
        - full_name*
        --- Mobile only
        - brand* (integer)
        - model* (integer)
        --- Cars only
        - make* (integer)
        - model* (integer)
        - mileage (integer)
        - year (integer 1900-2019)
        - body_style (choices)
        --- Real Estate only
        - purpose* ('for_sell', 'for_rent')
        - bathrooms (integer)
        - bedrooms (integer)
        - estate_type (choices)
        """
        ad_serializer = AdCreateSerializer(data=request.data)
        contact_serializer = AdContactSerializer(data=request.data)

        ad_valid = ad_serializer.is_valid(raise_exception=False)
        contact_valid = contact_serializer.is_valid(raise_exception=False)
        if not ad_valid or not contact_valid:
            return JsonResponse({**ad_serializer.errors, **contact_serializer.errors}, status=400)

        ad_data = ad_serializer.validated_data
        contact_data = contact_serializer.validated_data

        images = list(request.FILES.values())

        if not len(images):
            return Response(status=204)

        ad_data['city'] = core.models.City.objects.get(pk=ad_data['city'])
        ad_data['category'] = ads.models.Category.objects.get(pk=ad_data['category'])
        ad = ads.models.Ad(**ad_data)
        ad.user = request.user
        ad.save()

        contact_detail = ads.models.ContactDetail(**contact_data)
        contact_detail.ad = ad
        contact_detail.save()

        ads.models.AdImage.attach_to_ad(ad, images)

        self.create_subcategories(request, ad)

        payment = self.ad_payment(request, ad, False)
        response = {
            'ad_id': ad.pk,
        }
        if payment:
            response['payment_id'] = payment.pk

        return JsonResponse(response, status=201)

    # noinspection PyUnusedLocal
    def put(self, request, *args, **kwargs):
        """
        Edit Ad endpoint
        Payload for PUT request
        - id* (text)
        - title* (text)
        - description* (text)
        - price* (integer)
        - currency* ('kwd', 'usd')
        - is_seller_private* (boolean)
        - state* ('new', 'used')
        - city* (integer)
        - category* (integer)
        - image-1* (existing image)
        - image-2* (existing image)
        - image-n* (existing image)
        - premium_days (if payment selected)
        - multiple files for images (at least one image)
        --- Contact Details
        - email*
        - phone_number*
        - full_name*
        --- Mobile only
        - brand* (integer)
        - model* (integer)
        --- Cars only
        - make* (integer)
        - model* (integer)
        - mileage (integer)
        - year (integer 1900-2019)
        - body_style (choices)
        --- Real Estate only
        - purpose* ('for_sell', 'for_rent')
        - bathrooms (integer)
        - bedrooms (integer)
        - estate_type (choices)
        """
        ad = ads.models.Ad.objects.filter(pk=request.data.get('id'), user=request.user).first()
        if not ad:
            raise Http404

        ad_serializer = AdCreateSerializer(data=request.data, instance=ad)
        contact_detail = ads.models.ContactDetail.objects.filter(ad=ad).first()
        contact_serializer = AdContactSerializer(data=request.data, instance=contact_detail)

        ad_valid = ad_serializer.is_valid(raise_exception=False)
        contact_valid = contact_serializer.is_valid(raise_exception=False)
        if not ad_valid or not contact_valid:
            return JsonResponse({**ad_serializer.errors, **contact_serializer.errors}, status=400)

        ad_data = ad_serializer.validated_data
        contact_data = contact_serializer.validated_data

        images = list(request.FILES.values())
        existing_images = list(filter(lambda x: x, [request.POST.get(f'image-{i}') for i in range(7)]))
        existing_images = ads.models.AdImage.objects.filter(ad=ad, pk__in=existing_images)[:]

        if not len(images) and not len(existing_images):
            return Response('No images', status=204)

        ad_data['city'] = core.models.City.objects.get(pk=ad_data['city'])
        ad_data['category'] = ads.models.Category.objects.get(pk=ad_data['category'])
        ad = ad_serializer.update(ad, ad_data)
        contact_detail = contact_serializer.update(contact_detail, contact_data)

        old_images = ads.models.AdImage.objects.filter(ad=ad)
        if len(existing_images):
            old_images = old_images.exclude(pk__in=[img.pk for img in existing_images])
        old_images.delete()

        if len(images):
            ads.models.AdImage.attach_to_ad(ad, images,
                                            primary=all([not img.is_primary for img in existing_images]))

        self.create_subcategories(request, ad)

        payment = self.ad_payment(request, ad, False)
        response = {
            'ad_id': ad.pk,
        }
        if payment:
            response['payment_id'] = payment.pk

        return JsonResponse(response, status=201)


class EditAnAdAPIView(generics.RetrieveAPIView):
    serializer_class = EditAnAdInfoSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ads.models.Ad.objects.select_related('city', 'category').all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class UpdateAdStatusAPIView(mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = ads.models.Ad.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UpdateAdStatusSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class AdDetailAPIView(generics.RetrieveAPIView):
    queryset = ads.models.Ad.objects.all()
    serializer_class = AdDetailSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            self.queryset = ads.models.FavoriteAd.is_favorite(self.queryset, self.request.user)

        return self.queryset

    def get_serializer_context(self):
        context = super(AdDetailAPIView, self).get_serializer_context()
        context['contact_detail'] = (
            ads.models.ContactDetail
            .objects
            .filter(
                ad=self.get_object()
            )
            .first()
        )
        return context

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class AdCommentAPIView(generics.CreateAPIView):
    queryset = ads.models.Comment.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AdCommentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoriesAPIView(generics.ListAPIView):
    queryset = ads.models.Category.objects.all()
    serializer_class = CategorySerializer


class RemoveFavoriteAdAPIView(generics.DestroyAPIView):
    queryset = ads.models.FavoriteAd.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AddRemoveFavoriteAdSerializer
    lookup_field = 'ad'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class AddFavoriteAdAPIView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AddRemoveFavoriteAdSerializer

    def perform_create(self, serializer):
        ad = self.get_object(serializer)
        serializer.save(user=self.request.user, ad=ad)

    @staticmethod
    def get_object(serializer):
        try:
            return ads.models.Ad.objects.get(pk=serializer.validated_data['ad_id'])
        except ads.models.FavoriteAd.DoesNotExist:
            raise Http404


class RePublishAdAPIView(generics.GenericAPIView):
    queryset = ads.models.Ad.objects.all()
    serializer_class = RePublishAdSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, ad_id):
        return self.queryset.filter(pk=ad_id, user=self.request.user).first()

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        ad = self.get_object(serializer.validated_data['ad_id'])

        if not ad:
            raise Http404

        ad.republish()

        return Response({'publish_date': ad.publish_date.strftime('%d.%m.%Y')})


class CurrencyAPIView(views.APIView):
    # noinspection PyMethodMayBeStatic, PyUnusedLocal
    def get(self, request):
        return Response({
            'kwd_to_usd': ads.utils.get_kwd_usd_rate(),
        })
