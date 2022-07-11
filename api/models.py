"""Module specifying the models of the application."""

from decimal import Decimal

from django.db import models


class FX(models.Model):
    """Schema for table `FX`. Stores most updated exchange rates."""
    currency: str = models.CharField(max_length=3, primary_key=True)
    rate: Decimal = models.DecimalField(max_digits=19, decimal_places=5)
    updated: int = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.currency} {self.rate}'

class Bond(models.Model):
    """Schema for table `bond`. Stores most updated bond data."""
    bond_id: str = models.CharField(max_length=6, primary_key=True)
    currency: str = models.ForeignKey(FX, on_delete=models.CASCADE)
    price: Decimal = models.DecimalField(
        max_digits=19, decimal_places=5, blank=True, null=True
    )
    updated: int = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.bond_id} {self.currency}'

class Desk(models.Model):
    """Schema for table `desk`. Stores most updated desk data."""
    desk_id: str = models.CharField(max_length=5, primary_key=True)
    cash: Decimal = models.DecimalField(max_digits=19, decimal_places=5)
    updated: int = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.desk_id} ${self.cash}'

class Trader(models.Model):
    """Schema for table `trader`. Stores all bonds held."""
    trader_id: str = models.CharField(max_length=8, primary_key=True)
    desk_id: str = models.ForeignKey(Desk, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.trader_id} ${self.desk_id}'

class Book(models.Model):
    """Schema for table `book`. Each entry is "owned" by one Trader."""
    book_id: str = models.CharField(max_length=5, primary_key=True)
    trader_id: str = models.ForeignKey(Trader, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.book_id} ${self.trader_id}'

class BondRecord(models.Model):
    """Schema for table `bonds_held`. Stores a bond held by a trader."""
    trader_id: str = models.ForeignKey(Trader, on_delete=models.CASCADE)
    book_id: str = models.ForeignKey(Book, on_delete=models.CASCADE)
    bond_id: str = models.ForeignKey(Bond, on_delete=models.CASCADE)
    position: int = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.trader_id} {self.bond_id} {self.position}'

class EventLog(models.Model):
    """Schema for table `event_log`
    that records changes after a trade event
    """

    event_id: int = models.IntegerField(primary_key=True)
    desk_id: str = models.ForeignKey(Desk, on_delete=models.CASCADE)
    trader_id: str = models.ForeignKey(Trader, on_delete=models.CASCADE)
    book_id: str = models.ForeignKey(Book, on_delete=models.CASCADE)
    buy_sell: str = models.CharField(max_length=1)  # B or S
    quantity: int = models.IntegerField()
    bond_id: str = models.ForeignKey(Bond, on_delete=models.CASCADE)
    position: int = models.IntegerField()
    price: Decimal = models.DecimalField(max_digits=19, decimal_places=5)
    fx_rate: Decimal = models.DecimalField(max_digits=19, decimal_places=5)
    value: Decimal = models.DecimalField(
        max_digits=19, decimal_places=5
    )  # Net value of buy/sell. Always in USX.
    cash: Decimal = models.DecimalField(
        max_digits=19, decimal_places=5
    )  # Cash at Desk. Always in USX.

    def __str__(self):
        return f'{self.event_id} {self.desk_id} {self.trader_id} \
            {self.book_id} {self.buy_sell} {self.quantity} {self.bond_id} \
            {self.position} {self.price} {self.fx_rate} {self.value} \
            {self.cash}'

    def get_net_value(self):
        """Returns net value of the trade event."""
        if self.quantity and self.price and self.fx_rate:
            return round(self.quantity * (self.price / self.fx_rate), 2)
        raise ValueError('NV cannot be calculated')

class EventExceptionLog(models.Model):
    """Schema for table `event_exception_log`
    that records exceptions raised during a trade event
    """
    class TradeExceptionEnum(models.TextChoices):
        """Enum of names of trade exceptions."""
        INSUFFICIENT_CASH = 'INSUFFICIENT_CASH'
        BOND_NOT_FOUND = 'BOND_NOT_FOUND'
    event_id: int = models.IntegerField(primary_key=True)
    exception_name: str = models.CharField(
        max_length=20, choices=TradeExceptionEnum.choices
    )

    def __str__(self):
        return f'{self.event_id} {self.exception_name}'
