import pytest
from django.conf import settings

from news.forms import CommentForm

from .conftest import URLS


@pytest.mark.django_db
def test_news_count_order(client, all_news):
    """Проверить пагинацию и сортировку новостей."""
    response = client.get(URLS.home)
    object_list = response.context['object_list']
    news_count = object_list.count()
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news):
    """Проверить сортировку комментариев."""
    response = client.get(URLS.detail)
    assert 'news' in response.context
    news = response.context['news']
    all_comments_list = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments_list]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_form(client):
    """Проверить доступ страницы для анонимного клиента."""
    response = client.get(URLS.detail)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_admin_client_form(author_client, comment):
    """Проверить доступ страницы для автора новости."""
    admin_response = author_client.get(URLS.detail)
    assert 'form' in admin_response.context
    assert isinstance(admin_response.context['form'], CommentForm)
