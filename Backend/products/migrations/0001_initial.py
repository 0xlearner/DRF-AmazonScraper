# Generated by Django 3.0.6 on 2022-02-05 11:34

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.URLField(max_length=500)),
                ('asin', models.CharField(max_length=100, unique=True)),
                ('price', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
                ('rating', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('review_count', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('title', models.CharField(max_length=250)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.Category')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.Seller')),
            ],
        ),
    ]
