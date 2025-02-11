from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from .models import Samochod, Zamowienie, Newsletter, Promocja
from datetime import datetime, timedelta, date
from django.views.decorators.cache import cache_control
import re


# Create your views here.


@user_passes_test(lambda u: u.is_superuser)
def reservations_view(request):
    # Aktualizacja statusów zamówień
    aktualizuj_statusy()

    # Pobieranie filtrów z zapytania
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    car = request.GET.get('car', '')
    user = request.GET.get('user', '')
    status = request.GET.get('status', '')

    # Pobieranie wszystkich rezerwacji
    reservations = Zamowienie.objects.all().order_by('od_kiedy')

    # Filtrowanie po dacie
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        reservations = reservations.filter(od_kiedy__gte=start_date)
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        reservations = reservations.filter(do_kiedy__lte=end_date)

    # Filtrowanie po samochodzie
    if car:
        reservations = reservations.filter(samochod__numer_rejestracyjny=car)

    # Filtrowanie po użytkowniku
    if user:
        reservations = reservations.filter(uzytkownik__username=user)

    # Filtrowanie po statusie
    if status == 'active':
        reservations = reservations.filter(rezerwacja_aktywna=True)
    elif status == 'not_active':
        reservations = reservations.filter(rezerwacja_aktywna=False).exclude(uzytkownik__username="admin")
    elif status == 'technical_break':
        reservations = reservations.filter(uzytkownik__username="admin")

    # Obliczanie łącznego zysku
    total_earnings = sum([r.laczny_koszt for r in reservations if r.uzytkownik.username.lower() != "admin"])

    # Pobieranie unikalnych samochodów i użytkowników do list rozwijanych
    available_cars = Zamowienie.objects.values_list('samochod__numer_rejestracyjny', 'samochod__marka', 'samochod__model').distinct()
    available_users = Zamowienie.objects.values_list('uzytkownik__username', flat=True).distinct()

    # Renderowanie szablonu
    return render(request, 'reservations.html', {
        'reservations': reservations,
        'total_earnings': total_earnings,
        'available_cars': available_cars,
        'available_users': available_users,
    })


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def profile_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Walidacja numeru telefonu (może zawierać tylko cyfry i opcjonalnie + na początku)
        phone_regex = re.compile(r'^\+?\d{9,15}$')
        if not phone_regex.match(phone_number):
            messages.error(request, "Niepoprawny numer telefonu! Podaj poprawny format.")
            return redirect('profile')

        # Aktualizacja danych użytkownika
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()

        # Aktualizacja danych profilu użytkownika
        user_profile = request.user.userprofile
        user_profile.phone_number = phone_number
        user_profile.save()

        if password1 and password2:
            if password1 == password2:
                request.user.set_password(password1)
                request.user.save()
                messages.success(request, "Hasło zostało zmienione.")
            else:
                messages.error(request, "Hasła nie są identyczne.")


        messages.success(request, "Twoje dane zostały pomyślnie zaktualizowane.")
        return redirect('profile')

    return render(request, 'profile.html')



@login_required
def book_car_view(request):
    uzytkownik = request.user

    if request.method == "POST":
        print("DEBUG POST:", request.POST)  # Sprawdzenie, jakie dane są przesyłane

        numer_rejestracyjny = request.POST.get("numer_rejestracyjny")
        start_date = request.POST.get("od_kiedy")
        end_date = request.POST.get("do_kiedy")
        laczny_koszt = request.POST.get("laczny_koszt", "0 zł").replace(" zł", "")

        # Pobierz samochód lub zwróć 404
        samochod = get_object_or_404(Samochod, numer_rejestracyjny=numer_rejestracyjny)

        # Pobierz dostępne promocje dla samochodu
        promocje = Promocja.objects.all()
        wybrana_promocja = None

        # Szukamy promocji dla konkretnego modelu
        for promocja in promocje:
            if promocja.marka == samochod.marka and promocja.model == samochod.model:
                wybrana_promocja = promocja
                break

        # Jeśli brak dopasowania modelu, sprawdzamy tylko markę
        if not wybrana_promocja:
            for promocja in promocje:
                if promocja.marka == samochod.marka and not promocja.model:
                    wybrana_promocja = promocja
                    break

        # Ustawienie ceny promocyjnej, jeśli obowiązuje
        if wybrana_promocja:
            samochod.obnizona_cena = round(
                samochod.cena - (samochod.cena * (wybrana_promocja.procent_znizki / 100)), 2
            )
        else:
            samochod.obnizona_cena = None

        # Pobranie listy zajętych dat dla tego samochodu
        zajete_zakresy = Zamowienie.objects.filter(samochod=samochod).values("od_kiedy", "do_kiedy")
        zajete_daty = []
        for zakres in zajete_zakresy:
            start = zakres["od_kiedy"]
            end = zakres["do_kiedy"]
            while start <= end:
                zajete_daty.append(start.strftime("%Y-%m-%d"))
                start += timedelta(days=1)

        # Walidacja poprawności danych wejściowych
        try:
            if not start_date or not end_date:
                return render(request, 'book_car.html', {
                    'samochod': samochod,
                    'uzytkownik': request.user,
                    'zajete_daty': zajete_daty,
                    'error': 'Nie wybrano wszystkich dat rezerwacji.',
                })

            # Konwersja dat
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            # Sprawdzenie kolejności dat
            if end_date < start_date:
                return render(request, 'book_car.html', {
                    'samochod': samochod,
                    'uzytkownik': request.user,
                    'zajete_daty': zajete_daty,
                    'error': 'Data zakończenia rezerwacji nie może być wcześniejsza niż data rozpoczęcia.',
                })

            # Sprawdzenie kolizji z już istniejącymi rezerwacjami
            for zajeta in zajete_daty:
                zajeta_date = datetime.strptime(zajeta, "%Y-%m-%d").date()
                if start_date <= zajeta_date <= end_date:
                    return render(request, 'book_car.html', {
                        'samochod': samochod,
                        'uzytkownik': request.user,
                        'zajete_daty': zajete_daty,
                        'error': 'Wybrany termin jest już zajęty. Wybierz inne daty.',
                    })

        except ValueError:
            return render(request, 'book_car.html', {
                'samochod': samochod,
                'uzytkownik': request.user,
                'zajete_daty': zajete_daty,
                'error': 'Błąd formatu daty! Wybierz datę ponownie.',
            })

        # Obliczenie liczby dni rezerwacji
        ilosc_dni = (end_date - start_date).days + 1

        # Pobranie ceny końcowej (z promocją, jeśli dotyczy)
        cena_za_dzien = samochod.obnizona_cena if samochod.obnizona_cena else samochod.cena

        # Obliczenie całkowitego kosztu
        try:
            laczny_koszt = float(laczny_koszt)
            if laczny_koszt <= 0:
                return render(request, 'book_car.html', {
                    'samochod': samochod,
                    'uzytkownik': request.user,
                    'zajete_daty': zajete_daty,
                    'error': 'Łączny koszt musi być większy niż 0 zł.',
                })
        except ValueError:
            return render(request, 'book_car.html', {
                'samochod': samochod,
                'uzytkownik': request.user,
                'zajete_daty': zajete_daty,
                'error': 'Nieprawidłowy format ceny.',
            })

        # Utworzenie nowego zamówienia
        zamowienie = Zamowienie.objects.create(
            uzytkownik=uzytkownik,
            samochod=samochod,
            od_kiedy=start_date,
            do_kiedy=end_date,
            ilosc_dni=ilosc_dni,
            laczny_koszt=laczny_koszt,
            marka=samochod.marka,
            model=samochod.model,
            cena_za_dzien=cena_za_dzien,
            rezerwacja_aktywna=True,
        )

        # Zapisanie zamówienia w bazie
        zamowienie.save()

        # Przekierowanie na stronę z potwierdzeniem rezerwacji
        return redirect('order_history')

    else:
        # Obsługa GET (np. gdy wchodzisz bezpośrednio na /book_car?nr=XYZ)
        numer_rejestracyjny = request.GET.get("nr")
        if not numer_rejestracyjny:
            return redirect('fleet')

        samochod = get_object_or_404(Samochod, numer_rejestracyjny=numer_rejestracyjny)

        # Pobranie zajętych dat
        zajete_zakresy = Zamowienie.objects.filter(samochod=samochod).values("od_kiedy", "do_kiedy")
        zajete_daty = []
        for zakres in zajete_zakresy:
            start = zakres["od_kiedy"]
            end = zakres["do_kiedy"]
            while start <= end:
                zajete_daty.append(start.strftime("%Y-%m-%d"))
                start += timedelta(days=1)

        return render(request, 'book_car.html', {
            'samochod': samochod,
            'uzytkownik': uzytkownik,
            'zajete_daty': zajete_daty,
        })


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')  # Przekierowanie po zalogowaniu
        else:
            messages.error(request, "Błędna nazwa użytkownika lub hasło")  # Komunikat o błędzie

    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatyczne logowanie po rejestracji
            return redirect('index')  # Przekierowanie na stronę główną
        else:
            # Formularz jest nieprawidłowy, więc zwracamy z powrotem do szablonu
            # ten sam formularz z błędami, aby je wyświetlić
            return render(request, 'register.html', {'form': form})
    else:
        # Gdy wchodzimy na stronę GET-em, po prostu wyświetlamy pusty formularz
        form = CustomUserCreationForm()
        return render(request, 'register.html', {'form': form})

def check_username_view(request):
    username = request.GET.get('username', '')
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})

def logout_view(request):
    logout(request)
    return redirect('index')

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(required=True, label="Imię", max_length=30)
    last_name = forms.CharField(required=True, label="Nazwisko", max_length=30)
    email = forms.EmailField(required=True, label="Adres email")
    phone_number = forms.CharField(required=True, label="Numer telefonu", max_length=15)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {
            'username': 'Nazwa użytkownika',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].help_text = None

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")

        # Sprawdzenie czy numer ma tylko cyfry i opcjonalnie + na początku
        if not re.match(r'^\+?\d{9,15}$', phone_number):
            raise forms.ValidationError("Numer telefonu powinien zawierać od 9 do 15 cyfr i może zaczynać się od '+'.")

        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            user.userprofile.phone_number = self.cleaned_data['phone_number']
            user.userprofile.save()

        return user



@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_history_view(request):
    aktualizuj_statusy()
    user = request.user
    order_history = Zamowienie.objects.filter(uzytkownik=user).order_by('-od_kiedy')
    return render(request, 'order_history.html', {'order_history': order_history})


def aktualizuj_statusy():
    dzisiaj = date.today()
    zamowienia = Zamowienie.objects.all()

    for zamowienie in zamowienia:
        if zamowienie.od_kiedy <= dzisiaj <= zamowienie.do_kiedy:
            zamowienie.rezerwacja_aktywna = True
        else:
            zamowienie.rezerwacja_aktywna = False
        zamowienie.save()

def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        # Treść wiadomości z e-mail użytkownika
        email_body = f"Imię i nazwisko: {name}\n"
        email_body += f"E-mail: {email}\n\n"
        email_body += f"Wiadomość:\n{message}"

        # Wyślij email
        send_mail(
            subject=f"Kontakt od {name}",
            message=email_body,
            from_email="no-reply@yourdomain.com",  # Domyślny e-mail nadawcy
            recipient_list=["bartoszkapustka15@gmail.com"],
        )

        messages.success(request, "Wiadomość została wysłana!")
        return redirect("contact")  # Przekierowanie na stronę kontaktową

    return render(request, "contact.html")


from django.shortcuts import render
from .models import Promocja, Samochod

def index_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        email_body = f"Imię i nazwisko: {name}\nE-mail: {email}\n\nWiadomość:\n{message}"

        send_mail(
            subject=f"Kontakt od {name}",
            message=email_body,
            from_email="no-reply@yourdomain.com",
            recipient_list=["bartoszkapustka15@gmail.com"],
        )

        messages.success(request, "Wiadomość została wysłana!")
        return redirect("index")

    # Pobieramy maksymalnie 3 losowe promocje
    promocje = Promocja.objects.all()[:3]

    return render(request, "index.html", {"promocje": promocje})


def newsletter_signup(request):
    if request.method == "POST":
        email = request.POST.get("email")  # Pobranie e-maila z formularza
        if email:
            # Sprawdzenie, czy email już istnieje w bazie
            if not Newsletter.objects.filter(email=email).exists():
                # Zapis do bazy danych
                Newsletter.objects.create(email=email)

                # Wysłanie maila potwierdzającego
                send_mail(
                    subject="Newsletter - Wypożyczalnia",
                    message="Pomyślnie zapisano Cię do Newslettera.",
                    from_email="no-reply@yourdomain.com",
                    recipient_list=[email],
                )

                messages.success(request, "Zostałeś zapisany do Newslettera!")
            else:
                messages.info(request, "Ten e-mail jest już zapisany do Newslettera.")
        else:
            messages.error(request, "Podaj poprawny adres e-mail.")

    return redirect(request.META.get("HTTP_REFERER", "/"))




def fleet_view(request):

    samochody = Samochod.objects.all()
    promocje = Promocja.objects.all()

    # Dodaj do każdego samochodu atrybut 'obniżona_cena', nawet jeśli nie ma promocji
    for samochod in samochody:
        samochod.obnizona_cena = None  # Domyślnie brak promocji
        wybrana_promocja = None

        # Najpierw szukamy promocji pasującej zarówno marką, jak i modelem
        for promocja in promocje:
            if samochod.marka == promocja.marka and samochod.model == promocja.model:
                wybrana_promocja = promocja
                break  # Znaleziono idealną promocję

        # Jeśli nie znaleziono promocji dla konkretnego modelu, szukamy promocji dla samej marki
        if not wybrana_promocja:
            for promocja in promocje:
                if samochod.marka == promocja.marka and not promocja.model:
                    wybrana_promocja = promocja
                    break  # Znaleziono promocję dla marki

        # Jeśli znaleziono jakąkolwiek promocję, obliczamy obniżoną cenę
        if wybrana_promocja:
            samochod.obnizona_cena = round(
                samochod.cena - (samochod.cena * (wybrana_promocja.procent_znizki / 100)), 2
            )

    return render(request, "fleet.html", {"samochody": samochody})


def offers_view(request):
    promocje = Promocja.objects.all()  # Pobieramy wszystkie promocje z bazy danych
    return render(request, 'offers.html', {'promocje': promocje})

def terms_view(request):
    return render(request, 'terms.html')
def about_us_view(request):
    return render(request, 'about-us.html')
