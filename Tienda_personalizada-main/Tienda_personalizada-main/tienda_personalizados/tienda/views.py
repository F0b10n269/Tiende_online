from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages  # ✅ AGREGAR ESTA IMPORTACIÓN

from .models import Producto, Categoria, Pedido
from .forms import SolicitudPedidoForm

def index(request):
    productos_destacados = Producto.objects.filter(activo=True)[:6]
    categorias = Categoria.objects.all()
    return render(request, 'tienda/index.html', {
        'productos_destacados': productos_destacados,
        'categorias': categorias
    })

def catalogo(request):
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
    producto = get_object_or_404(Producto, pk=pk, activo=True)
    return render(request, 'tienda/detalle_producto.html', {'producto': producto})

def solicitar_pedido(request):
    if request.method == 'POST':
        form = SolicitudPedidoForm(request.POST, request.FILES)
        if form.is_valid():
            pedido = form.save()
            request.session['ultimo_pedido_id'] = pedido.id
            request.session['token_seguimiento'] = str(pedido.token_seguimiento)
            
            # ✅ CORREGIDO: Usar messages correctamente después de importarlo
            messages.success(request, '¡Pedido enviado con éxito!')
            return redirect('tienda:pedido_exitoso')
        else:
            # ✅ CORREGIDO: Mensaje de error si el formulario no es válido
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
        return render(request, 'tienda/pedido_exitoso.html', context)
    except Pedido.DoesNotExist:
        messages.error(request, 'No se encontró el pedido.')
        return redirect('tienda:index')

def seguimiento_pedido(request, token):
    pedido = get_object_or_404(Pedido, token_seguimiento=token)
    imagenes_referencia = pedido.imagenes_referencia.all()
    return render(request, 'tienda/seguimiento_pedido.html', {
        'pedido': pedido,
        'imagenes_referencia': imagenes_referencia
    })
