from django import forms
from django.utils.functional import lazy
from django.utils.translation import gettext as _

import faq.models

__all__ = (
    'AskQuestionForm',
    'AnswerForm',
)


class CleanFullNameForm(object):
    def clean_author_full_name(self) -> str:
        author_full_name = self.cleaned_data['author_full_name'].strip()
        try:
            names = [val.strip() for val in author_full_name.split(' ', 1)]
            assert len(names) == 2
            assert all(names)
        except AssertionError:
            raise forms.ValidationError(_('Make sure you have first and last names included.'))
        return author_full_name


class AskQuestionForm(CleanFullNameForm, forms.ModelForm):
    title = forms.CharField(widget=forms.Textarea())
    category = forms.ChoiceField(choices=lazy(faq.models.Category.as_choices, tuple))

    class Meta:
        model = faq.models.Question
        exclude = ('created', 'category')


class AnswerForm(CleanFullNameForm, forms.ModelForm):
    answer_id = forms.IntegerField(required=False)

    class Meta:
        model = faq.models.Answer
        fields = ('author_full_name', 'author_email', 'description',)
