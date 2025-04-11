ACCESS_RESTRICTED_HELP_MESSAGE = """Не знаю кто ты.

Для добавления в white list напиши кому-нибудь из Админов бота
<a>@[admin1]</a>
<a>@[admin2]</a>
<a>@[admin3]</a>
"""


HELP_MESSAGE = """SeriousBot

Что можно сделать:
отправить боту команду /status или любой текст, кроме /help. Бот подскажет что делать дальше.

забрать коммиты из привязанного к таску Merge Request в ветку
/insert JIRATICKETKEY-8888 serious_branch

проверить коммит в ветке
/contains JIRATICKETKEY-8888 serious_branch

Владелец бота <a>@[m.boriskin]</a>
"""


ADMIN_HELP_MESSAGE = """Всё окей. Ты Админ бота.

Дополнительно к общим командам ты можешь:

добавить юзера в white list бота, чтобы он мог устанавливать Инциденты и Предупреждения
/add меншен_коллеги
пример:
/add <a>@[m.boriskin]</a>

удалить юзера из white list бота, чтобы он больше не мог устанавливать Инциденты и Предупреждения
/del меншен_коллеги
пример:
/del <a>@[m.boriskin]</a>

посмотреть всех пользователей, кто есть в white list бота
/white_list
"""
