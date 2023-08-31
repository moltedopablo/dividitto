from django.utils import translation
import calendar
import datetime


def get_spanish_month_name(month_number):
    names = {
        1: 'Enero',
        2: 'Febrero',
        3: 'Marzo',
        4: 'Abril',
        5: 'Mayo',
        6: 'Junio',
        7: 'Julio',
        8: 'Agosto',
        9: 'Septiembre',
        10: 'Octubre',
        11: 'Noviembre',
        12: 'Diciembre'
    }
    return names[month_number]


def get_month_name(month):
    if 'es' == translation.get_language():
        return get_spanish_month_name(month)
    else:
        return calendar.month_name[month]


def get_current_month_year():
    now = datetime.datetime.now()
    return (now.month, now.year)


def get_date_params(month, year):
    if month is None:
        month = get_current_month_year()[0]
    if year is None:
        year = get_current_month_year()[1]

    (month, year) = (int(month), int(year))
    (prev_month, prev_year) = (month - 1, year) if month > 1 else (12, year - 1)
    (next_month, next_year) = (month + 1, year) if month < 12 else (1, year + 1)
    return {
        'month': month,
        'year': year,
        'month_name': get_month_name(month),
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year, }
