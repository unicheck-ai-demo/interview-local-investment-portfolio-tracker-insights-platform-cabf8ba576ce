import pytest
from django.urls import reverse

from app.models import User

pytestmark = pytest.mark.django_db


def test_register_and_login(api_client):
    reg_url = reverse('api:register')
    login_url = reverse('api:login')
    # Register new user
    resp = api_client.post(reg_url, {'username': 'abc', 'password': 'xyz', 'role': 'investor'}, format='json')
    assert resp.status_code == 201
    token = resp.data['token']
    assert User.objects.filter(username='abc').exists()
    # Login
    resp2 = api_client.post(login_url, {'username': 'abc', 'password': 'xyz'}, format='json')
    assert resp2.status_code == 200
    assert resp2.data['token'] == token
