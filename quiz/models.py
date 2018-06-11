import reprlib
from django.utils import timezone
from django.db import models


class Quiz(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)

    def __str__(self):
        repr1 = reprlib.Repr()
        repr1.maxstring = 200
        return "Quiz: {0} \n Description: {1}".format(self.name, repr1.repr(self.description))

    class Meta:
        verbose_name_plural = 'Quizzes'
        ordering = ['pk']


class Question(models.Model):
    text = models.CharField(max_length=400)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')

    def __str__(self):
        repr1 = reprlib.Repr()
        repr1.maxstring = 200
        return repr1.repr(self.text)

    class Meta:
        ordering = ['pk']


class Answer(models.Model):
    text = models.CharField(max_length=300)
    score = models.IntegerField(default=0)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')

    def __str__(self):
        repr1 = reprlib.Repr()
        repr1.maxstring = 200
        return repr1.repr(self.text) + ' Score: {0}'.format(self.score)


class ScoreRange(models.Model):
    text = models.CharField(max_length=300)
    score = models.IntegerField()
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='score_ranges')

    def __str__(self):
        return self.text + " -- Score: {0}".format(self.score)


class FeaturedQuestionsPage(models.Model):
    title = models.CharField(max_length=200)
    created = models.DateField(default=timezone.now)
    active_until = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title


class FeaturedQuestion(models.Model):
    question = models.ForeignKey(Question, null=True, on_delete=models.SET_NULL)
    featured_page = models.ForeignKey(FeaturedQuestionsPage, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.question.text
