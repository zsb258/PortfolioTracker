"""Module specifying the models of the application."""

from decimal import Decimal

from django.db import models


class FX(models.Model):
    """Schema for table `FX`. Stores most updated exchange rates."""
    currency_id: str = models.CharField(max_length=3, primary_key=True)
    rate: Decimal = models.DecimalField(max_digits=19, decimal_places=5)
    initial: Decimal = models.DecimalField(max_digits=19, decimal_places=5)

    class Meta:
        ordering = ['currency_id']

    def __str__(self):
        return f'{self.currency_id} {self.rate}'

class Bond(models.Model):
    """Schema for table `bond`. Stores most updated bond data."""
    bond_id: str = models.CharField(max_length=6, primary_key=True)
    currency: str = models.ForeignKey(FX, on_delete=models.CASCADE)
    price: Decimal = models.DecimalField(
        max_digits=19, decimal_places=5, blank=True, null=True
    )
    initial_price: Decimal = models.DecimalField(
        max_digits=19, decimal_places=5, blank=True, null=True
    )

    class Meta:
        ordering = ['bond_id']

    def __str__(self):
        return f'{self.bond_id} uses:{self.currency}'

class Desk(models.Model):
    """Schema for table `desk`. Stores most updated desk data."""
    desk_id: str = models.CharField(max_length=5, primary_key=True)
    cash: Decimal = models.DecimalField(max_digits=19, decimal_places=5)

    class Meta:
        ordering = ['desk_id']

    def __str__(self):
        return f'{self.desk_id} ${self.cash}'

class Trader(models.Model):
    """Schema for table `trader`. Stores all bonds held."""
    trader_id: str = models.CharField(max_length=8, primary_key=True)
    desk: str = models.ForeignKey(Desk, on_delete=models.CASCADE)

    class Meta:
        ordering = ['desk', 'trader_id']

    def __str__(self):
        return f'{self.trader_id} from:{self.desk}'

class Book(models.Model):
    """Schema for table `book`. Each entry is "owned" by one Trader."""
    book_id: str = models.CharField(max_length=5, primary_key=True)
    trader: str = models.ForeignKey(Trader, on_delete=models.CASCADE)

    class Meta:
        ordering = ['trader', 'book_id']

    def __str__(self):
        return f'[{self.book_id}] under:[{self.trader}]'

class BondRecord(models.Model):
    """Schema for table `bonds_held`. Stores a bond held by a trader."""
    trader: str = models.ForeignKey(Trader, on_delete=models.CASCADE)
    book: str = models.ForeignKey(Book, on_delete=models.CASCADE)
    bond: str = models.ForeignKey(Bond, on_delete=models.CASCADE)
    position: int = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'by:[{self.trader}] bond:[{self.bond}] at:[{self.position}]'

class EventLog(models.Model):
    """Schema for table `event_log`
    that records changes after a trade event
    """

    event_id: int = models.PositiveIntegerField(primary_key=True)
    desk: str = models.ForeignKey(Desk, on_delete=models.CASCADE)
    trader: str = models.ForeignKey(Trader, on_delete=models.CASCADE)
    book: str = models.ForeignKey(Book, on_delete=models.CASCADE)
    buy_sell: str = models.CharField(max_length=4)  # `buy` or `sell`
    quantity: int = models.PositiveIntegerField()
    bond: str = models.ForeignKey(Bond, on_delete=models.CASCADE)
    position: int = models.PositiveIntegerField()
    price: Decimal = models.DecimalField(max_digits=19, decimal_places=5)
    fx_rate: Decimal = models.DecimalField(max_digits=19, decimal_places=5)
    value: Decimal = models.DecimalField(
        max_digits=19, decimal_places=5
    )  # Net value of single buy/sell. Always in USX.
    cash: Decimal = models.DecimalField(
        max_digits=19, decimal_places=5
    )  # Cash at Desk. Always in USX.

    def __str__(self):
        return f'{self.event_id} {self.desk} {self.trader} \
            {self.book} {self.buy_sell} {self.quantity} {self.bond} \
            {self.position} {self.price} {self.fx_rate} {self.value} \
            {self.cash}'

class FxEventLog(models.Model):
    """Schema for table `fx_event_log`
    that records fx changes after a market data event
    """

    event_id: int = models.PositiveIntegerField(primary_key=True)
    currency: str = models.ForeignKey(FX, on_delete=models.CASCADE)
    rate: Decimal = models.DecimalField(max_digits=19, decimal_places=5)

    def __str__(self):
        return f'FX {self.event_id} {self.currency} {self.rate}'

class PriceEventLog(models.Model):
    """Schema for table `fx_event_log`
    that records price changes after a market data event
    """

    event_id: int = models.PositiveIntegerField(primary_key=True)
    bond: str = models.ForeignKey(Bond, on_delete=models.CASCADE)
    price: Decimal = models.DecimalField(max_digits=19, decimal_places=5)

    def __str__(self):
        return f'Price {self.event_id} {self.bond} {self.price}'

class EventExceptionLog(models.Model):
    """Schema for table `event_exception_log`
    that records exceptions raised during a trade event
    """
    class TradeExceptionEnum(models.TextChoices):
        """Enum of names of trade exceptions."""
        NO_MARKET_PRICE = 'NO_MARKET_PRICE'
        CASH_OVERLIMIT = 'CASH_OVERLIMIT'
        QUANTITY_OVERLIMIT = 'QUANTITY_OVERLIMIT'

    event_id: int = models.IntegerField(primary_key=True)
    desk: str = models.ForeignKey(Desk, on_delete=models.CASCADE)
    trader: str = models.ForeignKey(Trader, on_delete=models.CASCADE)
    book: str = models.ForeignKey(Book, on_delete=models.CASCADE)
    buy_sell: str = models.CharField(max_length=4)  # `buy` or `sell`
    quantity: int = models.PositiveIntegerField()
    bond: str = models.ForeignKey(Bond, on_delete=models.CASCADE)
    price: Decimal = models.DecimalField(
        max_digits=19, decimal_places=5, blank=True, null=True
    )
    exclusion_type: str = models.CharField(
        max_length=20, choices=TradeExceptionEnum.choices
    )

    def __str__(self):
        return f'{self.event_id} boo{self.exclusion_type}'
