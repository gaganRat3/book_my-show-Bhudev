"""
URL configuration for bookmyshow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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



from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from core.views import landing_form, seat_selection, payment, booking_report, payment_confirmation

urlpatterns = [
    path('', landing_form, name='landing_form'),
    path('seats/', seat_selection, name='seat_selection'),
    path('payment/', payment, name='payment'),
    path('admin/', admin.site.urls),
    path('admin/report/', booking_report, name='booking_report'),
    path('payment/confirmation/', payment_confirmation, name='payment_confirmation'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
