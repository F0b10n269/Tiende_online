from django import forms
from .models import Pedido, ImagenReferencia

class SolicitudPedidoForm(forms.ModelForm):
    imagen_referencia_1 = forms.ImageField(required=False, label="Imagen de referencia 1")
    imagen_referencia_2 = forms.ImageField(required=False, label="Imagen de referencia 2")
    imagen_referencia_3 = forms.ImageField(required=False, label="Imagen de referencia 3")
    
    class Meta:
        model = Pedido
        fields = [
            'nombre_cliente', 'email', 'telefono', 'red_social',
            'producto_referencia', 'descripcion_diseno', 'fecha_requerida'
            # ❌ QUITAMOS 'plataforma' del formulario - se asigna automáticamente
        ]
        widgets = {
            'descripcion_diseno': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe tu diseño personalizado...'}),
            'fecha_requerida': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer el producto de referencia opcional
        self.fields['producto_referencia'].required = False
        self.fields['producto_referencia'].empty_label = "Selecciona un producto (opcional)"
    
    def save(self, commit=True):
        # ✅ Asignar automáticamente "sitio_web" como plataforma
        self.instance.plataforma = 'sitio_web'
        
        # ✅ Estados automáticos: Solicitado y Pendiente
        self.instance.estado_pedido = 'solicitado'
        self.instance.estado_pago = 'pendiente'
        self.instance.presupuesto_estimado = self.instance.calcular_presupuesto()
        
        pedido = super().save(commit=commit)
        
        # Guardar imágenes de referencia
        if commit:
            for i in range(1, 4):
                imagen_field = f'imagen_referencia_{i}'
                imagen = self.cleaned_data.get(imagen_field)
                if imagen:
                    ImagenReferencia.objects.create(
                        pedido=pedido,
                        imagen=imagen,
                        descripcion=f"Imagen de referencia {i} enviada por el cliente"
                    )
        
        return pedido
