# Generated by Django 4.0.6 on 2022-07-15 05:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bond',
            fields=[
                ('bond_id', models.CharField(max_length=6, primary_key=True, serialize=False)),
                ('price', models.DecimalField(blank=True, decimal_places=5, max_digits=19, null=True)),
                ('initial_price', models.DecimalField(blank=True, decimal_places=5, max_digits=19, null=True)),
            ],
            options={
                'ordering': ['bond_id'],
            },
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('book_id', models.CharField(max_length=5, primary_key=True, serialize=False)),
            ],
            options={
                'ordering': ['trader', 'book_id'],
            },
        ),
        migrations.CreateModel(
            name='Desk',
            fields=[
                ('desk_id', models.CharField(max_length=5, primary_key=True, serialize=False)),
                ('cash', models.DecimalField(decimal_places=5, max_digits=19)),
            ],
            options={
                'ordering': ['desk_id'],
            },
        ),
        migrations.CreateModel(
            name='FX',
            fields=[
                ('currency_id', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('rate', models.DecimalField(decimal_places=5, max_digits=19)),
                ('initial', models.DecimalField(decimal_places=5, max_digits=19)),
            ],
            options={
                'ordering': ['currency_id'],
            },
        ),
        migrations.CreateModel(
            name='Trader',
            fields=[
                ('trader_id', models.CharField(max_length=8, primary_key=True, serialize=False)),
                ('desk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.desk')),
            ],
            options={
                'ordering': ['desk', 'trader_id'],
            },
        ),
        migrations.CreateModel(
            name='PriceEventLog',
            fields=[
                ('event_id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('price', models.DecimalField(decimal_places=5, max_digits=19)),
                ('bond', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.bond')),
            ],
        ),
        migrations.CreateModel(
            name='FxEventLog',
            fields=[
                ('event_id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('rate', models.DecimalField(decimal_places=5, max_digits=19)),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.fx')),
            ],
        ),
        migrations.CreateModel(
            name='EventLog',
            fields=[
                ('event_id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('buy_sell', models.CharField(max_length=4)),
                ('quantity', models.PositiveIntegerField()),
                ('position', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=5, max_digits=19)),
                ('fx_rate', models.DecimalField(decimal_places=5, max_digits=19)),
                ('value', models.DecimalField(decimal_places=5, max_digits=19)),
                ('cash', models.DecimalField(decimal_places=5, max_digits=19)),
                ('bond', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.bond')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.book')),
                ('desk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.desk')),
                ('trader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.trader')),
            ],
        ),
        migrations.CreateModel(
            name='EventExceptionLog',
            fields=[
                ('event_id', models.IntegerField(primary_key=True, serialize=False)),
                ('buy_sell', models.CharField(max_length=4)),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.DecimalField(blank=True, decimal_places=5, max_digits=19, null=True)),
                ('exclusion_type', models.CharField(choices=[('NO_MARKET_PRICE', 'No Market Price'), ('CASH_OVERLIMIT', 'Cash Overlimit'), ('QUANTITY_OVERLIMIT', 'Quantity Overlimit')], max_length=20)),
                ('bond', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.bond')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.book')),
                ('desk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.desk')),
                ('trader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.trader')),
            ],
        ),
        migrations.AddField(
            model_name='book',
            name='trader',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.trader'),
        ),
        migrations.CreateModel(
            name='BondRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveIntegerField(default=0)),
                ('bond', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.bond')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.book')),
                ('trader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.trader')),
            ],
            options={
                'ordering': ['trader', 'book', 'bond'],
            },
        ),
        migrations.AddField(
            model_name='bond',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.fx'),
        ),
    ]
