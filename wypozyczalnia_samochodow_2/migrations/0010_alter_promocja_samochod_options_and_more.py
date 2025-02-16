# Generated by Django 5.1.5 on 2025-02-09 23:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wypozyczalnia_samochodow_2', '0009_promocja_samochod'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='promocja_samochod',
            options={'verbose_name': 'Promocja dla samochodu', 'verbose_name_plural': 'Promocje dla samochodów'},
        ),
        migrations.AlterUniqueTogether(
            name='promocja_samochod',
            unique_together={('promocja', 'marka', 'model')},
        ),
        migrations.AlterField(
            model_name='promocja_samochod',
            name='marka',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='promocja_samochod',
            name='model',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.RemoveField(
            model_name='promocja_samochod',
            name='samochod',
        ),
    ]
