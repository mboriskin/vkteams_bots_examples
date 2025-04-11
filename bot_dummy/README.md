### Пример работы бота

![VK Teams logotype](./resources/screenshot.png "logotype")

### запуск бота в cron

сделать файл бота исполняемым

```shell
chmod +x VKTeamsBot_getREviewsRuStore.py
```

открыть редактирование правил cron

```shell
crontab -e
```

добавить строку:

```
*/5 9-18 * * 1-5 /Users/user/Projects/vkteams_bots_examples/VKTeamsBot_getREviewsRuStore.py --token "токен_бота" > /Users/user/Projects/vkteams_bots_examples/rustore_scraper.console.log 2>&1
```

то есть каждые пять минут в рабочее время в рабочие дни вызывать вот этот скрипт
