from django.urls import path
from . import views

# Nombre del espacio de nombres para usar en templates como {% url 'tienda:index' %}
app_name = 'tienda' 

urlpatterns = [
    # --- Rutas para las Vistas (Frontend) ---
    # Usamos las funciones que definiste en views.py
    path('', views.index, name='index'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('producto/<int:pk>/', views.detalle_producto, name='detalle_producto'),
    path('solicitar/', views.solicitar_pedido, name='solicitar_pedido'),
    path('pedido-exitoso/', views.pedido_exitoso, name='pedido_exitoso'),
    path('seguimiento/<str:token>/', views.seguimiento_pedido, name='seguimiento_pedido'),
]