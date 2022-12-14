# Generated by Django 4.0.4 on 2022-08-01 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0017_remove_item_igv_alter_historicalpurchase_igv_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpurchase',
            name='igv',
            field=models.IntegerField(default=0, verbose_name='igv'),
        ),
        migrations.AlterField(
            model_name='historicalpurchase',
            name='total',
            field=models.IntegerField(default=0, verbose_name='total'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='igv',
            field=models.IntegerField(default=0, verbose_name='igv'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='total',
            field=models.IntegerField(default=0, verbose_name='total'),
        ),
    ]
