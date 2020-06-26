from rest_framework import serializers

import blog.models

__all__ = (
    'CategorySerializer',
    'ArticlesSerializer',
    'ArticleDetailSerializer',
    'ReportSerializer',
    'CommentSerializer',
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = blog.models.Category
        fields = ('pk', 'name')


class ArticlesSerializer(serializers.ModelSerializer):
    class Meta:
        model = blog.models.Article
        fields = (
            'pk',
            'title',
            'cover',
            'created',
        )


class ArticleDetailSerializer(serializers.ModelSerializer):
    comment_count = serializers.IntegerField()
    category = CategorySerializer()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = blog.models.Article
        fields = (
            'pk',
            'title',
            'description',
            'cover',
            'hit_count',
            'category',
            'created',
            'comments',
            'comment_count',
        )

    @staticmethod
    def get_comments(article):
        queryset = blog.models.Comment.objects.filter(article=article.pk)
        return queryset.values('pk', 'description', 'created', 'user__first_name', 'user__last_name', 'parent')


class ReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = blog.models.Comment
        fields = ('reports', )


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = blog.models.Comment
        fields = (
            'article',
            'parent',
            'description',
        )
