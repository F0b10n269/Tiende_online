from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from .models import Categoria, Producto, Insumo, Pedido, ImagenReferencia

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'cantidad_productos', 'descripcion_corta']
    search_fields = ['nombre']
    
    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'
    
    def cantidad_productos(self, obj):
        count = obj.producto_set.count()
        url = (
            reverse('admin:tienda_producto_changelist')
            + '?'
            + urlencode({'categoria__id': f'{obj.id}'})
        )
        return format_html('<a href="{}">{} productos</a>', url, count)
    cantidad_productos.short_description = 'Productos'

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio_base', 'activo', 'imagen_preview']
    list_filter = ['categoria', 'activo']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo', 'precio_base']
    
    def imagen_preview(self, obj):
        if obj.imagen_1:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.imagen_1.url)
        return "📷"
    imagen_preview.short_description = 'Imagen'

class ImagenReferenciaInline(admin.TabularInline):
    model = ImagenReferencia
    extra = 1
    readonly_fields = ['fecha_subida', 'imagen_preview']
    fields = ['imagen', 'imagen_preview', 'descripcion', 'fecha_subida']
    
    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.imagen.url)
        return "📷"
    imagen_preview.short_description = 'Vista Previa'

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'nombre_cliente', 
        'estado_pedido',  # ✅ Agregado directamente para list_editable
        'estado_pago',    # ✅ Agregado directamente para list_editable
        'estado_pedido_badge', 
        'estado_pago_badge', 
        'plataforma_badge',
        'fecha_creacion',
        'acciones_rapidas'
    ]
    
    list_filter = [
        'estado_pedido', 
        'estado_pago', 
        'plataforma', 
        'fecha_creacion',
        'producto_referencia'
    ]
    
    search_fields = [
        'nombre_cliente', 
        'email', 
        'telefono',
        'token_seguimiento',
        'descripcion_diseno'
    ]
    
    readonly_fields = [
        'token_seguimiento', 
        'fecha_creacion', 
        'fecha_actualizacion',
        'url_seguimiento'
    ]
    
    # ✅ CORRECCIÓN: Los campos deben estar en list_display para poder estar en list_editable
    list_editable = ['estado_pedido', 'estado_pago']
    
    inlines = [ImagenReferenciaInline]
    
    fieldsets = (
        ('👤 Información del Cliente', {
            'fields': (
                'nombre_cliente', 
                'email', 
                'telefono', 
                'red_social'
            )
        }),
        
        ('📦 Detalles del Pedido', {
            'fields': (
                'producto_referencia', 
                'descripcion_diseno', 
                'fecha_requerida', 
                'plataforma'
            )
        }),
        
        ('🔄 Estados del Pedido', {
            'fields': (
                'estado_pedido', 
                'estado_pago',
                'presupuesto_aprobado',
                'notas_internas'
            )
        }),
        
        ('🔗 Información de Seguimiento', {
            'fields': (
                'token_seguimiento',
                'url_seguimiento'
            ),
            'classes': ('collapse',)
        }),
        
        ('📅 Metadatos', {
            'fields': (
                'fecha_creacion', 
                'fecha_actualizacion'
            ),
            'classes': ('collapse',)
        }),
    )
    
    # Acciones personalizadas
    actions = ['marcar_como_aprobado', 'marcar_como_en_proceso', 'marcar_como_completado']
    
    def marcar_como_aprobado(self, request, queryset):
        updated = queryset.update(estado_pedido='aprobado')
        self.message_user(request, f'{updated} pedidos marcados como aprobados.')
    marcar_como_aprobado.short_description = "✅ Marcar pedidos seleccionados como Aprobados"
    
    def marcar_como_en_proceso(self, request, queryset):
        updated = queryset.update(estado_pedido='en_proceso')
        self.message_user(request, f'{updated} pedidos marcados como en proceso.')
    marcar_como_en_proceso.short_description = "⚙️ Marcar pedidos seleccionados como En Proceso"
    
    def marcar_como_completado(self, request, queryset):
        updated = queryset.update(estado_pedido='realizado', estado_pago='pagado')
        self.message_user(request, f'{updated} pedidos marcados como completados y pagados.')
    marcar_como_completado.short_description = "🎉 Marcar pedidos seleccionados como Completados"
    
    # Badges para visualización (solo lectura)
    def estado_pedido_badge(self, obj):
        colors = {
            'solicitado': '#6c757d',
            'aprobado': '#0dcaf0', 
            'en_proceso': '#0d6efd',
            'realizado': '#198754',
            'entregado': '#198754',
            'finalizado': '#212529',
            'cancelado': '#dc3545'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            colors.get(obj.estado_pedido, '#6c757d'),
            obj.get_estado_pedido_display()
        )
    estado_pedido_badge.short_description = 'Estado Visual'
    
    def estado_pago_badge(self, obj):
        colors = {
            'pendiente': '#ffc107',
            'parcial': '#0dcaf0',
            'pagado': '#198754'
        }
        return format_html(
            '<span style="background: {}; color: black; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            colors.get(obj.estado_pago, '#6c757d'),
            obj.get_estado_pago_display()
        )
    estado_pago_badge.short_description = 'Pago Visual'
    
    def plataforma_badge(self, obj):
        colors = {
            'facebook': '#1877f2',
            'instagram': '#e4405f',
            'whatsapp': '#25d366',
            'sitio_web': '#0dcaf0',
            'presencial': '#fd7e14',
            'otro': '#6c757d'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            colors.get(obj.plataforma, '#6c757d'),
            obj.get_plataforma_display()
        )
    plataforma_badge.short_description = 'Plataforma'
    
    def url_seguimiento(self, obj):
        if obj.token_seguimiento:
            url = reverse('tienda:seguimiento_pedido', kwargs={'token': obj.token_seguimiento})
            full_url = f"http://127.0.0.1:8000{url}"
            return format_html('<a href="{}" target="_blank">🔗 Ver Seguimiento del Cliente</a>', full_url)
        return "-"
    url_seguimiento.short_description = 'URL de Seguimiento'
    
    def acciones_rapidas(self, obj):
        links = []
        if obj.estado_pedido == 'solicitado':
            links.append('<span style="color: #0dcaf0;">⏳ Esperando aprobación</span>')
        elif obj.estado_pedido == 'aprobado':
            links.append('<span style="color: #198754;">✅ Aprobado</span>')
        elif obj.estado_pedido == 'en_proceso':
            links.append('<span style="color: #0d6efd;">⚙️ En producción</span>')
        elif obj.estado_pedido == 'realizado':
            links.append('<span style="color: #198754;">🎉 Listo</span>')
        
        # Agregar enlace al seguimiento
        if obj.token_seguimiento:
            url = reverse('tienda:seguimiento_pedido', kwargs={'token': obj.token_seguimiento})
            links.append(f'<a href="{url}" target="_blank">👁️ Ver</a>')
        
        return format_html(' | '.join(links)) if links else "-"
    acciones_rapidas.short_description = 'Acciones'

@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 
        'tipo', 
        'cantidad_disponible', 
        'unidad', 
        'estado_stock', 
        'necesita_reposicion'
    ]
    
    list_filter = [
        'tipo', 
        'unidad'
    ]
    
    search_fields = [
        'nombre'
    ]
    
    list_editable = [
        'cantidad_disponible'
    ]
    
    def estado_stock(self, obj):
        # Usar el método del modelo si existe, sino usar lógica básica
        if hasattr(obj, 'get_estado_inventario'):
            estado = obj.get_estado_inventario()
        else:
            # Lógica básica si el método no existe
            if obj.cantidad_disponible == 0:
                estado = "agotado"
            elif obj.cantidad_disponible < 10:
                estado = "bajo"
            else:
                estado = "normal"
        
        if estado == "agotado":
            return format_html('<span style="color: red; font-weight: bold;">⏹️ AGOTADO</span>')
        elif estado == "bajo":
            return format_html('<span style="color: orange; font-weight: bold;">⚠️ BAJO STOCK</span>')
        else:
            return format_html('<span style="color: green; font-weight: bold;">✅ EN STOCK</span>')
    estado_stock.short_description = 'Estado Stock'
    
    def necesita_reposicion(self, obj):
        # Usar el método del modelo si existe, sino usar lógica básica
        if hasattr(obj, 'necesita_reposicion'):
            return obj.necesita_reposicion()
        else:
            # Lógica básica si el método no existe
            return obj.cantidad_disponible < 5
    necesita_reposicion.boolean = True
    necesita_reposicion.short_description = '¿Reponer?'

# Configuración del sitio admin
admin.site.site_header = "🎨 Administración - Tienda Personalizados"
admin.site.site_title = "Tienda Personalizados - Admin"
admin.site.index_title = "📊 Panel de Control"
