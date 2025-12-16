from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importamos las vistas y viewsets necesarias para la API ademas del defaultrouter
from tienda.views import InsumoViewSet, PedidoViewSet, filtro_pedidos
from rest_framework.routers import DefaultRouter

# Configuración del Router para que la API funcione
router = DefaultRouter()
router.register(r'insumos', InsumoViewSet, basename='insumo')
router.register(r'pedidos', PedidoViewSet, basename='pedido')

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Rutas de la API
    # Primero ee mapeo el filtro para que no cause conflictos con el resto de las api
    path('api/pedidos/filtrar/', filtro_pedidos, name='api-filtro-pedidos'),
    
    # Luego asociamos todas las rutas con la API (insumos, pedidos, etc.)
    path('api/', include(router.urls)),

    # 2. Rutas de Frontend (Tienda)
    # Incluimos el archivo tienda/urls.py que acabamos de arreglar junto a sus respectivas funciones
    path('', include('tienda.urls', namespace='tienda')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)