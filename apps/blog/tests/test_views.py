import pytest

from django.apps import apps
from django.db.models import Count
from django.urls import reverse

import blog.factories
import blog.models


@pytest.mark.django_db
def test_blog_article(client, image_file):
    blog.factories.ArticleFactory.create_batch(30)
    article = blog.factories.ArticleFactory(cover=image_file())

    response = client.get(reverse('blog:article_detail', kwargs={'pk': article.pk, 'slug': article.slug}))
    article.refresh_from_db()

    assert response.status_code == 200
    assert article.hit_count == 1
    assert len(response.context['recent_posts']) == 4


@pytest.mark.django_db
def test_article_list(client, image_file):
    paginate_by = 6
    article_count = 30

    blog.factories.ArticleFactory.create_batch(article_count, cover=image_file())

    response = client.get(reverse('blog:news'))
    assert response.status_code == 200
    assert len(response.context['articles']) == paginate_by
    assert len(response.context['latest_news']) == paginate_by

    blog.factories.ArticleFactory(title='blog article', description='blog article description', cover=image_file())

    payload = {'q': 'article'}

    response = client.get(reverse('blog:news'), payload)

    assert response.status_code == 200
    assert len(response.context['articles']) == 1


@pytest.mark.django_db
def test_article_list_category_filter(client, image_file):
    paginate_by = 6
    article_count = 30

    category = blog.factories.CategoryFactory()
    blog.factories.ArticleFactory.create_batch(article_count, category=category, cover=image_file())
    payload = {'category': category.pk}

    response = client.get(reverse('blog:news'), payload)

    assert response.status_code == 200
    articles = response.context['articles']
    assert len(articles) == paginate_by
    assert all([article.category.name == category.name for article in articles])


@pytest.mark.django_db
def test_like_dislike(logged_in):
    comment = blog.factories.CommentFactory()
    payload = {'comment_id': comment.pk, 'vote_type': blog.models.Vote.LIKE}
    response = logged_in.client.post(reverse('blog:like_dislike_comment'), payload)

    assert response.status_code == 200

    response = response.json()

    assert response['like_count'] == 1
    assert response['dislike_count'] == 0

    response = logged_in.client.post(reverse('blog:like_dislike_comment'), payload)

    assert response.status_code == 200

    response = response.json()

    assert response['like_count'] == 0
    assert response['dislike_count'] == 0


@pytest.mark.django_db
def test_last_articles(client, image_file):
    articles_count = 30

    blog.factories.ArticleFactory.create_batch(articles_count, cover=image_file())
    response = client.get(reverse('blog:last_articles'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert response.status_code == 200


@pytest.mark.django_db
def test_report(logged_in):
    comment = blog.factories.CommentFactory()
    response = logged_in.client.post(reverse('blog:report', kwargs={'pk': comment.pk}))

    assert response.status_code == 204
    assert apps.get_model('core', 'Report').objects.filter(
        content_type__model='comment', object_id=comment.pk
    ).count() == 1


@pytest.mark.django_db
def test_report_invalid(logged_in):
    response = logged_in.client.post(reverse('blog:report', kwargs={'pk': 1}))

    assert response.status_code == 404


@pytest.mark.django_db
def test_new_comment(logged_in, image_file):
    article = blog.factories.ArticleFactory(cover=image_file())
    payload = {'article_id': article.pk, 'description': 'test comment text'}

    response = logged_in.client.post(reverse('blog:new_comment'), payload)

    assert response.status_code == 302

    article.refresh_from_db()
    comments = blog.models.Article.objects.filter(pk=article.pk).annotate(c_count=Count('comments')).first()
    assert comments.c_count == 1

    comment = blog.factories.CommentFactory()
    payload['comment_id'] = comment.pk

    response = logged_in.client.post(reverse('blog:new_comment'), payload)

    assert response.status_code == 302

    article.refresh_from_db()
    comments = blog.models.Article.objects.filter(pk=article.pk).annotate(c_count=Count('comments')).first()

    assert comments.c_count == 2


@pytest.mark.django_db
def test_new_comment_invalid(logged_in, image_file):
    payload = {'article_id': 1}

    response = logged_in.client.post(reverse('blog:new_comment'), payload)

    assert response.status_code == 400

    payload = {'description': 'test comment text'}

    response = logged_in.client.post(reverse('blog:new_comment'), payload)

    assert response.status_code == 400

    article = blog.factories.ArticleFactory(cover=image_file())
    payload = {'article_id': article.pk}

    response = logged_in.client.post(reverse('blog:new_comment'), payload)

    assert response.status_code == 400
