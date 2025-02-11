"""
URL configuration for wypozyczalnia_samochodow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# Wypozyczalnia_samochodow/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from wypozyczalnia_samochodow_2.views import (
    index_view, about_us_view, contact_view, fleet_view,
    offers_view, terms_view, login_view, register_view,
    profile_view, order_history_view, logout_view, check_username_view,
    book_car_view, reservations_view, newsletter_signup
)


urlpatterns = [
    path('admin/', admin.site.urls),

    # Ścieżki do poszczególnych stron:
    path('', index_view, name='index'),                        # http://127.0.0.1:8000/
    path('about-us./', about_us_view, name='about-us'),         # http://127.0.0.1:8000/about-us/
    path('contact/', contact_view, name='contact'),
    path('fleet/', fleet_view, name='fleet'),
    path('promotions/', offers_view, name='offers'),
    path('terms/', terms_view, name='terms'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path('order_history/', order_history_view, name='order_history'),
    path('logout/', logout_view, name='logout'),
    path('check-username', check_username_view, name='check_username'),
    path('book-car/', book_car_view, name='book_car'),
    path('reservations/', reservations_view, name='reservations'),
    path('newsletter_signup/', newsletter_signup, name='newsletter_signup'),
]


# Dodanie obsługi plików multimedialnych
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


