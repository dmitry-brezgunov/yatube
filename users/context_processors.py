import datetime as dt


def year(request):
    '''Динамическое отображение года для футера'''
    current_year = dt.datetime.today().year
    return {"year": current_year}
