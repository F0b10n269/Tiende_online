from django.urls import path
from . import views

app_name = 'tienda'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('catalogo/', views.CatalogoView.as_view(), name='catalogo'),
    path('producto/<int:pk>/', views.DetalleProductoView.as_view(), name='detalle_producto'),
    path('solicitar-pedido/', views.SolicitarPedidoView.as_view(), name='solicitar_pedido'),
    path('pedido-exitoso/', views.pedido_exitoso, name='pedido_exitoso'),

    # URL correcta para seguimiento
    path('seguimiento/<str:token>/', views.seguimiento_pedido, name='seguimiento_pedido'),
]
