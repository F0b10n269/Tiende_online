from django.urls import path
from .views import ReporteView
from . import views

# Nombre de la app para utilizar los api
app_name = 'tienda' 

urlpatterns = [
    #rutas para las views
    #las funciones que definimos en views.py
    path('', views.index, name='index'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('producto/<int:pk>/', views.detalle_producto, name='detalle_producto'),
    path('solicitar/', views.solicitar_pedido, name='solicitar_pedido'),
    path('pedido-exitoso/', views.pedido_exitoso, name='pedido_exitoso'),
    path('seguimiento/<str:token>/', views.seguimiento_pedido, name='seguimiento_pedido'),
    path('reporte/', views.ReporteView.as_view(), name='reporte')
]