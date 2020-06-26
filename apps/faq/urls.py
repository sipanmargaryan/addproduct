from django.urls import path

from . import views

app_name = 'faq'
urlpatterns = [
    path('top-questions/', views.QuestionsView.as_view(), name='top_questions'),
    path('recent-questions/', views.QuestionsView.as_view(top=False), name='recent_questions'),
    path('ask-question/', views.AskQuestionView.as_view(), name='ask_question'),
    path('question/<int:pk>/<str:slug>/', views.QuestionDetailView.as_view(), name='question_detail'),
    path('report/<int:pk>/', views.ReportView.as_view(), name='report'),
]
