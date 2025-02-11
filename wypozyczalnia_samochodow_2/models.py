import datetime

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils.timezone import now
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
     return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Create your models here.

class Samochod(models.Model):
    SKRZYNIA_BIEGOW = [
        ('A', 'Automatyczna'),
        ('M', 'Manualna'),
    ]

    RODZAJ_SILNIKA = [
        ('Benzyna', 'Benzyna'),
        ('Diesel', 'Diesel'),
        ('Elektryczny', 'Elektryczny'),
        ('Hybrydowy', 'Hybrydowy'),
    ]

    numer_rejestracyjny = models.CharField(max_length=15, primary_key=True, unique=True)
    marka = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    ilosc_miejsc = models.IntegerField()
    pojemnosc_bagaznika = models.FloatField(help_text="W litrach")
    liczba_drzwi = models.IntegerField()
    skrzynia = models.CharField(max_length=1, choices=SKRZYNIA_BIEGOW)
    cena = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cena za dzień wynajmu w złotówkach")
    zdjecie_samochodu = models.ImageField(upload_to='samochody_zdjecia/')
    opis = models.TextField(blank=True, help_text="Krótki opis samochodu")
    rodzaj_silnika = models.CharField(max_length=15, choices=RODZAJ_SILNIKA, default='Benzyna')
    pojemnosc_silnika = models.FloatField(help_text="Pojemność silnika w litrach", default=0)
    moc = models.IntegerField(help_text="Moc silnika w KM", default=0)
    przebieg = models.IntegerField(help_text="Przebieg w kilometrach", default=0)
    rocznik = models.IntegerField(help_text="Rok produkcji", default=datetime.today().year)

    def __str__(self):
        return f"{self.marka} {self.model} ({self.numer_rejestracyjny})"

    class Meta:
        verbose_name = "Samochod"
        verbose_name_plural = "Samochody"


# class Zamowienie(models.Model):
#     id_zamowienia = models.AutoField(primary_key=True)
#     uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE, to_field="username")  # Klucz obcy do auth_user
#     samochod = models.ForeignKey('Samochod', on_delete=models.CASCADE, to_field="numer_rejestracyjny")  # Klucz obcy do Samochod
#     od_kiedy = models.DateField()
#     do_kiedy = models.DateField()
#
#     # Dane użytkownika pobierane z auth_user
#     imie = models.CharField(max_length=30, editable=False)
#     nazwisko = models.CharField(max_length=30, editable=False)
#
#     # Dane samochodu pobierane z tabeli Samochod
#     marka = models.CharField(max_length=50, editable=False)
#     model = models.CharField(max_length=50, editable=False)
#     cena_za_dzien = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
#
#     # Pola obliczeniowe
#     ilosc_dni = models.IntegerField(default=1, editable=False)
#     laczny_koszt = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
#
#     # Czy rezerwacja jest aktywna
#     rezerwacja_aktywna = models.BooleanField(default=False, editable=False)
#
#     def clean(self):
#         """Sprawdzenie, czy samochód nie jest już zarezerwowany w podanym terminie."""
#         if self.samochod and self.od_kiedy and self.do_kiedy:
#             kolidujace_zamowienia = Zamowienie.objects.filter(
#                 samochod=self.samochod,
#                 do_kiedy__gte=self.od_kiedy,  # Sprawdza czy rezerwacja kończy się po dacie startowej nowej rezerwacji
#                 od_kiedy__lte=self.do_kiedy   # Sprawdza czy rezerwacja zaczyna się przed datą końcową nowej rezerwacji
#             ).exclude(id_zamowienia=self.id_zamowienia)  # Wyklucza aktualne zamówienie (w przypadku edycji)
#
#             if kolidujace_zamowienia.exists():
#                 raise ValidationError("Samochód jest już zarezerwowany w tym terminie.")
#         super().clean()
#         if self.laczny_koszt is None or self.laczny_koszt <= 0:
#             raise ValidationError("Łączny koszt musi być większy od 0.")
#
#     def save(self, *args, **kwargs):
#         """Automatyczne obliczanie wartości przed zapisaniem zamówienia"""
#         self.clean()  # Sprawdzenie warunków walidacji przed zapisem
#
#         if self.od_kiedy and self.do_kiedy:
#             # Zapewniamy, że daty są instancjami `date`
#             if isinstance(self.od_kiedy, datetime):
#                 self.od_kiedy = self.od_kiedy.date()
#             if isinstance(self.do_kiedy, datetime):
#                 self.do_kiedy = self.do_kiedy.date()
#
#             self.ilosc_dni = (self.do_kiedy - self.od_kiedy).days
#             if self.ilosc_dni < 1:
#                 self.ilosc_dni = 1  # Minimalna rezerwacja to 1 dzień
#
#         # Pobieranie danych z użytkownika
#         if self.uzytkownik:
#             self.imie = self.uzytkownik.first_name
#             self.nazwisko = self.uzytkownik.last_name
#
#         # Pobieranie danych z samochodu
#         if self.samochod:
#             self.marka = self.samochod.marka
#             self.model = self.samochod.model
#             self.cena_za_dzien = self.samochod.cena
#             self.laczny_koszt = self.ilosc_dni * self.cena_za_dzien
#
#         super().save(*args, **kwargs)
#
#     def is_active(self):
#         """Sprawdza, czy zamówienie jest aktywne na podstawie aktualnej daty"""
#         dzisiaj = now().date()
#         return self.od_kiedy <= dzisiaj <= self.do_kiedy
#
#     def __str__(self):
#         return f"Zamówienie {self.id_zamowienia}: {self.uzytkownik.username} - {self.marka} {self.model}"
#
#     class Meta:
#         verbose_name = "Zamowienie"
#         verbose_name_plural = "Zamowienia"


class Zamowienie(models.Model):
    id_zamowienia = models.AutoField(primary_key=True)
    uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE, to_field="username")  # Klucz obcy do auth_user
    samochod = models.ForeignKey('Samochod', on_delete=models.CASCADE, to_field="numer_rejestracyjny")  # Klucz obcy do Samochod
    od_kiedy = models.DateField()
    do_kiedy = models.DateField()

    # Dane użytkownika pobierane z auth_user
    imie = models.CharField(max_length=30, editable=False)
    nazwisko = models.CharField(max_length=30, editable=False)

    # Dane samochodu pobierane z tabeli Samochod
    marka = models.CharField(max_length=50, editable=False)
    model = models.CharField(max_length=50, editable=False)
    cena_za_dzien = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    # Pola obliczeniowe
    ilosc_dni = models.IntegerField(default=1, editable=False)
    laczny_koszt = models.DecimalField(max_digits=10, decimal_places=2)  # Ustawiamy na edytowalne

    # Czy rezerwacja jest aktywna
    rezerwacja_aktywna = models.BooleanField(default=False, editable=False)

    def clean(self):
        """Sprawdzenie, czy samochód nie jest już zarezerwowany w podanym terminie."""
        if self.samochod and self.od_kiedy and self.do_kiedy:
            kolidujace_zamowienia = Zamowienie.objects.filter(
                samochod=self.samochod,
                do_kiedy__gte=self.od_kiedy,  # Sprawdza czy rezerwacja kończy się po dacie startowej nowej rezerwacji
                od_kiedy__lte=self.do_kiedy   # Sprawdza czy rezerwacja zaczyna się przed datą końcową nowej rezerwacji
            ).exclude(id_zamowienia=self.id_zamowienia)  # Wyklucza aktualne zamówienie (w przypadku edycji)

            if kolidujace_zamowienia.exists():
                raise ValidationError("Samochód jest już zarezerwowany w tym terminie.")

        if self.laczny_koszt is None or self.laczny_koszt <= 0:
            raise ValidationError("Łączny koszt musi być większy od 0.")

    def save(self, *args, **kwargs):
        """Zapisuje zamówienie bez automatycznego obliczania wartości."""
        self.clean()  # Sprawdzenie warunków walidacji przed zapisem

        # Pobieranie danych z użytkownika
        if self.uzytkownik:
            self.imie = self.uzytkownik.first_name
            self.nazwisko = self.uzytkownik.last_name

        # Pobieranie danych z samochodu
        if self.samochod:
            self.marka = self.samochod.marka
            self.model = self.samochod.model
            self.cena_za_dzien = self.samochod.cena

        super().save(*args, **kwargs)

    def is_active(self):
        """Sprawdza, czy zamówienie jest aktywne na podstawie aktualnej daty"""
        dzisiaj = now().date()
        return self.od_kiedy <= dzisiaj <= self.do_kiedy

    def __str__(self):
        return f"Zamówienie {self.id_zamowienia}: {self.uzytkownik.username} - {self.marka} {self.model}"

    class Meta:
        verbose_name = "Zamowienie"
        verbose_name_plural = "Zamowienia"




class Newsletter(models.Model):
    email = models.EmailField(unique=True)  # E-mail musi być unikalny
    date_subscribed = models.DateTimeField(auto_now_add=True)  # Data subskrypcji

    def __str__(self):
        return self.email
    class Meta:
        verbose_name = "Newsletter"
        verbose_name_plural = "Newsletter'y"


class Promocja(models.Model):
    nazwa = models.CharField(max_length=100, primary_key=True)  # Klucz główny
    opis = models.TextField()
    zdjecie = models.ImageField(upload_to='promocje_zdjecia/', default="promocje_zdjecia/default.png")
    procent_znizki = models.DecimalField(max_digits=5, decimal_places=2,
                                         help_text="Procentowa zniżka na wynajem (np. 10.00 = 10%)")

    # Nowe pola
    marka = models.CharField(max_length=50, blank=True, null=True,
                             help_text="Marka, do której odnosi się promocja (opcjonalnie)")
    model = models.CharField(max_length=50, blank=True, null=True,
                             help_text="Model, do którego odnosi się promocja (opcjonalnie)")

    def __str__(self):
        return f"{self.nazwa} - {self.procent_znizki}%"

    class Meta:
        verbose_name = "Promocja"
        verbose_name_plural = "Promocje"
