from rest_framework_swagger.views import get_swagger_view

from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from .sitemaps import *  # noqa

schema_view = get_swagger_view(title=f'{settings.CLIENT_DOMAIN} API')

sitemaps = {
    'static': StaticViewSitemap,
    'ads': AdsViewSitemap,
    'authors': AuthorsViewSitemap,
    'events': EventsViewSitemap,
    'faq': QuestionsViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ads.urls', namespace='ads')),
    path('', include('common.urls', namespace='common')),
    path('', include('events.urls', namespace='events')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('accounts/', include('users.urls', namespace='users')),
    path('messaging/', include('messaging.urls', namespace='messaging')),
    path('faq/', include('faq.urls', namespace='faq')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
]

api_apps = [
    'users',
    'ads',
    'payments',
    'messaging',
    'events',
    'faq',
    'blog',
    'common',
]

urlpatterns += [
    path(f'api/v{settings.API_VERSION}/{app}/', include(f'{app}.api.urls', namespace=f'{app}_api')) for app in api_apps
]

admin.site.site_header = settings.CLIENT_DOMAIN
admin.site.site_title = settings.CLIENT_DOMAIN

if settings.ENABLE_DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

if settings.DEBUG:
    urlpatterns += [
        path('api-docs/', schema_view)
    ]
