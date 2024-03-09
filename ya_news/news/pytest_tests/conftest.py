# conftest.py
from datetime import datetime, timedelta
from collections import namedtuple

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

COMMENT_TEXT = 'Текст комментария'
ID = 1
NEW_COMMENT_TEXT = 'Обновлённый комментарий'

form_data = {'text': COMMENT_TEXT}

url_name = namedtuple(
    'name',
    ['home', 'detail', 'comments', 'delete',
     'edit', 'login', 'logout', 'signup'])

url = url_name(
    reverse('news:home'),
    reverse('news:detail', args=(ID,)),
    reverse('news:detail', args=(ID,)) + '#comments',
    reverse('news:delete', args=(ID,)),
    reverse('news:edit', args=(ID,)),
    reverse('users:login'),
    reverse('users:logout'),
    reverse('users:signup'))


@pytest.fixture
def author(django_user_model):
    """Создать модель пользователя Автор."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    """Создать модель пользователя Читатель."""
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    """Создать и залогинить клиента-Автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    """Создать и залогинить клиента-Читателя."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    """Создать объект news класса News."""
    return News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )


@pytest.fixture
def all_news():
    """Создать несколько объектов news класса News."""
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
    """Создать объект comment класса Comment."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )


@pytest.fixture
def all_comments(news, author):
    """Создать несколько объектов comment класса Comment."""
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
