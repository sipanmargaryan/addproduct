from rest_framework import serializers

from django.core.files import storage
from django.db.models import Avg
from django.utils import timezone

import ads.models
import core.models
from ads.mixins import RelatedDataMixin
from core.api.serializers import CitySerializer
from users.api.serializers import UserProfileSerializer

__all__ = (
    'CategorySerializer',
    'AdImageSerializer',
    'AdSerializer',
    'UpdateAdStatusSerializer',
    'AdAnAddInfoSerializer',
    'AdDetailSerializer',
    'AdCommentSerializer',
    'AddRemoveFavoriteAdSerializer',
    'AdCreateSerializer',
    'AdContactSerializer',
    'RePublishAdSerializer',
    'EditAnAdInfoSerializer',
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ads.models.Category
        fields = (
            'pk',
            'name',
        )


class AdImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ads.models.AdImage
        fields = (
            'image',
            'is_primary',
        )


class AdSerializer(serializers.ModelSerializer):
    city = CitySerializer()
    category = CategorySerializer()
    user = UserProfileSerializer()
    primary_image = serializers.SerializerMethodField()
    is_favorite = serializers.BooleanField(default=False)

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
            'is_favorite',
        )

    @staticmethod
    def get_primary_image(ad):
        return storage.default_storage.url(ad.primary_image)


class UpdateAdStatusSerializer(serializers.ModelSerializer):
    status = serializers.IntegerField(write_only=True)

    class Meta:
        model = ads.models.Ad
        fields = ('status', )


# noinspection PyAbstractClass
class AdAnAddInfoSerializer(serializers.Serializer):
    categories = serializers.SerializerMethodField(read_only=True)
    is_seller_private = ads.models.Ad.SELLER_TYPES

    class Meta:
        fields = ('categories', 'is_seller_private')

    @staticmethod
    def get_categories():
        return ads.models.Category.objects.all('pk', 'name')


class AdDetailSerializer(serializers.ModelSerializer):
    city = CitySerializer()
    category = CategorySerializer()
    user = UserProfileSerializer()
    comments = serializers.SerializerMethodField()
    review = serializers.SerializerMethodField()
    recommended = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    is_favorite = serializers.BooleanField(default=False)

    class Meta:
        model = ads.models.Ad
        fields = (
            'pk',
            'title',
            'description',
            'state',
            'views',
            'is_seller_private',
            'publish_date',
            'price',
            'currency',
            'user',
            'category',
            'city',
            'adimage_set',
            'comments',
            'review',
            'recommended',
            'is_favorite',
            'phone_number',
        )
        depth = 1

    def get_phone_number(self, ad):
        phone = ''
        if self.context['contact_detail']:
            phone = self.context['contact_detail'].phone_number_clean
        elif ad.external_phone_number:
            phone = ad.external_phone_number_clean
        return f'+965{phone}' if phone and len(phone) == 8 else phone

    def get_comments(self, ad):
        queryset = ads.models.Comment.objects.filter(ad=ad.pk)\
            .values(
                'pk',
                'description',
                'created',
                'user__first_name',
                'user__last_name',
                'user__avatar'
        ).order_by('-created')

        return self.change_image(queryset, 'user__avatar')

    @staticmethod
    def get_review(ad):
        queryset = ads.models.AdReview.objects.filter(ad=ad.pk)
        return dict(
            count=queryset.count(),
            average=queryset.aggregate(avg=Avg('rating'))['avg'],
        )

    def get_recommended(self, ad):
        user = self.context['request'].user
        queryset = ads.models.AdImage.primary_image(
            ads.models.Ad.objects.active()
            .exclude(pk=ad.pk)
            .order_by('-publish_date')
        )

        if user.is_authenticated:
            queryset = ads.models.FavoriteAd.is_favorite(queryset, user)

        top_ad_list = list(queryset.filter(premium_until__gte=timezone.now()).order_by('?')[:6])

        if len(top_ad_list) < 6:
            top_ad_list.extend(
                queryset
                .exclude(pk__in=[ad.pk for ad in top_ad_list])
                .order_by('-publish_date')
                [:6 - len(top_ad_list)]
            )

        top_ad_list = [dict(
            pk=ad.pk,
            description=ad.description,
            price=ad.price,
            currency=ad.currency,
            title=ad.title,
            primary_image=ad.primary_image,
        ) for ad in top_ad_list]

        return self.change_image(top_ad_list, 'primary_image')

    @staticmethod
    def change_image(data, field):
        new_data = []
        for ad in data:
            if ad[field]:
                ad[field] = storage.default_storage.url(ad[field])
            new_data.append(ad)
        return new_data


class AdCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = ads.models.Comment
        fields = ('description', 'ad')


class AddRemoveFavoriteAdSerializer(serializers.ModelSerializer):
    ad_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ads.models.FavoriteAd
        fields = ('ad_id', )


class AdCreateSerializer(serializers.ModelSerializer):
    # category = serializers.ChoiceField(choices=ads.models.Category.as_choices())
    # city = serializers.ChoiceField(choices=core.models.City.as_choices())
    is_seller_private = serializers.ChoiceField(choices=ads.models.Ad.SELLER_TYPES, initial=False)
    state = serializers.ChoiceField(choices=ads.models.Ad.STATES, initial=ads.models.Ad.NEW_STATE)
    price = serializers.IntegerField(min_value=1)

    class Meta:
        model = ads.models.Ad
        fields = (
            'title', 'description', 'price',  # 'category', 'city',
            'currency', 'state', 'is_seller_private',
        )


class AdContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ads.models.ContactDetail
        fields = ('email', 'phone_number', 'full_name')


class RePublishAdSerializer(serializers.ModelSerializer):
    ad_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ads.models.Ad
        fields = ('ad_id',)


class EditAnAdInfoSerializer(RelatedDataMixin, serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    related_data = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = ads.models.Ad
        fields = (
            'pk',
            'title',
            'description',
            'price',
            'currency',
            'is_seller_private',
            'state',
            'city',
            'category',
            'category_name',
            'images',
            'email',
            'phone_number',
            'full_name',
            'related_data',
        )

    @staticmethod
    def get_email(ad):
        return ad.contactdetail_set.first().email

    @staticmethod
    def get_full_name(ad):
        return ad.contactdetail_set.first().full_name

    @staticmethod
    def get_phone_number(ad):
        return ad.contactdetail_set.first().phone_number

    @staticmethod
    def get_images(ad):
        return [
            {'image': storage.default_storage.url(image['image']), 'pk': image['pk']}
            for image in ads.models.AdImage.objects.filter(ad=ad.pk).values('pk', 'image')
        ]

    @staticmethod
    def get_category_name(ad):
        return ad.category.name
