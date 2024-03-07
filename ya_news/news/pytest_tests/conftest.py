# conftest.py
import pytest

from datetime import datetime, timedelta
from django.conf import settings
# Импортируем класс клиента.
from django.test.client import Client
from django.utils import timezone

# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import Comment, News


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def news():
    news = News.objects.create(  # Создаём объект новости.
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def all_news():
    today = datetime.today()
    all_news = [
        News(title=f'Новость {index}',
             text='Просто текст.',
             date=today - timedelta(days=index)
             )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(  # Создаём объект комментария.
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def all_comments(news, author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return all_comments


@pytest.fixture
# Фикстура запрашивает другую фикстуру создания новости.
def news_id_for_args(news):
    # И возвращает кортеж, который содержит id новости.
    # На то, что это кортеж, указывает запятая в конце выражения.
    return (news.id,)


@pytest.fixture
# Фикстура запрашивает другую фикстуру создания новости.
def comment_id_for_args(comment):
    # И возвращает кортеж, который содержит id новости.
    # На то, что это кортеж, указывает запятая в конце выражения.
    return (comment.id,)


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст'
    }
