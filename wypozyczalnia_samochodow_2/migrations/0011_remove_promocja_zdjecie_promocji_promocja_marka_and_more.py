# Generated by Django 5.1.5 on 2025-02-09 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wypozyczalnia_samochodow_2', '0010_alter_promocja_samochod_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promocja',
            name='zdjecie_promocji',
        ),
        migrations.AddField(
            model_name='promocja',
            name='marka',
            field=models.CharField(blank=True, help_text='Marka, do której odnosi się promocja (opcjonalnie)', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='promocja',
            name='model',
            field=models.CharField(blank=True, help_text='Model, do którego odnosi się promocja (opcjonalnie)', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='promocja',
            name='zdjecie',
            field=models.ImageField(default='promocje_zdjecia/default.png', upload_to='promocje_zdjecia/'),
        ),
        migrations.AlterField(
            model_name='promocja',
            name='nazwa',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='promocja',
            name='procent_znizki',
            field=models.DecimalField(decimal_places=2, help_text='Procentowa zniżka na wynajem (np. 10.00 = 10%)', max_digits=5),
        ),
        migrations.DeleteModel(
            name='Promocja_Samochod',
        ),
    ]
