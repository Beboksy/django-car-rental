# Generated by Django 5.1.5 on 2025-02-07 17:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wypozyczalnia_samochodow_2', '0002_samochod'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Zamowienie',
            fields=[
                ('id_zamowienia', models.AutoField(primary_key=True, serialize=False)),
                ('od_kiedy', models.DateField()),
                ('do_kiedy', models.DateField()),
                ('imie', models.CharField(editable=False, max_length=30)),
                ('nazwisko', models.CharField(editable=False, max_length=30)),
                ('marka', models.CharField(editable=False, max_length=50)),
                ('model', models.CharField(editable=False, max_length=50)),
                ('cena_za_dzien', models.DecimalField(decimal_places=2, editable=False, max_digits=10)),
                ('ilosc_dni', models.IntegerField(default=1, editable=False)),
                ('laczny_koszt', models.DecimalField(decimal_places=2, editable=False, max_digits=10)),
                ('rezerwacja_aktywna', models.BooleanField(default=False, editable=False)),
                ('samochod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wypozyczalnia_samochodow_2.samochod')),
                ('uzytkownik', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
        ),
    ]
