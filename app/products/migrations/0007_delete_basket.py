# Generated by Django 4.1.7 on 2023-04-10 11:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_basket'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Basket',
        ),
    ]
