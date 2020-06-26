import math

import pytest

from django.apps import apps
from django.urls import reverse
from django.utils import timezone

from ads.factories import (
    AdFactory, AdImageFactory, AdReviewFactory, CategoryFactory,
    FavoriteAdFactory
)
from core.factories import CityFactory
from events.factories import EventFactory
from messaging.factories import MessageFactory, ThreadFactory
from users.factories import UserFactory


@pytest.mark.django_db
def test_favorite_ads(logged_in):
    ads = AdFactory.create_batch(20)

    user = logged_in.user

    for ad in ads[:15]:
        FavoriteAdFactory(ad=ad, user=user)

    response = logged_in.client.get(reverse('ads:favorites'))

    assert response.status_code == 200
    assert len(response.context['favorites']) == 10
    assert len([favorite for favorite in response.context['favorites'] if favorite.user == user]) == 10

    response = logged_in.client.get(f'{reverse("ads:favorites")}?page=2')

    assert response.status_code == 200
    assert len(response.context['favorites']) == 5
    assert len([favorite for favorite in response.context['favorites'] if favorite.user == user]) == 5

    response = logged_in.client.get(f'{reverse("ads:favorites")}?page=99')

    assert response.status_code == 404


@pytest.mark.django_db
def test_add_remove_favorite_ad(logged_in):
    ad = AdFactory()

    user = logged_in.user

    response = logged_in.client.post(reverse('ads:add_remove_favorite'), {'ad_id': ad.pk})

    assert response.status_code == 200
    assert apps.get_model('ads', 'FavoriteAd').objects.filter(user=user, ad=ad).count() == 1

    response = logged_in.client.post(reverse('ads:add_remove_favorite'), {'ad_id': ad.pk})

    assert response.status_code == 200
    assert apps.get_model('ads', 'FavoriteAd').objects.filter(user=user, ad=ad).count() == 0

    response = logged_in.client.post(reverse('ads:add_remove_favorite'), {'ad_id': 99})

    assert response.status_code == 404


@pytest.mark.django_db
def test_my_ads_all(logged_in, image_file):
    def extract_name(url):
        if not url:
            return
        return url.split('/')[-1].split('.')[0]

    user = logged_in.user

    AdFactory.create_batch(10)

    ad = AdFactory.create(user=user, status=1)
    ad_image = AdImageFactory(ad=ad, is_primary=True)
    ad_image.image.save('image.png', image_file())
    AdImageFactory.create_batch(10, ad=ad, is_primary=False)

    active_ads = [ad.pk for ad in AdFactory.create_batch(4, user=user, status=1)]
    active_ads.append(ad.pk)
    inactive_ads = [ad.pk for ad in AdFactory.create_batch(5, user=user, status=0)]

    response = logged_in.client.get(reverse('ads:my'))

    assert response.status_code == 200
    assert len(response.context['ads']) == 10
    assert all([ad.pk in active_ads or ad.pk in inactive_ads for ad in response.context['ads']])
    assert any([extract_name(ad.primary_image) == extract_name(ad_image.image.url) for ad in response.context['ads']])


@pytest.mark.django_db
def test_my_ads_active(logged_in):
    user = logged_in.user

    # Add random and inactive ads
    AdFactory.create_batch(10)
    AdFactory.create_batch(5, user=user, status=0)

    active_ads = [ad.pk for ad in AdFactory.create_batch(5, user=user, status=1)]
    response = logged_in.client.get('{}?filter_by=active'.format(reverse('ads:my')))

    assert response.status_code == 200
    assert len(response.context['ads']) == 5
    assert all([ad.pk in active_ads for ad in response.context['ads']])


@pytest.mark.django_db
def test_my_ads_inactive(logged_in):
    user = logged_in.user

    # Add random and active ads
    AdFactory.create_batch(10)
    AdFactory.create_batch(5, user=user, status=1)

    AdFactory.create_batch(5, user=user, status=1)
    inactive_ads = [ad.pk for ad in AdFactory.create_batch(5, user=user, status=0)]
    response = logged_in.client.get('{}?filter_by=inactive'.format(reverse('ads:my')))

    assert response.status_code == 200
    assert len(response.context['ads']) == 5
    assert all([ad.pk in inactive_ads for ad in response.context['ads']])


@pytest.mark.django_db
def test_my_ads_message_count(logged_in):
    user = logged_in.user

    ad = AdFactory(user=user)
    thread1 = ThreadFactory(ad=ad)
    thread2 = ThreadFactory(ad=ad)
    MessageFactory.create_batch(10, thread=thread1)
    MessageFactory.create_batch(5, thread=thread2)

    response = logged_in.client.get(reverse('ads:my'))

    assert response.status_code == 200
    assert len(response.context['ads']) == 1
    assert response.context['ads'][0].message_count == 15


@pytest.mark.django_db
def test_ad_details(client, image_file):
    ad = AdFactory(title='title', views=0)
    images = AdImageFactory.create_batch(10, ad=ad, image=image_file())

    response = client.get(ad.get_absolute_url())
    ad.refresh_from_db()

    assert response.status_code == 200
    assert response.context['ad'].pk == ad.pk
    assert ad.views == 1
    assert [adi.image.url for adi in response.context['ad'].images] == [adi.image.url for adi in images]


@pytest.mark.django_db
def test_ad_details_authenticated(logged_in):
    user = logged_in.user
    ad = AdFactory(title='title', views=0)

    response = logged_in.client.get(ad.get_absolute_url())

    assert response.status_code == 200
    assert response.context['ad'].pk == ad.pk
    assert not response.context['ad'].is_favorite

    FavoriteAdFactory(ad=ad, user=user)

    response = logged_in.client.get(ad.get_absolute_url())
    ad.refresh_from_db()

    assert response.status_code == 200
    assert ad.views == 2
    assert response.context['ad'].is_favorite


@pytest.mark.django_db
def test_ad_details_redirect(client):
    ad = AdFactory(title='title')

    response = client.get(reverse('ads:ad_detail', kwargs={'pk': ad.pk, 'slug': 'invalid'}))

    assert response.status_code == 301
    assert response['location'] == ad.get_absolute_url()


@pytest.mark.django_db
def test_ad_delete(logged_in):
    ad = AdFactory(title='title', user=logged_in.user)
    payload = {'ad_id': ad.pk}
    response = logged_in.client.post(reverse('ads:delete'), payload)

    assert response.status_code == 204
    assert apps.get_model('ads', 'Ad').objects.filter(user=logged_in.user).count() == 0


@pytest.mark.django_db
def test_ad_republish(logged_in):
    publish_date = timezone.now() - timezone.timedelta(days=7)
    ad = AdFactory(title='title', user=logged_in.user, publish_date=publish_date)
    payload = {'ad_id': ad.pk}
    response = logged_in.client.post(reverse('ads:republish'), payload)

    assert response.status_code == 200
    assert response.json()['publish_date'] == timezone.now().strftime('%d.%m.%Y')


@pytest.mark.django_db
def test_ad_republish_invalid(logged_in):
    publish_date = timezone.now() - timezone.timedelta(days=5)
    ad = AdFactory(title='title', user=logged_in.user, publish_date=publish_date)
    payload = {'ad_id': ad.pk}
    response = logged_in.client.post(reverse('ads:republish'), payload)

    assert response.status_code == 200
    assert response.json()['publish_date'] == publish_date.strftime('%d.%m.%Y')


@pytest.mark.django_db
def test_ad_toggle_status(logged_in):
    ad = AdFactory(title='title', user=logged_in.user, status=1)
    payload = {'ad_id': ad.pk}
    response = logged_in.client.post(reverse('ads:toggle_status'), payload)
    ad.refresh_from_db()

    assert response.status_code == 200
    assert response.json()['is_active'] is False
    assert bool(ad.status) is False

    response = logged_in.client.post(reverse('ads:toggle_status'), payload)
    ad.refresh_from_db()

    assert response.status_code == 200
    assert response.json()['is_active']
    assert bool(ad.status)


@pytest.mark.django_db
def test_ad_add_view(logged_in):
    user = logged_in.user
    user.first_name = 'John'
    user.last_name = 'Doe'
    user.save()

    initial = {
        'full_name': user.get_full_name(),
        'email': user.email,
        'phone_number': user.phone_number,
    }

    response = logged_in.client.get(reverse('ads:add'))

    assert response.status_code == 200
    assert response.context['form'] is not None
    assert set(response.context['contact_form'].initial.values()) == set(initial.values())


@pytest.mark.django_db
def test_ad_add_save(logged_in, image_file):
    category = CategoryFactory()
    city = CityFactory()

    payload = {
        'category': category.pk,
        'city': city.pk,
        'title': 'Spam',
        'description': 'Egg',
        'price': 256,
        'currency': 'kwd',
        'state': 'used',
        'is_seller_private': 'False',
        'full_name': 'John Doe',
        'email': 'email@example.com',
        'phone_number': '12345678',
        'image-1': image_file(),
        'image-2': image_file(),
        'premium_days': 7,
    }

    response = logged_in.client.post(reverse('ads:add'), payload)
    ad = apps.get_model('ads', 'Ad').objects.first()
    contact_detail = apps.get_model('ads', 'ContactDetail').objects.first()
    payment = apps.get_model('payments', 'Payment').objects.filter(ad=ad).first()

    payload['is_seller_private'] = False
    payload['category'] = category
    payload['city'] = city

    assert response.status_code == 201
    assert response.json()['next_url'] == payment.get_absolute_url()

    assert all([v == getattr(ad, k) for k, v in payload.items() if hasattr(ad, k)])
    assert all([v == getattr(contact_detail, k) for k, v in payload.items() if hasattr(contact_detail, k)])
    assert apps.get_model('ads', 'AdImage').objects.filter(ad=ad.pk).count() == 2


@pytest.mark.django_db
def test_ad_add_save_invalid(logged_in):

    response = logged_in.client.post(reverse('ads:add'))

    assert response.status_code == 400

    category = CategoryFactory()
    city = CityFactory()

    payload = {
        'category': category.pk,
        'city': city.pk,
        'title': 'Spam',
        'description': 'Egg',
        'price': 256,
        'currency': 'kwd',
        'state': 'used',
        'is_seller_private': 'False',
        'full_name': 'John Doe',
        'email': 'email@example.com',
        'phone_number': '12345678',
    }

    response = logged_in.client.post(reverse('ads:add'), payload)

    assert response.status_code == 204


@pytest.mark.django_db
def test_homepage(client, image_file):
    ads = AdFactory.create_batch(10, premium_until=timezone.now() + timezone.timedelta(days=1))
    for ad in ads:
        AdImageFactory(
            ad=ad, image=image_file(), is_primary=True
        )

    EventFactory.create_batch(
        10, start_date=timezone.now() + timezone.timedelta(days=2),
        image=image_file(),
    )

    response = client.get(reverse('ads:home'))

    assert response.status_code == 200
    assert len(response.context['ads']) == 6
    assert response.context['ads'][0].primary_image
    assert len(response.context['events']) == 10


@pytest.mark.django_db
def test_homepage_is_favorite(logged_in, image_file):
    ads = AdFactory.create_batch(10)
    for ad in ads:
        AdImageFactory(ad=ad, image=image_file(), is_primary=True)
        if ad.pk % 2 == 0:
            FavoriteAdFactory(ad=ad, user=logged_in.user)

    EventFactory.create_batch(
        10, start_date=timezone.now() + timezone.timedelta(days=2),
        image=image_file(),
    )

    response = logged_in.client.get(reverse('ads:home'))

    assert response.status_code == 200
    assert all([ad.is_favorite for ad in response.context['ads'] if ad.pk % 2 == 0])


@pytest.mark.django_db
def test_ads(client):
    paginate_by = 9
    price_max = 200
    price_min = 10

    category = CategoryFactory()
    AdFactory.create_batch(30, category=category, price=price_min)
    AdFactory(price=price_max, is_seller_private=True)

    response = client.get(reverse('ads:ads'))

    assert response.status_code == 200
    assert len(response.context['ads']) == paginate_by
    assert response.context['ads_count'] == 31
    assert response.context['filter_form']
    assert response.context['ads_data']['price__max'] == price_max
    assert response.context['ads_data']['price__min'] == price_min
    assert response.context['categories_ads'][0]['count'] == 30
    assert response.context['is_paginated']
    assert response.context['page_obj'].paginator.num_pages == math.ceil(31 / paginate_by)

    payload = {
        'category': category.pk,
        'price_min': price_max,
        'seller_type': 'private',
    }

    response = client.get(reverse('ads:ads'), payload)
    assert response.status_code == 200
    assert response.context['page_obj'].paginator.num_pages == 1
    assert not response.context['is_paginated']
    assert all([ad.is_seller_private for ad in response.context['ads']])


@pytest.mark.django_db
def test_seller_view(client):
    user = UserFactory()
    AdFactory.create_batch(24, user=user)
    AdFactory.create_batch(24)

    response = client.get(reverse('ads:seller', kwargs={'user': user.pk}))

    assert response.status_code == 200
    assert len(response.context['ads']) == 12
    assert all([ad.user == user for ad in response.context['ads']])


@pytest.mark.django_db
def test_ad_detail_view(client, image_file):
    user = UserFactory()
    ad = AdFactory(user=user, title='Ad')
    AdImageFactory(ad=ad, is_primary=True, image=image_file())
    AdImageFactory.create_batch(4, ad=ad, is_primary=False, image=image_file())
    AdReviewFactory(ad=ad, rating=4, user=UserFactory())
    AdReviewFactory(ad=ad, rating=5, user=UserFactory())
    AdReviewFactory(ad=ad, rating=1, user=UserFactory())

    response = client.get(reverse('ads:ad_detail', kwargs={'pk': ad.pk, 'slug': ad.slug}))
    ad.refresh_from_db()

    assert response.status_code == 200
    assert response.context['ad'].title == ad.title
    assert response.context['review_metrics']['count'] == 3
    assert int(response.context['review_metrics']['average']) == 3
    assert ad.views == 1


@pytest.mark.django_db
def test_add_comment_view(logged_in):
    ad = AdFactory()
    payload = {
        'ad': ad.pk,
        'description': 'Comment',
    }
    response = logged_in.client.post(reverse('ads:add_comment'), payload)

    assert response.status_code == 302
    assert response['location'] == ad.get_absolute_url()
