# test_logic.py
import pytest

from django.urls import reverse

from http import HTTPStatus
# Импортируем функции для проверки редиректа и ошибки формы:
from pytest_django.asserts import assertRedirects, assertFormError

# Импортируем из модуля forms сообщение об ошибке:
from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


# Указываем фикстуру form_data в параметрах теста.
def test_user_can_create_comment(author_client, author,
                                 news, form_data,
                                 news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    # В POST-запросе отправляем данные, полученные из фикстуры form_data:
    response = author_client.post(url, data=form_data)
    # Проверяем, что был выполнен редирект на страницу успешного добавления заметки:
    assertRedirects(response, f'{url}#comments')
    # Считаем количество комментариев.
    assert Comment.objects.count() == 1
    # Получаем объект комментария из базы.
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


# Добавляем маркер, который обеспечит доступ к базе данных:
@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client,
                                            form_data,
                                            news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    # Через анонимный клиент пытаемся создать комментарий:
    client.post(url, data=form_data)
    # Считаем количество комментариев в БД, ожидаем 0 комментариев.
    assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(author_client,
                                 news_id_for_args):
    # Формируем данные для отправки формы; текст включает
    # первое слово из списка стоп-слов.
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=news_id_for_args)
    # Пытаемся создать новый комментарий:
    response = author_client.post(url, data=bad_words_data)
    # Проверяем, что в ответе содержится ошибка формы для поля text:
    assertFormError(response, 'form', 'text', errors=WARNING)
    # Убеждаемся, что количество комментариев в базе равно 0:
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, form_data,
                                   news_id_for_args,
                                   comment_id_for_args):
    news_url = reverse('news:detail', args=news_id_for_args)  # Адрес новости.
    url_to_comments = news_url + '#comments'  # Адрес блока с комментариями. 
    delete_url = reverse('news:delete', args=comment_id_for_args)
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
          client,
          reader_client,
          comment_id_for_args):
    # Выполняем запрос на удаление от пользователя-читателя.
    delete_url = reverse('news:delete', args=comment_id_for_args) 
    response = client.delete(delete_url)
    response_reader = reader_client.delete(delete_url)
    # Проверяем, что вернулась 404 ошибка.
    assert ((response.status_code and response_reader.status_code)
            == HTTPStatus.NOT_FOUND)
    # Убедимся, что комментарий по-прежнему на месте.
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client,
                                 comment,
                                 news_id_for_args,
                                 comment_id_for_args,
                                 form_data):
    # Выполняем запрос на редактирование от имени автора комментария.
    news_url = reverse('news:detail', args=news_id_for_args)  # Адрес новости.
    url_to_comments = news_url + '#comments'  # Адрес блока с комментариями. 
    edit_url = reverse('news:edit', args=comment_id_for_args)
    form_data['text'] = NEW_COMMENT_TEXT
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    # Проверяем, что текст комментария соответствует обновленному.
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(client,
                                                reader_client,
                                                comment,
                                                form_data,
                                                comment_id_for_args):
    edit_url = reverse('news:edit', args=comment_id_for_args) 
    response = client.post(edit_url, data=form_data)
    response_reader = reader_client.post(edit_url, data=form_data)
    # Проверяем, что вернулась 404 ошибка.
    assert ((response.status_code and response_reader.status_code)
            == HTTPStatus.NOT_FOUND)
    comment.refresh_from_db()
    # Убедимся, что комментарий по-прежнему на месте.
    assert comment.text == COMMENT_TEXT
