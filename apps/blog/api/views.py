from django_filters import rest_framework as filters
from rest_framework import generics, permissions, status
from rest_framework.response import Response

import blog.models
from blog.api.filters import ArticlesFilter

from .serializers import *  # noqa

__all__ = (
    'ArticlesAPIView',
    'ArticleDetailAPIView',
    'ReportAPIView',
    'NewCommentAPIView',
    'CategoriesAPIView',
)


class ArticlesAPIView(generics.ListAPIView):
    queryset = blog.models.Article.objects.active()
    serializer_class = ArticlesSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ArticlesFilter

    def get_queryset(self):
        return self.queryset.order_by('-created')


class ArticleDetailAPIView(generics.RetrieveAPIView):
    queryset = blog.models.Article.objects.active()
    serializer_class = ArticleDetailSerializer

    def get_queryset(self):
        return blog.models.Comment.attach_comment_count(self.queryset)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class ReportAPIView(generics.CreateAPIView):
    queryset = blog.models.Comment.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ReportSerializer

    def post(self, request, *args, **kwargs):
        self.get_object().reports.create(user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class NewCommentAPIView(generics.CreateAPIView):
    queryset = blog.models.Comment.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoriesAPIView(generics.ListAPIView):
    queryset = blog.models.Category.objects.all()
    serializer_class = CategorySerializer
