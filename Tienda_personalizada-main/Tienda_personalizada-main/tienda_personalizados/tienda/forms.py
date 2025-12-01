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
            'producto_referencia', 'descripcion_diseno', 'fecha_requerida',
            'plataforma'
        ]
        widgets = {
            'descripcion_diseno': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Describe tu diseño, colores, texto, estilo, etc.'
            }),
            'fecha_requerida': forms.DateInput(attrs={'type': 'date'}),
            'plataforma': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'plataforma': '¿Dónde realizó el pedido?',
            'descripcion_diseno': 'Descripción del diseño *',
            'fecha_requerida': 'Fecha requerida (opcional)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer el producto_referencia opcional
        self.fields['producto_referencia'].required = False
        self.fields['producto_referencia'].empty_label = "Seleccione un producto (opcional)"
        
    def save(self, commit=True):
        pedido = super().save(commit=commit)
        
        # Guardar imágenes de referencia si se proporcionaron
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
