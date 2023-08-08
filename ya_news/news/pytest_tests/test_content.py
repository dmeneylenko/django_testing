import pytest

from django.conf import settings
from django.urls import reverse


def test_news_count(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.parametrize(
    'parametrized_client, form_in_list',
    (
        (pytest.lazy_fixture('admin_client'), 1),
        (pytest.lazy_fixture('client'), 0)
    ),
)
def test_has_no_form(parametrized_client, news, form_in_list):
    url = reverse('news:detail', args=(news.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_list
