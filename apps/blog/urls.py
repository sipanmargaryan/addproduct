from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('news/', views.ArticlesView.as_view(), name='news'),
    path('news/<int:pk>/<str:slug>/', views.ArticleView.as_view(), name='article_detail'),
    path('like-dislike-comment/', views.VoteCommentView.as_view(), name='like_dislike_comment'),
    path('last-articles/', views.LastArticlesView.as_view(), name='last_articles'),
    path('report/<int:pk>/', views.ReportView.as_view(), name='report'),
    path('new-comment/', views.NewComment.as_view(), name='new_comment'),
]
