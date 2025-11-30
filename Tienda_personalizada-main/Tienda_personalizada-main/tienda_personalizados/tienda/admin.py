from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from django.db.models import F
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
        'estado_pedido',  # ✅ Para list_editable
        'estado_pago',    # ✅ Para list_editable
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
        'tipo_badge', 
        'cantidad_disponible', 
        'cantidad_minima',
        'unidad_badge', 
        'estado_inventario_badge', 
        'necesita_reposicion_badge',
        'marca',
        'color_display',
        'fecha_actualizacion_short'
    ]
    
    list_filter = [
        'tipo', 
        'unidad', 
        'marca',
        'necesita_reposicion_filter'
    ]
    
    search_fields = [
        'nombre', 
        'marca', 
        'color',
        'tipo'
    ]
    
    list_editable = [
        'cantidad_disponible', 
        'cantidad_minima'
    ]
    
    readonly_fields = [
        'fecha_actualizacion',
        'estado_inventario_display',
        'necesita_reposicion_display'
    ]
    
    fieldsets = (
        ('Información Básica del Insumo', {
            'fields': (
                'nombre',
                'tipo',
                'marca',
                'color',
                'activo'
            )
        }),
        
        ('Control de Inventario', {
            'fields': (
                'cantidad_disponible',
                'cantidad_minima', 
                'unidad',
                'precio_unitario',
                'estado_inventario_display',
                'necesita_reposicion_display'
            )
        }),
        
        ('Metadatos', {
            'fields': (
                'fecha_actualizacion',
            ),
            'classes': ('collapse',)
        }),
    )
    
    # Acciones personalizadas para inventario
    actions = [
        'reponer_stock_minimo',
        'incrementar_stock_10',
        'incrementar_stock_50',
        'marcar_como_inactivos_agotados'
    ]
    
    def reponer_stock_minimo(self, request, queryset):
        """Repone el stock al nivel mínimo establecido"""
        for insumo in queryset:
            if insumo.cantidad_disponible < insumo.cantidad_minima:
                cantidad_reponer = insumo.cantidad_minima * 2
                insumo.cantidad_disponible = cantidad_reponer
                insumo.save()
        
        self.message_user(
            request, 
            f"✅ Stock repuesto para {queryset.count()} insumos que estaban bajo mínimo"
        )
    reponer_stock_minimo.short_description = "🔄 Reponer stock al doble del mínimo"
    
    def incrementar_stock_10(self, request, queryset):
        """Incrementa el stock en 10 unidades"""
        for insumo in queryset:
            insumo.cantidad_disponible += 10
            insumo.save()
        
        self.message_user(
            request, 
            f"📈 Stock incrementado en 10 unidades para {queryset.count()} insumos"
        )
    incrementar_stock_10.short_description = "➕ Incrementar stock +10 unidades"
    
    def incrementar_stock_50(self, request, queryset):
        """Incrementa el stock en 50 unidades"""
        for insumo in queryset:
            insumo.cantidad_disponible += 50
            insumo.save()
        
        self.message_user(
            request, 
            f"📈 Stock incrementado en 50 unidades para {queryset.count()} insumos"
        )
    incrementar_stock_50.short_description = "➕ Incrementar stock +50 unidades"
    
    def marcar_como_inactivos_agotados(self, request, queryset):
        """Marca como inactivos los insumos agotados"""
        insumos_agotados = queryset.filter(cantidad_disponible=0)
        count = insumos_agotados.update(activo=False)
        
        self.message_user(
            request, 
            f"🔴 {count} insumos agotados marcados como inactivos"
        )
    marcar_como_inactivos_agotados.short_description = "🚫 Marcar insumos agotados como inactivos"
    
    # Filtros personalizados
    def necesita_reposicion_filter(self, queryset, name, value):
        if value == 'si':
            return queryset.filter(cantidad_disponible__lte=F('cantidad_minima'))
        elif value == 'no':
            return queryset.filter(cantidad_disponible__gt=F('cantidad_minima'))
        return queryset
    necesita_reposicion_filter.parameter_name = 'necesita_reposicion'
    necesita_reposicion_filter.title = '¿Necesita reposición?'
    
    # Métodos para display en lista
    def tipo_badge(self, obj):
        colors = {
            'tela': '#e91e63',
            'filamento': '#9c27b0',
            'tazas': '#2196f3',
            'accesorios': '#4caf50',
            'otros': '#607d8b'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            colors.get(obj.tipo, '#607d8b'),
            obj.get_tipo_display().upper()
        )
    tipo_badge.short_description = 'Tipo'
    
    def unidad_badge(self, obj):
        return format_html(
            '<span style="background: #17a2b8; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            obj.get_unidad_display()
        )
    unidad_badge.short_description = 'Unidad'
    
    def estado_inventario_badge(self, obj):
        estado = obj.get_estado_inventario()
        if estado == "agotado":
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">🔴 AGOTADO</span>'
            )
        elif estado == "bajo":
            return format_html(
                '<span style="background: #ffc107; color: black; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">🟡 BAJO STOCK</span>'
            )
        else:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">🟢 NORMAL</span>'
            )
    estado_inventario_badge.short_description = 'Estado Inventario'
    
    def necesita_reposicion_badge(self, obj):
        if obj.necesita_reposicion():
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">🚨 REPONER</span>'
            )
        return format_html(
            '<span style="background: #28a745; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">✅ OK</span>'
        )
    necesita_reposicion_badge.short_description = 'Reponer'
    
    def color_display(self, obj):
        if obj.color:
            return format_html(
                '<span style="display: inline-block; width: 20px; height: 20px; background: {}; border: 1px solid #ccc; border-radius: 3px;" title="{}"></span> {}',
                obj.color.lower(),
                obj.color,
                obj.color
            )
        return "-"
    color_display.short_description = 'Color'
    
    def fecha_actualizacion_short(self, obj):
        return obj.fecha_actualizacion.strftime("%d/%m/%Y")
    fecha_actualizacion_short.short_description = 'Última Actualización'
    
    # Métodos para campos de solo lectura
    def estado_inventario_display(self, obj):
        estado = obj.get_estado_inventario()
        if estado == "agotado":
            return format_html('<span style="color: #dc3545; font-weight: bold;">🔴 AGOTADO - Stock: 0 unidades</span>')
        elif estado == "bajo":
            return format_html('<span style="color: #ffc107; font-weight: bold;">🟡 BAJO STOCK - Solo {} unidades disponibles</span>', obj.cantidad_disponible)
        else:
            return format_html('<span style="color: #28a745; font-weight: bold;">🟢 STOCK NORMAL - {} unidades disponibles</span>', obj.cantidad_disponible)
    estado_inventario_display.short_description = 'Estado Actual del Inventario'
    
    def necesita_reposicion_display(self, obj):
        if obj.necesita_reposicion():
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">🚨 NECESITA REPOSICIÓN URGENTE! (Mínimo: {}, Actual: {})</span>',
                obj.cantidad_minima,
                obj.cantidad_disponible
            )
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">✅ Stock suficiente (Mínimo: {}, Actual: {})</span>',
            obj.cantidad_minima,
            obj.cantidad_disponible
        )
    necesita_reposicion_display.short_description = 'Alerta de Reposición'

# Configuración del sitio admin
admin.site.site_header = "🎨 Administración - Tienda Personalizados"
admin.site.site_title = "Tienda Personalizados - Admin"
admin.site.index_title = "📊 Panel de Control"
