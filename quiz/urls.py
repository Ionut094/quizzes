from django.urls import path
from .views import *


urlpatterns = [
    path('', index,name='home'),
    path('quiz/<int:pk>/', get_quiz_by_pk, name='get_quiz'),
    path('submit-quiz/<int:pk>/', submit_quiz, name='submit_quiz'),
    path('quiz/<int:pk>/prev-page/', save_answers_from_prev_page),
    path('quiz/<int:pk>/next-page/', save_answers_from_next_page),
]
