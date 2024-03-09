from http import HTTPStatus
from random import choice

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

from .conftest import COMMENT_TEXT, form_data, NEW_COMMENT_TEXT, URLS


def test_user_can_create_comment(author_client, author, news, comment):
    """Проверить возможность создания комментария автором новости."""
    comment.delete()
    init_comments_count = Comment.objects.count()
    response = author_client.post(URLS.detail,
                                  data=form_data)
    assertRedirects(response, f'{URLS.detail}#comments')
    assert Comment.objects.count() == init_comments_count + 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, comment):
    """Проверить невозможность создания комментария анонимом."""
    comment.delete()
    init_comments_count = Comment.objects.count()
    client.post(URLS.detail, data=form_data)
    assert Comment.objects.count() == init_comments_count


def test_user_cant_use_bad_words(author_client, news):
    """Проверить появление сообщения о наличии плохих слов в комментарии."""
    bad_words_data = {'text':
                      f'Какой-то текст, {choice(BAD_WORDS)}, еще текст'}
    init_comments_count = Comment.objects.count()
    response = author_client.post(URLS.detail, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == init_comments_count


def test_author_can_delete_comment(author_client, comment):
    """Проверить возможность удаления комментария автором новости."""
    init_comments_count = Comment.objects.count()
    response = author_client.delete(URLS.delete)
    assertRedirects(response, URLS.comments)
    assert Comment.objects.count() == init_comments_count - 1


def test_user_cant_delete_comment_of_another_user(client,
                                                  reader_client):
    """Проверить невозможность удаления комментария не автором."""
    init_comments_count = Comment.objects.count()
    response = client.delete(URLS.delete)
    response_reader = reader_client.delete(URLS.delete)
    assert ((response.status_code and response_reader.status_code)
            == HTTPStatus.NOT_FOUND)
    assert Comment.objects.count() == init_comments_count


def test_author_can_edit_comment(author_client, comment):
    """Проверить возможность редактирования комментария автором."""
    form_data['text'] = NEW_COMMENT_TEXT
    response = author_client.post(URLS.edit, data=form_data)
    assertRedirects(response, URLS.comments)
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(client,
                                                reader_client,
                                                comment):
    """Проверить невозможность редактирования комментария не автором."""
    response = client.post(URLS.edit, data=form_data)
    response_reader = reader_client.post(URLS.edit, data=form_data)
    assert ((response.status_code and response_reader.status_code)
            == HTTPStatus.NOT_FOUND)
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
