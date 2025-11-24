import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point

from app.models import Asset, Institution, Portfolio, Transaction
from app.services import PortfolioService

pytestmark = pytest.mark.django_db


@pytest.mark.xfail(strict=True)
def test_portfolio_performance_single_query(db, django_assert_num_queries):
    User = get_user_model()
    user = User.objects.create_user(username='u', password='p', role='investor')
    inst = Institution.objects.create(name='I', type='bank', location=Point(0, 0, srid=4326))
    asset = Asset.objects.create(name='A', asset_type='stock', institution=inst)
    portfolio = Portfolio.objects.create(user=user, name='P')
    Transaction.objects.create(
        portfolio=portfolio, asset=asset, trans_type='buy', amount=10, price=5, date='2024-01-01T00:00:00Z'
    )
    Transaction.objects.create(
        portfolio=portfolio, asset=asset, trans_type='buy', amount=20, price=15, date='2024-01-02T00:00:00Z'
    )
    with django_assert_num_queries(1):
        avg_price, total_amount = PortfolioService.portfolio_performance(portfolio.id)
    assert avg_price == pytest.approx((5 + 15) / 2)
    assert total_amount == 30
