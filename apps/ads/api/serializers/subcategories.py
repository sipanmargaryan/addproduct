from rest_framework import serializers

import ads.models

__all__ = (
    'CarMakeCategorySerializer',
    'CarModelCategorySerializer',
    'MobileBrandCategorySerializer',
    'MobileModelCategorySerializer',
)


class CarMakeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ads.models.CarMakeCategory
        fields = ('pk', 'name', )


class CarModelCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ads.models.CarModelCategory
        fields = ('pk', 'name', )


class MobileBrandCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ads.models.MobileBrandCategory
        fields = ('pk', 'name', )


class MobileModelCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ads.models.MobileModelCategory
        fields = ('pk', 'name', )
