# Generated by Django 4.0.4 on 2022-08-01 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0016_historicalpurchase_igv_purchase_igv_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='igv',
        ),
        migrations.AlterField(
            model_name='historicalpurchase',
            name='igv',
            field=models.IntegerField(default=0, max_length=10, verbose_name='igv'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='igv',
            field=models.IntegerField(default=0, max_length=10, verbose_name='igv'),
        ),
    ]
