import pytest
from django.urls import reverse
from rest_framework import status

from app.models import User

pytestmark = pytest.mark.django_db


def test_user_list(api_client):
    User.objects.create_user(username='x', password='pw', role='investor')
    url = reverse('api:user-list')
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    assert any(u['username'] == 'x' for u in resp.data['results'])


def test_institution_create(authenticated_api_client):
    url = reverse('api:institution-list')
    data = {
        'name': 'GeoBank',
        'type': 'bank',
        'location': {'type': 'Point', 'coordinates': [14.44, 50.09]},
    }
    resp = authenticated_api_client.post(url, data, format='json')
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data['name'] == 'GeoBank'
