from django.urls import path

from .views import *  # noqa

app_name = 'ads'
urlpatterns = [
    path('', HomeAdsView.as_view(), name='home'),
    path('ads', AdsView.as_view(), name='ads'),
    path('ad/<int:pk>/<str:slug>/', AdDetailView.as_view(), name='ad_detail'),
    path('my/', MyAdsView.as_view(), name='my'),
    path('favorites/', FavoriteAdsView.as_view(), name='favorites'),
    path('add-remove-favorite/', AddRemoveFavorite.as_view(), name='add_remove_favorite'),
    path('republish/', RePublishAdView.as_view(), name='republish'),
    path('delete/', DeleteAdView.as_view(), name='delete'),
    path('toggle-status/', ToggleAdStatusView.as_view(), name='toggle_status'),
    path('add-an-ad/', AddAnAdView.as_view(), name='add'),
    path('edit-ad/<int:pk>/', EditAnAdView.as_view(), name='edit'),
    path('seller/<int:user>/', SellerView.as_view(), name='seller'),
    path('add-comment/', AddCommentView.as_view(), name='add_comment'),
    path('car-models/', CarModelView.as_view(), name='car_models'),
    path('mobile-models/', MobileModelView.as_view(), name='mobile_models'),
    path('save-search/', SaveSearchView.as_view(), name='save_search'),
]
