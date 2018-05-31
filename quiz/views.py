import operator
from django.shortcuts import render, get_object_or_404, HttpResponse, redirect
from django.core.paginator import Paginator
from quiz import models


def index(request):

    quizzes = models.Quiz.objects.all()

    return render(request, 'quiz/index.html', {'quizzes': quizzes})


def get_quiz_by_pk(request, pk):
    quiz = get_object_or_404(models.Quiz, pk=pk)
    all_questions = quiz.questions.all()

    paginator = Paginator(all_questions, 2)

    page = int(request.GET.get('page', 1))
    if page <= 0:
        page = 1

    questions = paginator.get_page(page)

    saved_answers = request.session.get('saved-answers', {})

    checked_answers = _get_checked_answers(saved_answers, questions)

    return render(request, 'quiz/quiz_detail.html', {'quiz': quiz, 'questions': questions,
                                                     'checked_answers': checked_answers})


def submit_quiz(request, pk):
    _save_answers_to_session(request)
    grouped_answers = _get_normalized_dict(request.session['saved-answers'])

    quiz = get_object_or_404(models.Quiz, pk=pk)
    question_ids = [question.id for question in quiz.questions.all()]

    if not _are_valid(grouped_answers, question_ids):
        return HttpResponse('Please answer all the questions')

    answer_ids = [a_id for q_id in question_ids for a_id in grouped_answers[q_id]]
    score = _calculate_score(answer_ids)
    result = _compute_result(quiz, score)

    request.session['saved-answers'] = {}

    return render(request, 'quiz/quiz_result.html', {'quiz': quiz, 'score': score, 'result': result})


def save_answers_from_prev_page(request, pk):
    _save_answers_to_session(request)
    page = request.GET['page']
    return redirect(f'/quiz/{pk}/?page={page}')


def save_answers_from_next_page(request, pk):
    _save_answers_to_session(request)
    page = request.GET['page']
    return redirect(f'/quiz/{pk}/?page={page}')


def _group_answers_by_question(answers):
    answers_by_questions = {}

    for tuple_str in answers:
        ids = tuple_str.split(',')
        q_id = int(ids[0])
        a_id = int(ids[1])
        answers_by_questions.setdefault(q_id, []).append(a_id)

    return answers_by_questions


def _are_valid(answers_by_question, question_ids):
    for q_id in question_ids:
        if q_id not in answers_by_question:
            return False
        else:
            if not answers_by_question[q_id]:
                return False
    return True


def _calculate_score(answers):

    return sum([models.Answer.objects.get(pk=a_id).score for a_id in answers])


def _save_answers_to_session(request):
    answers = request.POST.getlist('answers')
    grouped_answers = _group_answers_by_question(answers)

    saved_answers = request.session.setdefault('saved-answers', {})
    saved_answers.update(grouped_answers)
    request.session['saved-answers'] = saved_answers


def _get_normalized_dict(grouped_answers):
    answers_by_question = {}
    for key in grouped_answers.keys():
        answers_by_question[int(key)] = grouped_answers[key]

    return answers_by_question


def _get_checked_answers(saved_answers, questions):
    checked_answers = []
    for pk in [question.pk for question in questions]:

        if pk in saved_answers:
            checked_answers = checked_answers + saved_answers[pk]
        elif str(pk) in saved_answers:
            checked_answers = checked_answers + saved_answers[str(pk)]
    return checked_answers


def _compute_result(quiz, score):
    score_ranges = quiz.score_ranges.all()
    if not score_ranges:
        return None

    ranges = zip(score_ranges, score_ranges[1:])
    if not ranges:
        return None

    for s_range in ranges:
        if s_range[0].score < score < s_range[1].score:
            return s_range[0]
    return score_ranges[len(score_ranges) - 1]
