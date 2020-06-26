import pytest

from django.utils import timezone

from ads.factories import AdFactory


@pytest.mark.django_db
def test_ad_is_able_to_publish():
    ad = AdFactory()

    assert ad.is_able_to_republish is False

    ad.publish_date = timezone.now() - timezone.timedelta(days=7)

    assert ad.is_able_to_republish

    ad.republish()
    ad.refresh_from_db()

    assert ad.is_able_to_republish is False
    assert ad.publish_date.date() == timezone.now().date()
