# Generated by Django 3.1 on 2020-10-01 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auto_20201001_1714'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='auction_winner_id',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]