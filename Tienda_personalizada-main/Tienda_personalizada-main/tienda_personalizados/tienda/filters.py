import django_filters
from .models import Pedido, Producto
from django import forms

class PedidoFilter(django_filters.FilterSet):
    fecha_inicio = django_filters.DateFilter(
        field_name='fecha_creacion',
        lookup_expr='gte',
        label='Fecha Inicio',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    fecha_fin = django_filters.DateFilter(
        field_name='fecha_creacion',
        lookup_expr='lte',
        label='Fecha Fin',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    estado = django_filters.MultipleChoiceFilter(
        field_name='estado_pedido',
        choices=Pedido.ESTADOS_PEDIDO,
        label='Estado de Pedido',
        widget=forms.CheckboxSelectMultiple
    )

    plataforma = django_filters.ChoiceFilter(
        choices=Pedido.PLATAFORMAS,
        label='Plataforma de Origen',
        empty_label='Todas las plataformas'
    )

    class meta:
        model = Pedido
        fields = ['fecha_inicio', 'fecha_fin', 'estado', 'plataforma']