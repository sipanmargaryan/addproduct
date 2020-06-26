from django.urls import path

from .views import ad_detail, ad_list, subcategories

app_name = 'ads_api'
urlpatterns = [
    path('add-an-ad/', ad_detail.AddAnAdAPIView.as_view(), name='add'),
    path('edit-an-ad/<int:pk>/', ad_detail.EditAnAdAPIView.as_view(), name='edit'),
    path('delete-ad/<int:pk>/', ad_detail.AdDestroyView.as_view(), name='delete'),
    path('my/', ad_list.MyAdsAPIView.as_view(), name='my'),
    path('favorites/', ad_list.FavoriteAdsAPIView.as_view(), name='favorites'),
    path('delete-favorites/', ad_list.DeleteFavoriteAdsAPIView.as_view(), name='delete_favorites'),
    path('seller/<int:user>/', ad_list.SellerAPIView.as_view(), name='seller'),
    path('update-status/<int:pk>/', ad_detail.UpdateAdStatusAPIView.as_view(), name='update_status'),
    path('ad/<int:pk>/', ad_detail.AdDetailAPIView.as_view(), name='ad_detail'),
    path('ad-comment/', ad_detail.AdCommentAPIView.as_view(), name='ad_comment'),
    path('ads/', ad_list.AdsAPIView.as_view(), name='ads'),
    path('categories/', ad_detail.CategoriesAPIView.as_view(), name='category'),
    path('delete-favorite/<int:ad>/', ad_detail.RemoveFavoriteAdAPIView.as_view(), name='delete_favorite'),
    path('add-favorite/', ad_detail.AddFavoriteAdAPIView.as_view(), name='add_favorite'),
    path('subcategories/cars/makes/', subcategories.CarMakesAPIView.as_view(), name='car_makes'),
    path('subcategories/cars/makes/<int:pk>/models/', subcategories.CarModelsAPIView.as_view(), name='car_models'),
    path('subcategories/mobile/brands/', subcategories.MobileBrandsAPIView.as_view(), name='mobile_brands'),
    path(
        'subcategories/mobile/brands/<int:pk>/models/',
        subcategories.MobileModelsAPIView.as_view(),
        name='mobile_models',
    ),
    path('republish/', ad_detail.RePublishAdAPIView.as_view(), name='republish'),
    path('currency/', ad_detail.CurrencyAPIView.as_view(), name='currency'),
    path('featured-ads/', ad_list.FeaturedAdsAPIView.as_view(), name='featured_ads'),
]
