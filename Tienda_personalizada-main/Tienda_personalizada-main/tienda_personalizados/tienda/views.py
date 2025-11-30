from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Producto, Categoria, Pedido
from .forms import SolicitudPedidoForm
from django.db.models import Q  

def index(request):
    # ✅ Productos destacados (máximo 6)
    productos_destacados = Producto.objects.filter(activo=True, destacado=True)[:6]
    
    # ✅ Si no hay productos destacados, mostrar productos normales
    if not productos_destacados:
        productos_destacados = Producto.objects.filter(activo=True)[:6]
    
    categorias = Categoria.objects.all()
    return render(request, 'tienda/index.html', {
        'productos_destacados': productos_destacados,
        'categorias': categorias
    })

def catalogo(request):
    productos = Producto.objects.filter(activo=True)
    
    # ✅ Búsqueda por término
    query = request.GET.get('q')
    if query:
        productos = productos.filter(
            models.Q(nombre__icontains=query) | 
            models.Q(descripcion__icontains=query) |
            models.Q(categoria__nombre__icontains=query)
        )
    
    # ✅ Filtrado por categoría
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    # ✅ Obtener categorías para el filtro
    categorias = Categoria.objects.all()
    
    return render(request, 'tienda/catalogo.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_actual': categoria_id,
        'query': query  # ✅ Pasar la query al template
    })

def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk, activo=True)
    return render(request, 'tienda/detalle_producto.html', {'producto': producto})

def solicitar_pedido(request):
    if request.method == 'POST':
        form = SolicitudPedidoForm(request.POST, request.FILES)
        if form.is_valid():
            pedido = form.save()
            request.session['ultimo_pedido_id'] = pedido.id
            request.session['token_seguimiento'] = str(pedido.token_seguimiento)
            return redirect('tienda:pedido_exitoso')
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
    pedido_id = request.session.get('ultimo_pedido_id')
    token_seguimiento = request.session.get('token_seguimiento')
    
    if not pedido_id or not token_seguimiento:
        return redirect('tienda:index')
    
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        # CORREGIR: Usar reverse con el token completo
        url_seguimiento = request.build_absolute_uri(
            reverse('tienda:seguimiento_pedido', kwargs={'token': str(pedido.token_seguimiento)})
        )
        context = {
            'pedido': pedido,
            'url_seguimiento': url_seguimiento
        }
        
        # Limpiar la sesión
        if 'ultimo_pedido_id' in request.session:
            del request.session['ultimo_pedido_id']
        if 'token_seguimiento' in request.session:
            del request.session['token_seguimiento']
            
        return render(request, 'tienda/pedido_exitoso.html', context)
    except Pedido.DoesNotExist:
        return redirect('tienda:index')

def seguimiento_pedido(request, token):
    try:
        # Buscar el pedido por el token completo
        pedido = get_object_or_404(Pedido, token_seguimiento=token)
    except Pedido.DoesNotExist:
        # Si no encuentra, intentar buscar como string
        try:
            pedido = get_object_or_404(Pedido, token_seguimiento__contains=token)
        except Pedido.DoesNotExist:
            return render(request, 'tienda/404.html', status=404)
    
    imagenes_referencia = pedido.imagenes_referencia.all()
    return render(request, 'tienda/seguimiento_pedido.html', {
        'pedido': pedido,
        'imagenes_referencia': imagenes_referencia
    })

