from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as geomodels
from django.db import models


class User(AbstractUser):
    ROLE_INVESTOR = 'investor'
    ROLE_ADVISOR = 'advisor'
    ROLE_CHOICES = [
        (ROLE_INVESTOR, 'Investor'),
        (ROLE_ADVISOR, 'Advisor'),
    ]
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default=ROLE_INVESTOR)
    groups = models.ManyToManyField('auth.Group', related_name='app_users', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='app_users', blank=True)


class Institution(models.Model):
    TYPE_BANK = 'bank'
    TYPE_BROKER = 'broker'
    TYPE_FUND = 'fund'
    TYPE_CHOICES = [
        (TYPE_BANK, 'Bank'),
        (TYPE_BROKER, 'Broker'),
        (TYPE_FUND, 'Fund'),
    ]
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    location = geomodels.PointField(geography=True, srid=4326)

    class Meta:
        indexes = [
            models.Index(fields=['type']),
            geomodels.Index(fields=['location']),
        ]


class Portfolio(models.Model):
    user = models.ForeignKey('User', related_name='portfolios', on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('user', 'name')]
        ordering = ['-created_at']


class Asset(models.Model):
    TYPE_STOCK = 'stock'
    TYPE_BOND = 'bond'
    TYPE_MUTUAL_FUND = 'mutual_fund'
    TYPE_LOCAL = 'local_product'
    TYPE_CHOICES = [
        (TYPE_STOCK, 'Stock'),
        (TYPE_BOND, 'Bond'),
        (TYPE_MUTUAL_FUND, 'Mutual Fund'),
        (TYPE_LOCAL, 'Local Product'),
    ]
    name = models.CharField(max_length=128)
    asset_type = models.CharField(max_length=24, choices=TYPE_CHOICES)
    institution = models.ForeignKey('Institution', related_name='assets', on_delete=models.CASCADE)

    class Meta:
        indexes = [models.Index(fields=['asset_type'])]
        ordering = ['name']


class Transaction(models.Model):
    portfolio = models.ForeignKey('Portfolio', related_name='transactions', on_delete=models.CASCADE)
    asset = models.ForeignKey('Asset', related_name='transactions', on_delete=models.CASCADE)
    trans_type = models.CharField(max_length=16)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    price = models.DecimalField(max_digits=20, decimal_places=4)
    date = models.DateTimeField()
    details = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=['date', 'trans_type'])]
        ordering = ['-date']
