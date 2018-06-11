from django.contrib import admin
from .models import *
from .forms import *


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    fields = ('name', 'description')
    list_filter = ('name', )
    search_fields = ('name', 'description')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz')
    list_filter = ('quiz', )
    search_fields = ('text', )


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    fields = ('text', 'score', 'question')
    list_display = ('text', 'score', 'question')
    search_fields = ('text', 'question__text')
    ordering = ('-score', )


@admin.register(ScoreRange)
class ResultAdmin(admin.ModelAdmin):
    fields = ('text', 'score', 'quiz')
    ordering = ('-score', )


@admin.register(FeaturedQuestion)
class FeaturedQuestionAdmin(admin.ModelAdmin):
    form = FeaturedQuestionForm


class FeaturedQuestionInLine(admin.TabularInline):
    model = FeaturedQuestion
    form = FeaturedQuestionForm
    extra = 4
    max_num = 4


@admin.register(FeaturedQuestionsPage)
class FeaturedQuestionsPageAdmin(admin.ModelAdmin):
    form = FeaturedQuestionsPageForm
    inlines = [
        FeaturedQuestionInLine
    ]