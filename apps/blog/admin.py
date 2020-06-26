from django.contrib import admin

import blog.models


class ArticleAdmin(admin.ModelAdmin):
    fields = ('title', 'description', 'status', 'category', 'cover')


admin.site.register(blog.models.Category)
admin.site.register(blog.models.Comment)
admin.site.register(blog.models.Article, ArticleAdmin)
