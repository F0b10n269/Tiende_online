from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from .serializers import InsumoSerializer, PedidoSerializer
from .models import Insumo
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import viewsets, mixins

from .models import Producto, Categoria, Pedido
from .forms import SolicitudPedidoForm

# ============================================
# VISTAS BASADAS EN FUNCIONES
# ============================================

def index(request):
    """Vista de inicio con productos destacados y categorías"""
    productos_destacados = Producto.objects.filter(activo=True)[:6]
    categorias = Categoria.objects.all()
    return render(request, 'tienda/index.html', {
        'productos_destacados': productos_destacados,
        'categorias': categorias
    })

def catalogo(request):
    """Vista de catálogo con filtros y búsqueda"""
    productos = Producto.objects.filter(activo=True)
    categoria_id = request.GET.get('categoria')
    busqueda = request.GET.get('q')
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) | 
            Q(descripcion__icontains=busqueda)
        )
    
    categorias = Categoria.objects.all()
    return render(request, 'tienda/catalogo.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_actual': categoria_id,
        'busqueda': busqueda
    })

def detalle_producto(request, pk):
    """Vista de detalle de producto"""
    producto = get_object_or_404(Producto, pk=pk, activo=True)
    return render(request, 'tienda/detalle_producto.html', {'producto': producto})

def solicitar_pedido(request):
    """Vista para solicitar pedido (versión basada en función)"""
    if request.method == 'POST':
        form = SolicitudPedidoForm(request.POST, request.FILES)
        if form.is_valid():
            pedido = form.save()
            request.session['ultimo_pedido_id'] = pedido.id
            request.session['token_seguimiento'] = str(pedido.token_seguimiento)
            
            messages.success(request, '¡Pedido enviado con éxito!')
            return redirect('tienda:pedido_exitoso')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = SolicitudPedidoForm()
        producto_id = request.GET.get('producto')
        if producto_id:
            try:
                producto = Producto.objects.get(id=producto_id)
                form.initial['producto_referencia'] = producto
            except Producto.DoesNotExist:
                pass
    
    return render(request, 'tienda/solicitar_pedido.html', {'form': form})

def pedido_exitoso(request):
    """Vista de confirmación después de enviar pedido"""
    pedido_id = request.session.get('ultimo_pedido_id')
    token_seguimiento = request.session.get('token_seguimiento')
    
    if not pedido_id or not token_seguimiento:
        messages.warning(request, 'No hay información de pedido reciente.')
        return redirect('tienda:index')
    
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        context = {
            'pedido': pedido,
            'url_seguimiento': request.build_absolute_uri(f'/seguimiento/{token_seguimiento}/')
        }
        
        # Limpiar la sesión (opcional, depende de tu preferencia)
        # if 'ultimo_pedido_id' in request.session:
        #     del request.session['ultimo_pedido_id']
        # if 'token_seguimiento' in request.session:
        #     del request.session['token_seguimiento']
            
        return render(request, 'tienda/pedido_exitoso.html', context)
    except Pedido.DoesNotExist:
        messages.error(request, 'No se encontró el pedido.')
        return redirect('tienda:index')

def seguimiento_pedido(request, token):
    """Vista de seguimiento de pedido"""
    pedido = get_object_or_404(Pedido, token_seguimiento=token)
    imagenes_referencia = pedido.imagenes_referencia.all()
    return render(request, 'tienda/seguimiento_pedido.html', {
        'pedido': pedido,
        'imagenes_referencia': imagenes_referencia
    })

# ============================================
# VISTAS BASADAS EN CLASES (para mayor flexibilidad)
# ============================================

class IndexView(ListView):
    """Vista de inicio basada en clase"""
    model = Producto
    template_name = 'tienda/index.html'
    context_object_name = 'productos_destacados'
    
    def get_queryset(self):
        return Producto.objects.filter(activo=True)[:6]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        return context

class CatalogoView(ListView):
    """Vista de catálogo basada en clase"""
    model = Producto
    template_name = 'tienda/catalogo.html'
    context_object_name = 'productos'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Producto.objects.filter(activo=True)
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        context['categoria_actual'] = self.request.GET.get('categoria')
        return context

class DetalleProductoView(DetailView):
    """Vista de detalle de producto basada en clase"""
    model = Producto
    template_name = 'tienda/detalle_producto.html'
    context_object_name = 'producto'

class SolicitarPedidoView(CreateView):
    """Vista para solicitar pedido basada en clase"""
    model = Pedido
    form_class = SolicitudPedidoForm
    template_name = 'tienda/solicitar_pedido.html'
    success_url = reverse_lazy('tienda:pedido_exitoso')
    
    def get_initial(self):
        initial = super().get_initial()
        producto_id = self.request.GET.get('producto')
        if producto_id:
            try:
                producto = Producto.objects.get(id=producto_id)
                initial['producto_referencia'] = producto
            except Producto.DoesNotExist:
                pass
        return initial
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Guardar el ID del pedido en la sesión para mostrarlo en la página de éxito
        self.request.session['ultimo_pedido_id'] = self.object.id
        self.request.session['token_seguimiento'] = str(self.object.token_seguimiento)
        
        # Agregar mensaje de éxito
        messages.success(self.request, '¡Pedido enviado con éxito!')
        
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)


class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer

class PedidoViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
    ):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer