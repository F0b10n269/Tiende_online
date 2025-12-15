from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from django import forms
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
    list_display = ['nombre', 'categoria', 'precio_base', 'activo', 'imagen_preview']
    list_filter = ['categoria', 'activo']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['activo', 'precio_base']
    
    def imagen_preview(self, obj):
        if obj.imagen_1:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.imagen_1.url)
        return "Sin imagen"
    imagen_preview.short_description = 'Imagen'

# ============================================
# INSUMO
# ============================================
@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    # ✅ ACTUALIZADO: Agregar marca y color
    list_display = [
        'nombre', 
        'tipo', 
        'cantidad_disponible', 
        'unidad', 
        'marca',      # ✅ NUEVO
        'color',      # ✅ NUEVO
        'estado_stock'
    ]
    
    # ✅ ACTUALIZADO: Agregar marca a los filtros
    list_filter = ['tipo', 'unidad', 'marca']
    
    # ✅ ACTUALIZADO: Agregar marca y color a la búsqueda
    search_fields = ['nombre', 'tipo', 'marca', 'color']
    
    # ✅ ACTUALIZADO: Hacer la marca editable desde la lista
    list_editable = ['cantidad_disponible', 'marca']
    
    # ✅ AGREGADO: Organizar el formulario
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'nombre',
                'tipo',
                'marca',      # ✅ NUEVO
                'color',      # ✅ NUEVO
            )
        }),
        ('Control de Inventario', {
            'fields': (
                'cantidad_disponible',
                'unidad',
            )
        }),
    )
    
    def estado_stock(self, obj):
        if obj.cantidad_disponible == 0:
            return format_html('<span style="color: red;">⏹️ Sin stock</span>')
        elif obj.cantidad_disponible < 10:
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
    readonly_fields = ['fecha_subida']

# ============================================
# PEDIDO - VERSIÓN SIN UUID
# ============================================
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    form = PedidoAdminForm
    
    list_display = [
        'id', 
        'nombre_cliente', 
        'estado_pedido', 
        'estado_pago',
        'plataforma', 
        'fecha_creacion', 
        'token_corto'
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
        'token_seguimiento',
        'descripcion_diseno'
    ]
    
    readonly_fields = [
        'token_seguimiento', 
        'fecha_creacion', 
        'fecha_actualizacion'
    ]
    
    list_editable = ['estado_pedido', 'estado_pago']
    inlines = [ImagenReferenciaInline]
    
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('nombre_cliente', 'email', 'telefono', 'red_social')
        }),
        ('Detalles del Pedido', {
            'fields': ('producto_referencia', 'descripcion_diseno', 'fecha_requerida', 'plataforma')
        }),
        ('Estados', {
            'fields': ('estado_pedido', 'estado_pago')
        }),
        ('Información Adicional', {
            'fields': ('presupuesto_aprobado', 'presupuesto_estimado', 'notas_internas')
        }),
        ('Metadatos', {
            'fields': ('token_seguimiento', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def token_corto(self, obj):
        # Mostrar solo primeros 8 caracteres del token string
        if obj.token_seguimiento and len(obj.token_seguimiento) > 8:
            return str(obj.token_seguimiento)[:8] + '...'
        return str(obj.token_seguimiento) if obj.token_seguimiento else ''
    token_corto.short_description = 'Token'

    # ✅ ACCIONES SIMPLES (del primer código, adaptadas)
    actions = ['marcar_como_aprobado', 'marcar_como_en_proceso', 'marcar_pago_como_pagado']
    
    def marcar_como_aprobado(self, request, queryset):
        updated = queryset.update(estado_pedido='aprobado')
        self.message_user(request, f'{updated} pedidos aprobados.')
    marcar_como_aprobado.short_description = "Marcar como Aprobado"
    
    def marcar_como_en_proceso(self, request, queryset):
        updated = queryset.update(estado_pedido='en_proceso')
        self.message_user(request, f'{updated} pedidos en proceso.')
    marcar_como_en_proceso.short_description = "Marcar como En Proceso"
    
    def marcar_pago_como_pagado(self, request, queryset):
        updated = queryset.update(estado_pago='pagado')
        self.message_user(request, f'{updated} pedidos marcados como pagados.')
    marcar_pago_como_pagado.short_description = "Marcar pago como Pagado"

# ============================================
# IMAGEN REFERENCIA (admin separado opcional)
# ============================================
@admin.register(ImagenReferencia)
class ImagenReferenciaAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'descripcion', 'fecha_subida', 'imagen_preview']
    list_filter = ['fecha_subida']
    
    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="50" height="50" />', obj.imagen.url)
        return "Sin imagen"
    imagen_preview.short_description = 'Vista previa'

# ============================================
# CONFIGURACIÓN DEL SITIO ADMIN
# ============================================
admin.site.site_header = "Administración de Tienda Personalizados"
admin.site.site_title = "Tienda Personalizados"
admin.site.index_title = "Panel de Control"
