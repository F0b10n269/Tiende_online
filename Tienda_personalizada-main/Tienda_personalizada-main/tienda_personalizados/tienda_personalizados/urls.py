from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importamos las vistas necesarias para la API
from tienda.views import InsumoViewSet, PedidoViewSet, filtro_pedidos
from rest_framework.routers import DefaultRouter

# Configuración del Router de la API
router = DefaultRouter()
router.register(r'insumos', InsumoViewSet, basename='insumo')
router.register(r'pedidos', PedidoViewSet, basename='pedido')

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Rutas de la API (El orden importa)
    # Primero el filtro específico para que no choque con el router
    path('api/pedidos/filtrar/', filtro_pedidos, name='api-filtro-pedidos'),
    
    # Luego las rutas automáticas del router (insumos, pedidos, etc.)
    path('api/', include(router.urls)),

    # 2. Rutas del Frontend (Tienda)
    # Incluimos el archivo tienda/urls.py que acabamos de arreglar
    path('', include('tienda.urls', namespace='tienda')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)