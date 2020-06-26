from django import forms
from django.utils.functional import lazy

from ads.models import (
    Ad, CarAd, Category, Comment, ContactDetail, RealEstateAd
)
from core.models import City


class AdForm(forms.ModelForm):
    category = forms.ChoiceField(choices=lazy(Category.as_choices, tuple))
    city = forms.ChoiceField(choices=lazy(City.as_choices, tuple))
    is_seller_private = forms.ChoiceField(choices=Ad.SELLER_TYPES, initial=False)
    state = forms.ChoiceField(choices=Ad.STATES, initial=Ad.NEW_STATE)
    price = forms.IntegerField(min_value=1)

    class Meta:
        model = Ad
        fields = (
            'title', 'description', 'price',
            'currency', 'state', 'is_seller_private',
        )


class CarAdForm(forms.ModelForm):
    body_style = forms.ChoiceField(choices=CarAd.BODY_STYLES)

    class Meta:
        model = CarAd
        fields = ('mileage', 'year', 'body_style', )


class RealEstateAdForm(forms.ModelForm):
    estate_type = forms.ChoiceField(choices=RealEstateAd.ESTATE_TYPES)

    class Meta:
        model = RealEstateAd
        fields = ('bedrooms', 'bathrooms', 'estate_type', )


class ContactDetailForm(forms.ModelForm):
    class Meta:
        model = ContactDetail
        fields = ('email', 'phone_number', 'full_name')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('description', 'ad')
