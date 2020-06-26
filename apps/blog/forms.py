from django import forms
from django.utils.functional import lazy

import blog.models

__all__ = (
    'CommentForm',
)


class CommentForm(forms.ModelForm):
    article_id = forms.ChoiceField(choices=lazy(blog.models.Article.as_choices, tuple))
    comment_id = forms.IntegerField(required=False)

    class Meta:
        model = blog.models.Comment
        fields = ('description', )
