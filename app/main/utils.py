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
