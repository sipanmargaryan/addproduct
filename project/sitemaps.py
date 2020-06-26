from django.apps import apps
from django.contrib import sitemaps
from django.db.models import Count
from django.urls import reverse

__all__ = (
    'StaticViewSitemap',
    'AdsViewSitemap',
    'AuthorsViewSitemap',
    'EventsViewSitemap',
    'PostsViewSitemap',
    'QuestionsViewSitemap',
)


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return [
            'ads:home', 'blog:news', 'events:upcoming_events',
            'common:about_us', 'common:contact_us', 'common:privacy_policy',
            'common:help_and_support', 'common:terms',
            'users:login', 'users:signup',
        ]

    def location(self, item):
        return reverse(item)


class AdsViewSitemap(sitemaps.Sitemap):
    priority = 0.8
    changefreq = 'hourly'

    def items(self):
        return apps.get_model('ads', 'Ad').objects.active()

    def location(self, item):
        return item.get_absolute_url()


class AuthorsViewSitemap(sitemaps.Sitemap):
    priority = 0.7
    changefreq = 'daily'

    def items(self):
        return apps.get_model('users', 'User').objects.annotate(ads=Count('ad')).filter(ads__gt=0)

    def location(self, item):
        return item.get_seller_url()


class EventsViewSitemap(sitemaps.Sitemap):
    priority = 0.7
    changefreq = 'daily'

    def items(self):
        return apps.get_model('events', 'Event').objects.all()

    def location(self, item):
        return item.get_absolute_url()


class PostsViewSitemap(sitemaps.Sitemap):
    priority = 0.7
    changefreq = 'daily'

    def items(self):
        return apps.get_model('blog', 'Article').objects.active()

    def location(self, item):
        return item.get_absolute_url()


class QuestionsViewSitemap(sitemaps.Sitemap):
    priority = 0.7
    changefreq = 'daily'

    def items(self):
        return apps.get_model('faq', 'Question').objects.all()

    def location(self, item):
        return item.get_absolute_url()
