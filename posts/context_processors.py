import datetime as dt
# Когда удаляю этот файл, то pytest валится...


def year(request):
    year = dt.datetime.now().year
    return {
        'year': year,
    }
