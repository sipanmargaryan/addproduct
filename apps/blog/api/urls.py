from django.urls import path

from .views import *  # noqa

app_name = 'blog_api'
urlpatterns = [
    path('news/', ArticlesAPIView.as_view(), name='news'),
    path('news/<int:pk>/', ArticleDetailAPIView.as_view(), name='article_detail'),
    path('report/<int:pk>/', ReportAPIView.as_view(), name='report'),
    path('new-comment/', NewCommentAPIView.as_view(), name='new_comment'),
    path('categories/', CategoriesAPIView.as_view(), name='category'),
]
