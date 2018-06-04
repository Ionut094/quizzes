import operator
import inspect
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
    qa_dict = _parse_questions_and_answers_from_dict(request.POST)
    _save_answers_to_session(request, qa_dict)
    grouped_answers = _get_normalized_dict(request.session['saved-answers'])

    quiz = get_object_or_404(models.Quiz, pk=pk)
    question_ids = [question.id for question in quiz.questions.all()]

    if not _are_valid(grouped_answers, question_ids):
        return HttpResponse('Please answer all the questions')

    answer_ids = grouped_answers.values()
    score = _calculate_score(answer_ids)
    result = _compute_result(quiz, score)

    request.session['saved-answers'] = {}

    suggested_answers = _get_suggested_answers(answer_ids, question_ids)

    return render(request, 'quiz/quiz_result.html',
                  {'quiz': quiz, 'score': score, 'result': result, 'suggested_answers': suggested_answers})


def save_answers_from_prev_page(request, pk):
    qa_dict = _parse_questions_and_answers_from_dict(request.POST)
    _save_answers_to_session(request, qa_dict)
    page = request.GET['page']
    return redirect(f'/quiz/{pk}/?page={page}')


def save_answers_from_next_page(request, pk):
    qa_dict = _parse_questions_and_answers_from_dict(request.POST)
    _save_answers_to_session(request, qa_dict)
    page = request.GET['page']
    return redirect(f'/quiz/{pk}/?page={page}')


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


def _save_answers_to_session(request, answers):
    saved_answers = request.session.setdefault('saved-answers', {})
    saved_answers.update(answers)
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
            checked_answers.append(saved_answers[pk])
        elif str(pk) in saved_answers:
            checked_answers.append(saved_answers[str(pk)])
    return checked_answers


def _compute_result(quiz, score):
    score_ranges = quiz.score_ranges.all().order_by('score')
    if not score_ranges:
        return None

    for s_range in score_ranges:
        if s_range.score > score:
            return s_range

    return score_ranges.last()


def _get_suggested_answers(answer_ids, question_ids):
    suggested_answers = []
    for question_id in question_ids:
        question = models.Question.objects.get(pk=question_id)
        suggested_answers.append(max(question.answers.filter(score__gt=0).exclude(pk__in=answer_ids),
                                     key=operator.attrgetter('score')))
        
    return suggested_answers


def _parse_questions_and_answers_from_dict(post_dict):
    qa_dict = {}
    for key, answer_pk in post_dict.items():
        if key.startswith('answer'):
            i = key.find('[')
            question_pk = int(key[i + 1])
            qa_dict[question_pk] = int(answer_pk)
    return qa_dict
