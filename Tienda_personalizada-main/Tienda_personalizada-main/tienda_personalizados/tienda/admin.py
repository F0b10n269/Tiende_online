from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from django import forms
from django.db.models import Q
from .models import Categoria, Producto, Insumo, Pedido, ImagenReferencia

# ============================================
# FORMULARIO PERSONALIZADO PARA PEDIDOS
# ============================================
class PedidoAdminForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = '__all__'
        widgets = {
            'descripcion_diseno': forms.Textarea(attrs={'rows': 3}),
            'notas_internas': forms.Textarea(attrs={'rows': 3}),
        }

# ============================================
# CATEGORÍA
# ============================================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'cantidad_productos', 'descripcion_corta']
    search_fields = ['nombre', 'descripcion']
    list_per_page = 20
    
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
        return format_html('<a href="{}">{}</a>', url, count)
    cantidad_productos.short_description = 'Productos'

# ============================================
# PRODUCTO
# ============================================
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio_base', 'activo', 'imagen_preview', 'acciones']
    list_filter = ['categoria', 'activo']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['precio_base']
    list_per_page = 20
    
    def imagen_preview(self, obj):
        if obj.imagen_1:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />',
                obj.imagen_1.url
            )
        return "📷"
    imagen_preview.short_description = 'Imagen'
    
    def acciones(self, obj):
        pedidos_count = Pedido.objects.filter(producto_referencia=obj).count()
        if pedidos_count > 0:
            url = reverse('admin:tienda_pedido_changelist') + '?' + urlencode({'producto_referencia__id': f'{obj.id}'})
            return format_html('<a href="{}">{} pedidos</a>', url, pedidos_count)
        return "—"

# ============================================
# INSUMO
# ============================================
@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'cantidad_disponible', 'unidad', 'estado_stock']
    list_filter = ['tipo', 'unidad']
    search_fields = ['nombre', 'tipo']
    list_editable = ['cantidad_disponible']
    list_per_page = 20
    
    def estado_stock(self, obj):
        if obj.cantidad_disponible == 0:
            return format_html('<span style="color: red;">⛔ Sin stock</span>')
        elif obj.cantidad_disponible < 5:
            return format_html('<span style="color: orange;">⚠️ Bajo stock</span>')
        else:
            return format_html('<span style="color: green;">✅ En stock</span>')
    estado_stock.short_description = 'Estado'

# ============================================
# IMAGEN REFERENCIA INLINE
# ============================================
class ImagenReferenciaInline(admin.TabularInline):
    model = ImagenReferencia
    extra = 1
    readonly_fields = ['fecha_subida', 'imagen_preview']
    
    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="50" height="50" />', obj.imagen.url)
        return "📷"

# ============================================
# PEDIDO - CON MANEJO DE ERRORES DE UUID
# ============================================
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    form = PedidoAdminForm
    
    # ✅ LIST_DISPLAY SEGURO - Solo campos/métodos que no fallen
    list_display = [
        'id', 
        'nombre_cliente', 
        'email',
        'estado_pedido',
        'estado_pago',
        'plataforma',
        'fecha_creacion_corta',
    ]
    
    list_filter = [
        'estado_pedido', 
        'estado_pago', 
        'plataforma',
        'fecha_creacion'
    ]
    
    search_fields = [
        'nombre_cliente', 
        'email', 
        'telefono',
        'descripcion_diseno'
    ]
    
    readonly_fields = [
        'fecha_creacion', 
        'fecha_actualizacion',
        'token_seguimiento_display',  # Método seguro
    ]
    
    list_editable = ['estado_pedido', 'estado_pago']
    inlines = [ImagenReferenciaInline]
    list_per_page = 25
    
    # ✅ GET_QUERYSET SEGURO - Filtra pedidos con UUIDs válidos
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Filtrar solo pedidos con UUIDs válidos
        from uuid import UUID
        valid_pedidos = []
        
        for pedido in qs:
            try:
                # Verificar si el token es un UUID válido
                str_token = str(pedido.token_seguimiento)
                UUID(str_token)
                valid_pedidos.append(pedido.id)
            except (ValueError, AttributeError):
                # Si no es válido, no incluirlo en la lista
                continue
        
        return qs.filter(id__in=valid_pedidos)
    
    # ✅ MÉTODO SEGURO para mostrar token
    def token_seguimiento_display(self, obj):
        try:
            return str(obj.token_seguimiento)
        except:
            return "❌ Token inválido"
    token_seguimiento_display.short_description = 'Token de Seguimiento'
    
    # ✅ MÉTODO SEGURO para fecha
    def fecha_creacion_corta(self, obj):
        return obj.fecha_creacion.strftime('%d/%m %H:%M')
    fecha_creacion_corta.short_description = 'Fecha'
    
    # ✅ FIELDSETS SIMPLES
    fieldsets = (
        ('👤 Información del Cliente', {
            'fields': ('nombre_cliente', 'email', 'telefono', 'red_social')
        }),
        ('📦 Detalles del Pedido', {
            'fields': ('producto_referencia', 'descripcion_diseno', 'fecha_requerida', 'plataforma')
        }),
        ('🔄 Estados', {
            'fields': ('estado_pedido', 'estado_pago', 'presupuesto_aprobado', 'notas_internas')
        }),
        ('🔗 Seguimiento', {
            'fields': ('token_seguimiento_display',),
            'classes': ('collapse',)
        }),
        ('📅 Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    # ✅ ACCIONES SEGURAS
    actions = ['marcar_como_aprobado', 'marcar_como_en_proceso', 'marcar_pago_como_pagado']
    
    def marcar_como_aprobado(self, request, queryset):
        updated = queryset.update(estado_pedido='aprobado')
        self.message_user(request, f'{updated} pedidos aprobados.')
    
    def marcar_como_en_proceso(self, request, queryset):
        updated = queryset.update(estado_pedido='en_proceso')
        self.message_user(request, f'{updated} pedidos en proceso.')
    
    def marcar_pago_como_pagado(self, request, queryset):
        updated = queryset.update(estado_pago='pagado')
        self.message_user(request, f'{updated} pedidos marcados como pagados.')

# ============================================
# CONFIGURACIÓN DEL SITIO ADMIN
# ============================================
admin.site.site_header = "🎨 Tienda Personalizados"
admin.site.site_title = "Admin"
admin.site.index_title = "Panel de Control"
