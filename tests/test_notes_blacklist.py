import pytest

from utils.notes_blacklist import is_blacklisted


@pytest.mark.parametrize(
    'message, is_blocked',
    (
        ('', False),
        ('qwerty', False),
        ('@avbabich прошу присоединиться к задаче и сообщить сюда в комменты, на твой взгляд, '
         'каких компонентов фронта не хватает.', False),

        ('assigned to @katuxa and unassigned @gagara11', True),
        ('unassigned @gagara11', True),
        ('assigned to @katuxa', True),

        ('closed', True),
        ('closed via commit e29b8773411bb43b9232e27be15789af6ceeb545', True),
        ('closed via merge request !32', True),
        ('reopened', True),

        ('changed the description', True),
        ('changed time estimate to 2d', True),
        ('changed title from **Разработка сервиса ЕПГУ (Екб)** to **Разработка сервиса ЕПГУ (Е{+ЖД, Е+}кб)**', True),
        ('created branch [`7-`](https://gitlab.ezmp.kbinform.ru/ezmp/chel/compare/development...7-)', True),
        ('marked the task **Добавить столбец "Источник"** as completed', True),
        ('marked the task **В табличные формы мастера (в работе/отработано) добавить столбец '
         '"Фактическая дата" (это дата последней смены статуса)** as completed', True),

        ('added 1h 30m of time spent at 2018-05-29', True),

        ('mentioned in issue #114', True),
        ('mentioned in issue chel-taxi#7', True),
        ('mentioned in merge request !41', True),

        ('added ~221 and removed ~88 labels', True),
        ('added ~91 ~221 and removed ~88 labels', True),
        ('removed ~9 label', True),
        ('added ~108 label', True),
        ('added ~245 ~244 labels', True),
        ('added ~8 ~88 labels', True),
    )
)
def test_is_message_blacklisted(message, is_blocked):
    assert is_blacklisted(message) == is_blocked
