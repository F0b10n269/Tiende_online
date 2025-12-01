from django.urls import path
from . import views

app_name = 'tienda'

urlpatterns = [
    path('', views.index, name='index'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('producto/<int:pk>/', views.detalle_producto, name='detalle_producto'),
    path('solicitar-pedido/', views.solicitar_pedido, name='solicitar_pedido'),
    path('pedido-exitoso/', views.pedido_exitoso, name='pedido_exitoso'),
    # CAMBIAR: Usar <str:token> en lugar de <uuid:token>
    path('seguimiento/<str:token>/', views.seguimiento_pedido, name='seguimiento_pedido'),
]
