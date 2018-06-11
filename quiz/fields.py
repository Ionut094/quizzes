from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget
from .models import Question


class QuestionSelectWidget(ModelSelect2Widget):

    model = Question
    search_fields = [
        'text__icontains',
        'quiz__name__icontains',
        'quiz__description__icontains'
    ]
