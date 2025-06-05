from django.urls import path
from . import views

urlpatterns = [
    path('corrigir/', views.corrigir_redacao, name='corrigir_redacao'),
    path('', views.formulario_redacao_view, name='formulario_redacao'), # Opcional: se você quiser que o Django sirva o HTML
]