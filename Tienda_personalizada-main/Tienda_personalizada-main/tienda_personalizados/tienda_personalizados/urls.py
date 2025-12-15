from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from tienda.views import InsumoViewSet, PedidoViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'insumos',InsumoViewSet,basename='insumo')

#cuando se añade un nuevo viewset en al momento de registrarlo debe ser router.register de otra forma te dara error al haberse creado otro puerto
router.register(r'pedidos',PedidoViewSet, basename='pedido') #si aun te da error borra el defaultrouter dejando solo 1

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tienda.urls')),
    path('api/',include(router.urls))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


    