from rest_framework import serializers

from django.core.files import storage

import ads.models

from .ad_detail import AdSerializer

__all__ = (
    'MyAdsSerializer',
    'FavoriteAdsSerializer',
    'SellerAdSerializer',
)


class MyAdsSerializer(AdSerializer, serializers.ModelSerializer):
    message_count = serializers.CharField()
    is_favorite = serializers.BooleanField()

    class Meta:
        model = ads.models.Ad
        fields = (
            'pk',
            'title',
            'slug',
            'description',
            'state',
            'views',
            'is_seller_private',
            'publish_date',
            'premium_until',
            'price',
            'currency',
            'user',
            'category',
            'city',
            'primary_image',
            'message_count',
            'is_favorite',
        )


class FavoriteAdsSerializer(serializers.ModelSerializer):
    ad = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ads.models.FavoriteAd
        fields = (
            'ad',
        )

    @staticmethod
    def get_ad(ad):
        return {
            'pk': ad.ad.pk,
            'price': ad.ad.price,
            'title': ad.ad.title,
            'currency': ad.ad.currency,
            'primary_image': storage.default_storage.url(ad.primary_image),
        }


class SellerAdSerializer(serializers.ModelSerializer):
    primary_image = serializers.SerializerMethodField()
    is_favorite = serializers.BooleanField(default=False)

    class Meta:
        model = ads.models.Ad
        fields = (
            'pk',
            'title',
            'price',
            'currency',
            'primary_image',
            'is_favorite',
        )

    @staticmethod
    def get_primary_image(ad):
        return storage.default_storage.url(ad.primary_image)
