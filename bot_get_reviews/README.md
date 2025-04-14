### Бот сбора отзывов из сторов

бот собирает отзывы из RuStore, GooglePlay, запрашивая обновления каждые 30 минут

```python
scheduler.add_job(scrap_and_post_reviews, 'interval', minutes=30)
```

### Пример работы бота

отзыв из RuStore

![VK Teams RuStore review](resources/screenshot.png "screenshot")

отзыв из Google Play

![VK Teams GooglePlay review](resources/screenshot2.png "screenshot2")
