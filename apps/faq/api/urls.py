from django.urls import path

from .views import *  # noqa

app_name = 'faq_api'
urlpatterns = [
    path('questions/', QuestionsAPIView.as_view(), name='questions'),
    path('question/<int:pk>/', QuestionDetailAPIView.as_view(), name='question_detail'),
    path('ask-question/', AskQuestionAPIView.as_view(), name='ask_question'),
    path('report/<int:pk>/', ReportAPIView.as_view(), name='report'),
    path('new-comment/', NewCommentAPIView.as_view(), name='new_comment'),
    path('categories/', CategoriesAPIView.as_view(), name='category'),
]
