from django_filters import rest_framework as filters
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response

from django.http import Http404
from django.utils import timezone

import ads.models
import users.models
from ads.api.filters import MyAdsFilter
from ads.filters import AdFilter
from ads.views import MyAdsView
from users.api.serializers import UserProfileSerializer

from ..serializers import *  # noqa

__all__ = (
    'MyAdsAPIView',
    'FavoriteAdsAPIView',
    'DeleteFavoriteAdsAPIView',
    'SellerAPIView',
    'AdsAPIView',
    'FeaturedAdsAPIView',
)


class MyAdsAPIView(generics.ListAPIView):
    queryset = ads.models.Ad.objects.all()
    serializer_class = MyAdsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = MyAdsFilter

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        queryset = ads.models.AdImage.primary_image(queryset)
        queryset = MyAdsView.count_messages(queryset)
        if self.request.user.is_authenticated:
            queryset = ads.models.FavoriteAd.is_favorite(queryset, self.request.user)
        return queryset.order_by('-publish_date')


class FavoriteAdsAPIView(generics.ListAPIView):
    queryset = ads.models.FavoriteAd.objects.all()
    serializer_class = FavoriteAdsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = ads.models.FavoriteAd.objects.filter(user=self.request.user).select_related('ad')
        return ads.models.AdImage.primary_image(queryset, outer_ref='ad__pk')


class DeleteFavoriteAdsAPIView(views.APIView):

    def delete(self, request):
        ads.models.FavoriteAd.objects.filter(user=self.request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SellerAPIView(views.APIView):
    queryset = ads.models.Ad.objects.active()
    serializer_class = SellerAdSerializer

    def get_object(self, user):
        try:
            return users.models.User.objects.get(pk=user)
        except users.models.User.DoesNotExist:
            raise Http404

    def get_queryset(self, user):
        queryset = self.queryset.filter(user=user)
        queryset = ads.models.AdImage.primary_image(queryset)
        if self.request.user.is_authenticated:
            queryset = ads.models.FavoriteAd.is_favorite(queryset, self.request.user)
        return queryset.order_by('-publish_date')

    def get(self, request, user):
        serializer = self.serializer_class(self.get_queryset(user), many=True)
        user = UserProfileSerializer(self.get_object(user))
        return Response({
            'ads': serializer.data,
            'user': user.data,
        })


class AdsAPIView(generics.ListAPIView):
    queryset = ads.models.Ad.objects.active()
    serializer_class = AdSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AdFilter

    def get_queryset(self):
        queryset = ads.models.AdImage.primary_image(self.queryset)

        if self.request.user.is_authenticated:
            queryset = ads.models.FavoriteAd.is_favorite(queryset, self.request.user)

        return queryset.order_by('-publish_date')


class FeaturedAdsAPIView(generics.ListAPIView):
    queryset = ads.models.Ad.objects.active()
    serializer_class = AdSerializer

    def get_queryset(self):
        queryset = ads.models.AdImage.primary_image(self.queryset.order_by('-publish_date'))

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
