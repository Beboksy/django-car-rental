from django.contrib import admin
from .models import UserProfile, Samochod, Zamowienie, Newsletter, Promocja


# Zarejestruj model w panelu admina
admin.site.register(UserProfile)


@admin.register(Samochod)
class SamochodAdmin(admin.ModelAdmin):
    list_display = ('numer_rejestracyjny', 'marka', 'model', 'cena', 'skrzynia', 'rodzaj_silnika', 'pojemnosc_silnika', 'moc', 'przebieg', 'rocznik', 'pojemnosc_bagaznika')
    search_fields = ('numer_rejestracyjny', 'marka', 'model')

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_subscribed')  # Wyświetlane kolumny w panelu admina
    search_fields = ('email',)  # Pole wyszukiwania po e-mailu
    list_filter = ('date_subscribed',)  # Możliwość filtrowania po dacie
    ordering = ('-date_subscribed',)  # Sortowanie od najnowszych subskrypcji


@admin.register(Zamowienie)
class ZamowienieAdmin(admin.ModelAdmin):
    list_display = ('id_zamowienia', 'uzytkownik', 'samochod', 'od_kiedy', 'do_kiedy', 'laczny_koszt')
    readonly_fields = ('imie', 'nazwisko', 'marka', 'model')

    def is_active_display(self, obj):
        return obj.is_active()
    is_active_display.short_description = "Aktywne"
    is_active_display.boolean = True

@admin.register(Promocja)
class PromocjaAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'procent_znizki', 'marka', 'model')  # Wyświetlanie w panelu admina
    search_fields = ('nazwa', 'marka', 'model')  # Możliwość wyszukiwania
    list_filter = ('marka', 'model')  # Filtrowanie po marce i modelu

