from django_select2 import forms as ds2_froms
from django import forms
from . import models
from . import fields


class FeaturedQuestionsPageForm(forms.ModelForm):

    class Meta:
        exclude = []
        model = models.FeaturedQuestionsPage
        fields = ('title', 'created', 'active_until')


class FeaturedQuestionForm(forms.ModelForm):

    class Meta:

        exclude = []
        model = models.Question
        widgets = {
            'question': fields.QuestionSelectWidget(attrs={
                'style': 'width: 200px'
            })
        }
