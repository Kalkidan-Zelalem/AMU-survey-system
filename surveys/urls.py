# surveys/urls.py

from django.urls import path
from . import views

# This creates the "surveys:" namespace that is used in all templates and views.
app_name = 'surveys'

urlpatterns = [
    # This is now your main home page, and its full name is 'surveys:survey-list'.
    path('', views.SurveyListView.as_view(), name='survey-list'),
    
    # All your other URL patterns are preserved and will work correctly.
    path('survey/create/', views.survey_create_view, name='survey-create'),
    path('survey/<int:pk>/', views.SurveyDetailView.as_view(), name='survey-detail'),
    path('survey/<int:pk>/update/', views.SurveyUpdateView.as_view(), name='survey-update'),
    path('survey/<int:pk>/delete/', views.SurveyDeleteView.as_view(), name='survey-delete'),
    path('question/<int:pk>/edit/', views.QuestionUpdateView.as_view(), name='question-edit'),
    path('survey/<int:pk>/take/', views.SurveyTakeView.as_view(), name='survey-take'),
    path('public/<uuid:public_id>/', views.SurveyTakeView.as_view(), name='survey-public-take'),
    path('survey/<int:pk>/results/', views.SurveyResultsView.as_view(), name='survey-results'),
    path('survey/thank-you/', views.SurveyThankYouView.as_view(), name='survey-thank-you'),
]