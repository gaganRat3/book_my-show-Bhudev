from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_form, name='landing_form'),
    path('events/', views.event_list, name='event_list'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('add/', views.add_event, name='add_event'),
    path('event/<int:event_id>/seats/', views.seat_selection, name='seat_selection'),
    path('payment/', views.payment, name='payment'),
]
