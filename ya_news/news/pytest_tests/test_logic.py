from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from random import choice

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, comments_count',
    (
        (pytest.lazy_fixture('admin_client'), 1),
        (pytest.lazy_fixture('client'), 0)
    ),
)
def test_user_cant_create_comment(
    parametrized_client,
    news,
    form_data,
    comments_count
):
    url = reverse('news:detail', args=(news.id,))
    parametrized_client.post(url, data=form_data)
    assert Comment.objects.count() == comments_count


@pytest.mark.django_db
def test_user_cant_use_bad_words(admin_client, news, form_data):
    bad_words_data = {
        'text': f'Какой-то текст, {choice(BAD_WORDS)}, еще текст'
    }
    url = reverse('news:detail', args=(news.id,))
    form_data['text'] = bad_words_data
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, form_data, comment, news):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, form_data)
    assertRedirects(response, reverse(
        'news:detail',
        args=(news.id,)) + '#comments'
    )
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news


def test_other_user_not_can_edit_comment(admin_client, form_data, comment):
    url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author


def test_author_can_delete_comment(author_client, comment, news):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    assertRedirects(response, reverse(
        'news:detail',
        args=(news.id,)) + '#comments'
    )
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(admin_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
