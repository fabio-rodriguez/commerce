# Generated by Django 3.1 on 2020-11-10 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20201001_1716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='img_url',
            field=models.CharField(default='https://lh3.googleusercontent.com/proxy/8oBcMJk52g4P-ZleBeYxqcHV4oiE_Z8Q1wDkPGs517WYpNwqMwBaOksB37bJQDgr7_fCs8OCxdn3mzkHDM674AMzLu-R_u2ngfIj85qcXQ9URwn2l84', max_length=256),
        ),
    ]