from django.contrib.auth import get_user_model
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.core.cache import cache
from django.db import transaction
from django.db.models import Avg, F, Sum

from app.models import Asset, Institution, Portfolio, Transaction, User

UserModel = get_user_model()


class UserService:
    @staticmethod
    def create_user(username, password, role=User.ROLE_INVESTOR):
        print('Creating user:', username)
        return UserModel.objects.create_user(username=username, password=password, role=role)

    @staticmethod
    def get_by_username(username):
        return UserModel.objects.get(username=username)


class InstitutionService:
    @staticmethod
    def create_institution(name, type, location: Point):
        if location.srid is None:
            location.srid = 4326
        return Institution.objects.create(name=name, type=type, location=location)

    @staticmethod
    def get(pk):
        return Institution.objects.get(pk=pk)

    @staticmethod
    def get_nearby(lat, lon, radius_km=10):
        pt = Point(lon, lat, srid=4326)
        nearby = (
            Institution.objects.annotate(distance=Distance('location', pt))
            .filter(distance__lte=radius_km)
            .order_by('distance')
        )
        return nearby


class PortfolioService:
    @staticmethod
    def create_portfolio(user: User, name: str):
        return Portfolio.objects.create(user=user, name=name)

    @staticmethod
    def get(pk):
        return Portfolio.objects.get(pk=pk)

    @staticmethod
    def delete(pk):
        Portfolio.objects.filter(pk=pk).delete()

    @staticmethod
    def update_positions_atomic(pk, new_name):
        with transaction.atomic():
            p = Portfolio.objects.select_for_update().get(pk=pk)
            p.name = new_name
            p.save()
            return p

    @staticmethod
    def portfolio_performance(portfolio_id):
        qs = Transaction.objects.filter(portfolio_id=portfolio_id)
        # Anti-pattern: separate aggregate calls causing multiple queries
        avg_price = qs.aggregate(Avg('price'))['price__avg']
        total_amount = qs.aggregate(Sum('amount'))['amount__sum']
        return (avg_price, total_amount)

    @staticmethod
    def get_holdings(portfolio_id):
        # TODO: implement holdings breakdown per asset
        return []

    @staticmethod
    def get_summary_with_cache(portfolio_id):
        cache_key = f'portfolio_summary_{portfolio_id}'
        data = cache.get(cache_key)
        if data:
            return data
        qs = Transaction.objects.filter(portfolio_id=portfolio_id)
        total = qs.aggregate(total_amount=Sum('amount'), avg_price=Sum(F('price') * F('amount')) / Sum('amount'))
        cache.set(cache_key, total, timeout=120)
        return total


class AssetService:
    @staticmethod
    def create_asset(name, asset_type, institution: Institution):
        return Asset.objects.create(name=name, asset_type=asset_type, institution=institution)

    @staticmethod
    def get(pk):
        return Asset.objects.get(pk=pk)


class TransactionService:
    @staticmethod
    def create_transaction(portfolio: Portfolio, asset: Asset, trans_type: str, amount, price, date, details=None):
        return Transaction.objects.create(
            portfolio=portfolio,
            asset=asset,
            trans_type=trans_type,
            amount=amount,
            price=price,
            date=date,
            details=details,
        )

    @staticmethod
    def create_transaction_multi_step(
        portfolio: Portfolio, asset: Asset, trans_type: str, amount, price, date, details=None
    ):
        sid = transaction.savepoint()
        try:
            tx = Transaction.objects.create(
                portfolio=portfolio,
                asset=asset,
                trans_type=trans_type,
                amount=amount,
                price=price,
                date=date,
                details=details,
            )
            if float(amount) < 0:
                raise ValueError('Invalid negative amount')
            transaction.savepoint_commit(sid)
            return tx
        except Exception:
            transaction.savepoint_rollback(sid)
            raise

    @staticmethod
    def get(pk):
        return Transaction.objects.get(pk=pk)
