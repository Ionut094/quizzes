from django.shortcuts import render, get_object_or_404, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from quiz import models


def index(request):

    quizzes = models.Quiz.objects.all()

    return render(request, 'quiz/index.html', {'quizzes': quizzes})


def get_quiz_by_pk(request, pk):

    quiz = get_object_or_404(models.Quiz, pk=pk)
    questions = quiz.questions.all()
    return render(request, 'quiz/quiz_detail.html', {'quiz': quiz, 'questions': questions})


@csrf_exempt
def submit_quiz(request, pk):
    answers = request.POST.getlist('answers')
    grouped_answers = _group_answers_by_question(answers)

    quiz = get_object_or_404(models.Quiz, pk=pk)
    question_ids = [question.id for question in quiz.questions.all()]

    if not _are_valid(grouped_answers, question_ids):
        return HttpResponse('Please answer all the questions')

    answer_ids = [a_id for q_id in question_ids for a_id in grouped_answers[q_id]]
    score = _calculate_score(answer_ids)

    return HttpResponse('Your score was: {0}'.format(score))


def _group_answers_by_question(answers):
    answers_by_questions = {}

    for tuple_str in answers:
        ids = tuple_str.split(',')
        q_id = int(ids[0])
        a_id = int(ids[1])
        answers_by_questions.setdefault(q_id, []).append(a_id)

    return answers_by_questions


def _are_valid(answers_by_question,question_ids):
   for q_id in question_ids:
       if q_id not in answers_by_question:
           return False
       else:
           if not answers_by_question[q_id]:
                return False
   return True


def _calculate_score(answers):

    return sum([models.Answer.objects.get(pk=a_id).score for a_id in answers])
