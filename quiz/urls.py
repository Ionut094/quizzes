from django.urls import path
from .views import *


urlpatterns = [
    path('', index),
    path('quiz/<int:pk>/', get_quiz_by_pk, name='get_quiz'),
    path('submit-quiz/<int:pk>/', submit_quiz, name='submit_quiz')
]
