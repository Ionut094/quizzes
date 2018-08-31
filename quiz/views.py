import operator
from django.shortcuts import render, get_object_or_404, HttpResponse, redirect
from django.core.paginator import Paginator
from quiz import models


QUESTIONS_PER_PAGE = 2


def index(request):

    quizzes = models.Quiz.objects.all()

    return render(request, 'quiz/index.html', {'quizzes': quizzes})


def get_quiz_by_pk(request, pk):
    quiz = get_object_or_404(models.Quiz, pk=pk)
    all_questions = quiz.questions.all()

    paginator = Paginator(all_questions, QUESTIONS_PER_PAGE)

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
    all_questions = quiz.questions.all()
    question_ids = [question.id for question in all_questions]

    if not _are_valid(grouped_answers, question_ids):
        return HttpResponse('Please answer all the questions')

    answer_ids = grouped_answers.values()
    score = _calculate_score(answer_ids)
    result = _compute_result(quiz, score)

    request.session['saved-answers'] = {}

    suggested_answers = _get_suggested_answers(answer_ids, all_questions)

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


def _get_suggested_answers(answer_ids, all_questions):

    def get_selected_answer_for_question_by_related_answer(answer):
        question = answer.question
        return question.answers.filter(pk__in=answer_ids)[0]

    def calculate_coefficient(answer):
        selected_answer = get_selected_answer_for_question_by_related_answer(answer)
        return answer.score - selected_answer.score

    suggested_answers = []
    questions_per_page = _group_questions_per_page(all_questions)
    for page, questions in questions_per_page.items():
        answers = _get_answers_for_questions(questions)
        unselected_answers = [answer for answer in answers if answer.pk not in answer_ids]
        viable_answers = [answer for answer in unselected_answers if _is_answer_gt_selected_answer(answer, answer_ids)]
        if not viable_answers:
            continue
        suggested_answers.append(max(viable_answers, key=calculate_coefficient))
    return suggested_answers


def _parse_questions_and_answers_from_dict(post_dict):
    qa_dict = {}
    for key, answer_pk in post_dict.items():
        if key.startswith('answer'):
            i = key.find('[')
            question_pk = int(key[i + 1])
            qa_dict[question_pk] = int(answer_pk)
    return qa_dict


def _group_questions_per_page(questions):
    questions_per_page = {}
    pages = range(1, int(len(questions)/QUESTIONS_PER_PAGE) + 1)
    for page in pages:
        lb = (page-1)*QUESTIONS_PER_PAGE
        ub = page*QUESTIONS_PER_PAGE
        questions_per_page[page] = questions[lb:ub]

    return questions_per_page


def _get_answers_for_questions(questions):
    answers = []
    for question in questions:
        answers = answers + list(question.answers.all())
    return answers


def _is_answer_gt_selected_answer(answer, selected_answers):
    question = answer.question
    selected_answer = question.answers.filter(pk__in=selected_answers)[0]
    return selected_answer.score < answer.score

