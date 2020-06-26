import pytest

from django.urls import reverse

import faq.factories
import faq.models


@pytest.mark.django_db
def test_questions(client):
    paginate_by = 4
    questions_count = 10

    faq.factories.QuestionFactory.create_batch(questions_count)

    response = client.get(reverse('faq:top_questions'))
    assert response.status_code == 200
    assert len(response.context['questions']) == paginate_by

    faq.factories.QuestionFactory(title='question', description='question description')

    payload = {'q': 'question'}

    response = client.get(reverse('faq:top_questions'), payload)

    assert response.status_code == 200
    assert len(response.context['questions']) == 1

    payload = {'page': 2}

    response = client.get(reverse('faq:top_questions'), payload)

    assert response.status_code == 200
    assert response.status_code == 200
    assert len(response.context['questions']) == paginate_by

    category = faq.factories.CategoryFactory()
    faq.factories.QuestionFactory.create_batch(questions_count, category=category)
    payload = {'category': [category.pk]}

    response = client.get(reverse('faq:top_questions'), payload)

    assert response.status_code == 200
    assert len(response.context['questions']) == paginate_by


@pytest.mark.django_db
def test_questions_invalid(client):
    payload = {'page': 404}

    response = client.get(reverse('faq:top_questions'), payload)

    assert response.status_code == 404


@pytest.mark.django_db
def test_question_detail_view(client):
    for category in faq.factories.CategoryFactory.create_batch(10):
        faq.factories.QuestionFactory(category=category)

    question = faq.factories.QuestionFactory(category=faq.factories.CategoryFactory())

    response = client.get(reverse('faq:question_detail', kwargs={'pk': question.pk, 'slug': question.slug}))

    assert response.status_code == 200
    assert response.context['question'] == question
    assert len(response.context['category_questions'])
    assert len(response.context['other_questions']) == 4
    assert all([question.pk != q.pk for q in response.context['other_questions']])


@pytest.mark.django_db
def test_question_answer(client):
    question = faq.factories.QuestionFactory()
    payload = {
        'author_full_name': 'John Doe',
        'author_email': 'email@example.com',
        'description': 'Description!',
    }
    response = client.post(
        reverse('faq:question_detail', kwargs={'pk': question.pk, 'slug': question.slug}), payload
    )

    assert response.status_code == 302
    assert response['location'] == question.get_absolute_url()
    assert question.answer_set.first().author_full_name == payload['author_full_name']


@pytest.mark.django_db
def test_ask_question(client):
    category = faq.factories.CategoryFactory()

    payload = {
        'title': 'FAQ question title example',
        'description': 'FAQ question description example',
        'author_full_name': 'Jane Doe',
        'author_email': 'email@example.com',
        'category': category.pk,
    }

    response = client.post(reverse('faq:ask_question'), payload)
    question = faq.models.Question.objects.first()

    assert response.status_code == 302
    assert response['location'] == reverse('faq:top_questions')
    assert question.title == payload['title']
    assert question.description == payload['description']
    assert question.author_full_name == payload['author_full_name']
    assert question.author_email == payload['author_email']
    assert question.category.pk == payload['category']


@pytest.mark.django_db
def test_ask_question_invalid(client):
    category = faq.factories.CategoryFactory()

    payload = {
        'title': 'FAQ question title example',
        'description': 'FAQ question description example',
        'author_full_name': 'Jane',
        'author_email': 'email@example.com',
        'category': category.id,
    }

    response = client.post(reverse('faq:ask_question'), payload)

    assert response.status_code == 200
    assert faq.models.Question.objects.count() == 0


@pytest.mark.django_db
def test_report_view(logged_in):
    answer = faq.factories.AnswerFactory()
    response = logged_in.client.post(reverse('faq:report', kwargs={'pk': answer.pk}))

    assert response.status_code == 204
