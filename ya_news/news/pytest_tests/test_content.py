# test_content.py
import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count_order(client, all_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news_id_for_args):
    detail_url = reverse('news:detail', args=news_id_for_args)
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments_list = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments_list]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_admin_anonymous_client_form(client, author_client, news_id_for_args):
    detail_url = reverse('news:detail', args=news_id_for_args)
    response = client.get(detail_url)
    admin_response = author_client.get(detail_url)
    assert 'form' not in response.context
    assert isinstance(admin_response.context['form'], CommentForm)
