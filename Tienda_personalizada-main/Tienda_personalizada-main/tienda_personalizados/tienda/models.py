# models.py - VERSIÓN FINAL SIN UUID
from django.db import models
from django.utils import timezone
import secrets  # Para generar tokens simples

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
    TIPOS_UNIDAD = [
        ('unidades', 'Unidades'),
        ('metros', 'Metros'),
        ('litros', 'Litros'),
        ('kilos', 'Kilos'),
    ]
    
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=100)
    cantidad_disponible = models.IntegerField()
    unidad = models.CharField(max_length=20, choices=TIPOS_UNIDAD, default='unidades')
    
    # ✅ AGREGAR ESTOS CAMPOS NUEVOS:
    marca = models.CharField(
        max_length=50, 
        blank=True, 
        default="", 
        verbose_name="Marca"
    )
    color = models.CharField(
        max_length=30, 
        blank=True, 
        default="", 
        verbose_name="Color"
    )
    
    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"
    
    def __str__(self):
        return f"{self.nombre} ({self.cantidad_disponible} {self.unidad})"

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
    telefono = models.CharField(max_length=20, blank=True, default="")
    red_social = models.CharField(max_length=100, blank=True, default="")
    
    # Información del pedido
    producto_referencia = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion_diseno = models.TextField()
    fecha_requerida = models.DateField(null=True, blank=True)
    plataforma = models.CharField(max_length=20, choices=PLATAFORMAS, default='sitio_web')
    
    # Estados
    estado_pedido = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='solicitado')
    estado_pago = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='pendiente')
    
    # ✅ TOKEN DE SEGUIMIENTO SIN UUID (usando el segundo código como base)
    token_seguimiento = models.CharField(
        max_length=12,  # Más corto y manejable
        unique=True,
        editable=False,
        blank=True
    )
    
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Presupuestos
    presupuesto_aprobado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notas_internas = models.TextField(blank=True, default="")
    
    # Funcionalidad extra: Presupuesto estimado
    presupuesto_estimado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Presupuesto estimado"
    )
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.nombre_cliente}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('seguimiento_pedido', kwargs={'token': self.token_seguimiento})
    
    def calcular_presupuesto(self):
        """Calcula presupuesto automáticamente basado en producto y complejidad"""
        if self.producto_referencia:
            base = float(self.producto_referencia.precio_base)
        else:
            base = 10000
        
        complejidad = min(len(self.descripcion_diseno) / 500, 2.0)
        
        # Contar imágenes de referencia
        try:
            imagenes = self.imagenes_referencia.count()
        except:
            imagenes = 0
        
        factor_imagenes = min(imagenes * 0.15, 0.6)
        
        total = base * (1 + complejidad + factor_imagenes)
        return round(total, 2)
    
    def save(self, *args, **kwargs):
        # ✅ Asegurar token de seguimiento SIN UUID
        if not self.token_seguimiento:
            # Generar token simple de 10 caracteres (ej: "AbC123DeFg")
            self.token_seguimiento = secrets.token_urlsafe(10)[:10]
        
        # Calcular presupuesto estimado si no existe
        if not self.presupuesto_estimado:
            self.presupuesto_estimado = self.calcular_presupuesto()
        
        super().save(*args, **kwargs)

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

