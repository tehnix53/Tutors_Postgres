from data import teachers
import random

def give_me_lesson(some_dict):
    i = 0
    for k, v in some_dict.items():
        if v == True:
            i += 1
    if i == 0:
        return "Нет свободных уроков"
    else:
        return some_dict


def give_me_friday(some_day):
    day_dict = {'wed': 'Среда', 'sun': 'Воскресенье', 'fri': 'Пятница',
                'tue': 'Вторник', 'mon': 'Понедельник', 'thu': 'Четверг',
                'sat': 'Суббота'}
    if some_day in day_dict:
        return (day_dict[some_day])


def lesson_day(some_dict):
    new = {}
    for k, v in some_dict.items():
        new[give_me_friday(k)] = give_me_lesson(v)
    return new


teach_workday = {}
for i in teachers:
    teach_workday[i['id']] = lesson_day(i['free'])


def random_six():
    a = []
    i = 0
    while i < 6:
        b = (random.randint(0, 11))
        if b not in a:
            a += [b]
            i += 1
    return a
