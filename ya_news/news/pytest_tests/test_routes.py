# test_routes.py
from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from .conftest import url


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    (url.home, url.detail, url.login, url.logout, url.signup))
def test_pages_availability(client, name, news):
    """Проверить доступ страниц для всех пользователей."""
    response = client.get(name)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND)
    ),
)
@pytest.mark.parametrize(
    'name',
    (url.edit, url.delete))
def test_availability_for_comment_edit_and_delete(
        parametrized_client, name, expected_status, comment):
    """Проверить доступ страниц редактирования и удаления комментария."""
    response = parametrized_client.get(name)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    (url.edit, url.delete))
def test_redirect_for_anonymous_client(client, name):
    """Проверить редирект анонимного клиента."""
    redirect_url = f'{url.login}?next={name}'
    response = client.get(name)
    assertRedirects(response, redirect_url)
