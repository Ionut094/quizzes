from django.db import models
import reprlib


class Quiz(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)

    def __str__(self):
        repr1 = reprlib.Repr()
        repr1.maxstring = 200
        return "Quiz: {0} \n Description: {1}".format(self.name, repr1.repr(self.description))


class Question(models.Model):
    text = models.CharField(max_length=400)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

    def __str__(self):
        repr1 = reprlib.Repr()
        repr1.maxstring = 200
        return repr1.repr1(self.text)


class Answer(models.Model):
    text = models.CharField(max_length=300)
    score = models.IntegerField(default=0)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        repr1 = reprlib.Repr()
        repr1.maxstring = 200
        return repr1.repr(self.text) + ' Score: {0}'.format(self.score)


class Result(models.Model):
    text = models.CharField(max_length=300)
    score = models.IntegerField()
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
