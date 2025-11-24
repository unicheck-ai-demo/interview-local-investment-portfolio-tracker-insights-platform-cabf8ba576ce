import pytest
from django.contrib.gis.geos import Point

from app.services import AssetService, InstitutionService, PortfolioService, TransactionService, UserService


@pytest.mark.django_db
def test_user_service_create_and_get():
    user = UserService.create_user('u1', 'pw', role='investor')
    got = UserService.get_by_username('u1')
    assert user.pk == got.pk
    assert got.role == 'investor'


@pytest.mark.django_db
def test_full_crud_cycle():
    user = UserService.create_user('u2', 'pw', role='advisor')
    inst = InstitutionService.create_institution('F1', 'fund', Point(1.1, 2.2, srid=4326))
    asset = AssetService.create_asset('Bond A', 'bond', inst)
    portfolio = PortfolioService.create_portfolio(user, 'MainPort')
    tx = TransactionService.create_transaction(portfolio, asset, 'buy', 1000, 99.25, '2024-06-01T09:00:00Z')
    got_tx = TransactionService.get(tx.pk)
    assert got_tx.amount == 1000
    assert got_tx.asset == asset
    assert got_tx.portfolio == portfolio
    PortfolioService.delete(portfolio.pk)
    assert PortfolioService.create_portfolio(user, 'MainPort').name == 'MainPort'
