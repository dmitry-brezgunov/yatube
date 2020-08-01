from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    '''Фильтр для добавления класса к полю в шаблоне'''
    return field.as_widget(attrs={"class": css})


@register.filter
def format_count(word, count):
    '''Фильтр для склонение слова 'комментарий' по числу'''
    remainder_ten = count % 10
    remainder_hundred = count % 100
    if remainder_ten == 0:
        word += 'ев'
    elif remainder_ten == 1 and remainder_hundred != 11:
        word += 'й'
    elif remainder_ten < 5 and remainder_hundred not in [11, 12, 13, 14]:
        word += 'я'
    else:
        word += 'ев'
    return word
