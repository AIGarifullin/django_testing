from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from .conftest import URLS


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    (URLS.home, URLS.detail, URLS.login, URLS.logout, URLS.signup))
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
    (URLS.edit, URLS.delete))
def test_availability_for_comment_edit_and_delete(
        parametrized_client, name, expected_status, comment):
    """Проверить доступ страниц редактирования и удаления комментария."""
    response = parametrized_client.get(name)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    (URLS.edit, URLS.delete))
def test_redirect_for_anonymous_client(client, name):
    """Проверить редирект анонимного клиента."""
    redirect_url = f'{URLS.login}?next={name}'
    response = client.get(name)
    assertRedirects(response, redirect_url)
