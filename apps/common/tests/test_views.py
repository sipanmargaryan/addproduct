import pytest

from django.urls import reverse

from common.factories import ArticleFactory, ServiceFactory
from events.factories import EventFactory
from faq.factories import QuestionFactory


def test_contact_us(client, mailoutbox, settings):

    payload = {
        'email': 'email@example.com',
        'name': 'John Doe',
        'message': 'contact us message',
    }

    response = client.post(reverse('common:contact_us'), payload)

    assert response.status_code == 302

    assert len(mailoutbox) == 1
    message = mailoutbox[0]
    assert message.to == [settings.ADMIN_EMAIL]


@pytest.mark.django_db
def test_help_and_support(client):
    ArticleFactory.create_batch(10)

    response = client.get(reverse('common:help_and_support'))
    assert response.status_code == 200
    assert len(response.context['articles']) == 10

    ArticleFactory(title='article', description='article description')

    payload = {
        'q': 'article'
    }

    response = client.get(reverse('common:help_and_support'), payload)

    assert response.status_code == 200
    assert len(response.context['articles']) == 1


@pytest.mark.django_db
def test_services(client, image_file):
    ServiceFactory.create_batch(10, cover=image_file())

    response = client.get(reverse('common:services'))
    assert response.status_code == 200
    assert len(response.context['services']) == 10


@pytest.mark.django_db
def test_living_in_kuwait(client, image_file):
    ServiceFactory.create_batch(10, cover=image_file())
    EventFactory.create_batch(10, image=image_file())
    QuestionFactory.create_batch(10)

    response = client.get(reverse('common:living_in_armenia'))

    assert response.status_code == 200

    assert len(response.context['services']) == 6
    assert len(response.context['questions']) == 5
    assert len(response.context['events']) == 5
