from django.db.models import Count, F, Q
from django.views import generic

import blog.forms
import blog.models

__all__ = (
    'ArticleView',
    'ArticlesView',
    'LastArticlesView',
)


class ArticleView(generic.DetailView):
    model = blog.models.Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super(ArticleView, self).get_context_data(**kwargs)

        recent_posts = self.model.latest_news(5)
        if len(recent_posts) == 5:
            recent_posts = recent_posts[:4]
            context['recent_posts_show_more'] = True
        context['recent_posts'] = recent_posts

        context['comments'] = self.object.comments.select_related('user')

        return context

    def get(self, request, *args, **kwargs):
        # noinspection PyAttributeOutsideInit
        self.object = self.get_object()
        self.model.objects.filter(pk=self.object.pk).update(hit_count=F('hit_count') + 1)
        return super().get(request, *args, **kwargs)


class ArticlesView(generic.ListView):
    model = blog.models.Article
    template_name = 'blog/articles.html'
    paginate_by = 6
    context_object_name = 'articles'

    def get_context_data(self, **kwargs):
        context = super(ArticlesView, self).get_context_data(**kwargs)
        context['latest_news'] = self.model.latest_news(6).annotate(comment_count=Count('comments'))
        context['categories'] = blog.models.Category.objects.order_by('-name')
        return context

    def get_queryset(self):
        queryset = super(ArticlesView, self).get_queryset()

        search = self.request.GET.get('q')
        category = self.request.GET.get('category')
        sort_by = self.request.GET.get('sort_by', '-created')

        if category:
            queryset = queryset.filter(category__pk=category)
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))

        if sort_by in ['-created', '-views']:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('-created')

        return queryset.annotate(comment_count=Count('comments'))


class LastArticlesView(generic.ListView):
    model = blog.models.Article
    paginate_by = 4
    template_name = 'blog/includes/article_list.html'
    context_object_name = 'articles'
    ordering = ['-created']
