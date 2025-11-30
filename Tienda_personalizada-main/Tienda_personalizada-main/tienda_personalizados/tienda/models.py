import uuid
from django.db import models
from django.utils import timezone

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
    
    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)
    imagen_1 = models.ImageField(upload_to='productos/', blank=True, null=True)
    imagen_2 = models.ImageField(upload_to='productos/', blank=True, null=True)
    imagen_3 = models.ImageField(upload_to='productos/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
    
    def __str__(self):
        return self.nombre


class Insumo(models.Model):
    TIPOS_INSUMO = [
        ('tela', 'Tela'),
        ('filamento', 'Filamento 3D'),
        ('tazas', 'Tazas en blanco'),
        ('accesorios', 'Accesorios'),
        ('otros', 'Otros'),
    ]
    
    UNIDADES = [
        ('metros', 'Metros'),
        ('unidades', 'Unidades'),
        ('kg', 'Kilogramos'),
        ('rollos', 'Rollos'),
        ('litros', 'Litros'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name="Nombre del insumo")
    tipo = models.CharField(max_length=20, choices=TIPOS_INSUMO, verbose_name="Tipo de insumo")
    cantidad_disponible = models.IntegerField(default=0, verbose_name="Cantidad disponible")
    cantidad_minima = models.IntegerField(default=10, verbose_name="Cantidad mínima")
    unidad = models.CharField(max_length=20, choices=UNIDADES, default='unidades', verbose_name="Unidad de medida")
    marca = models.CharField(max_length=50, blank=True, verbose_name="Marca")
    color = models.CharField(max_length=30, blank=True, verbose_name="Color")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Precio unitario")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"
        ordering = ['tipo', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.marca} ({self.cantidad_disponible} {self.unidad})"
    
    def necesita_reposicion(self):
        """Verifica si el insumo necesita reposición"""
        return self.cantidad_disponible <= self.cantidad_minima
    
    def get_estado_inventario(self):
        """Retorna el estado del inventario"""
        if self.cantidad_disponible == 0:
            return "agotado"
        elif self.necesita_reposicion():
            return "bajo"
        else:
            return "normal"


class Pedido(models.Model):
    ESTADOS_PEDIDO = [
        ('solicitado', 'Solicitado'),
        ('aprobado', 'Aprobado'),
        ('en_proceso', 'En proceso'),
        ('realizado', 'Realizado'),
        ('entregado', 'Entregado'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]
    
    ESTADOS_PAGO = [
        ('pendiente', 'Pendiente'),
        ('parcial', 'Parcial'),
        ('pagado', 'Pagado'),
    ]
    
    PLATAFORMAS = [
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('whatsapp', 'WhatsApp'),
        ('sitio_web', 'Sitio Web'),
        ('presencial', 'Presencial'),
        ('otro', 'Otro'),
    ]
    
    # Información del cliente
    nombre_cliente = models.CharField(max_length=200)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)
    red_social = models.CharField(max_length=100, blank=True)
    
    # Información del pedido
    producto_referencia = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion_diseno = models.TextField()
    fecha_requerida = models.DateField(null=True, blank=True)
    plataforma = models.CharField(max_length=20, choices=PLATAFORMAS, default='sitio_web')
    
    # Estados
    estado_pedido = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='solicitado')
    estado_pago = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='pendiente')
    
    # Token de seguimiento (ahora con nombre más amigable)
    token_seguimiento = models.CharField(
        "Token de seguimiento",
        max_length=12,
        unique=True,
        editable=False,
        blank=True
    )

    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Funcionalidad extra: Presupuesto
    presupuesto_aprobado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notas_internas = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.nombre_cliente}"

    def save(self, *args, **kwargs):
        if not self.token_seguimiento:
            self.token_seguimiento = uuid.uuid4().hex[:12]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('tienda:seguimiento_pedido', kwargs={'token': self.token_seguimiento})


class ImagenReferencia(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='imagenes_referencia', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='referencias/')
    descripcion = models.CharField(max_length=200, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Imagen de Referencia"
        verbose_name_plural = "Imágenes de Referencia"
    
    def __str__(self):
        return f"Imagen para {self.pedido}"
