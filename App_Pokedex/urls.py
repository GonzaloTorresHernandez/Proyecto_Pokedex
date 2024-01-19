from django.urls import path
from . import views

urlpatterns = [path("", views.Home.as_view(), name='home'),
               path('Detalle-Pokemon/<int:id>', views.Detalle_Pokemon.as_view(), name='detalle-pokemon')]