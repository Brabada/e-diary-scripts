import logging
import random
import sys

import django.core.exceptions
from datacenter.models import Schoolkid, Mark, Commendation, Lesson, \
    Chastisement, Subject


def get_schoolkid(kid_name):
    if not kid_name:
        raise ValueError("Строка с ФИО не должна быть пустой.")
    try:
        schoolkid = Schoolkid.objects.get(full_name__contains=kid_name)
    except django.core.exceptions.ObjectDoesNotExist:
        raise django.core.exceptions.ObjectDoesNotExist(
            f"Ошибка! По запросу {kid_name} ничего не найдено.\nВозможно вы "
            f"допустили опечатку.\nФормат записи ФИО или ФИ."
        )
    return schoolkid


def fix_marks(kid_name):
    schoolkid = get_schoolkid(kid_name)
    good_mark_limit = 4
    Mark.objects.filter(
        schoolkid=schoolkid,
        points__lt=good_mark_limit).update(points=5)


def remove_chastisements(kid_name):
    schoolkid = get_schoolkid(kid_name)
    kid_chastisements = Chastisement.objects.filter(schoolkid=schoolkid)
    kid_chastisements.delete()


def create_commendation(kid_name, subject):
    commendations = (
        'Молодец!',
        'Отлично!',
        'Хорошо!',
        'Гораздо лучше, чем я ожидал!',
        'Ты меня приятно удивил!',
        'Великолепно!',
        'Прекрасно!',
        'Ты меня очень обрадовал!',
        'Именно этого я давно ждал от тебя!',
        'Сказано здорово – просто и ясно!',
        'Ты, как всегда, точен!',
        'Очень хороший ответ!',
        'Талантливо!',
        'Ты сегодня прыгнул выше головы!',
        'Я поражен!',
        'Уже существенно лучше!',
        'Потрясающе!',
        'Замечательно!',
        'Прекрасное начало!',
        'Так держать!',
        'Ты на верном пути!',
        'Здорово!',
        'Это как раз то, что нужно!',
        'Я тобой горжусь!',
        'С каждым разом у тебя получается всё лучше!',
        'Мы с тобой не зря поработали!',
        'Я вижу, как ты стараешься!',
        'Ты растешь над собой!',
        'Ты многое сделал, я это вижу!',
        'Теперь у тебя точно все получится!',
    )
    random_commendation = random.choice(commendations)
    schoolkid = get_schoolkid(kid_name)
    try:
        Subject.objects.get(title=subject,
                            year_of_study=schoolkid.year_of_study)
    except django.core.exceptions.ObjectDoesNotExist:
        raise django.core.exceptions.ObjectDoesNotExist(
            f"По предмету {subject} нет результатов."
            f"Возможно вы допустили опечатку в названии предмета.")
    kid_lessons = Lesson.objects.filter(year_of_study=schoolkid.year_of_study,
                                        group_letter=schoolkid.group_letter,
                                        subject__title=subject
                                        ).order_by('-date')
    for lesson in kid_lessons:
        try:
            kid_commendation = Commendation.objects.get(
                schoolkid=schoolkid,
                subject__title=subject,
                created=lesson.date
            )
        except django.core.exceptions.ObjectDoesNotExist:
            kid_commendation = None
        if not kid_commendation:
            Commendation.objects.create(text=random_commendation,
                                        created=lesson.date,
                                        schoolkid=schoolkid,
                                        subject=lesson.subject,
                                        teacher=lesson.teacher)
            break


def fix_all(kid_name, subject):
    try:
        fix_marks(kid_name)
        remove_chastisements(kid_name)
        create_commendation(kid_name, subject)
    except django.core.exceptions.MultipleObjectsReturned:
        logging.error(f"Ошибка! По запросу {kid_name} найдено несколько "
                      "результатов. Уточните имя.")
        sys.exit(1)
    except django.core.exceptions.ObjectDoesNotExist as ex:
        logging.error(ex.args)
        sys.exit(1)
    except ValueError as val_err:
        logging.error(val_err.args)
        sys.exit(1)
