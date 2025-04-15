from django import forms
from .models import Order
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['tipo_servico', 'quantidade_servico', 'preco_unitario', 'observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('tipo_servico', css_class='form-group col-md-12 mb-3'),
                css_class='row'
            ),
            Row(
                Column('quantidade_servico', css_class='form-group col-md-6 mb-3'),
                Column('preco_unitario', css_class='form-group col-md-6 mb-3'),
                css_class='row'
            ),
            'observacoes',
            Submit('submit', 'Salvar', css_class='btn btn-primary mt-3')
        )

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'status',
            Submit('submit', 'Atualizar Status', css_class='btn btn-primary mt-3')
        )

    def clean_status(self):
        status = self.cleaned_data.get('status')
        if self.instance.status != 'pendente' and status != self.instance.status:
            raise forms.ValidationError('Não é possível alterar o status de uma ordem que já foi aprovada ou rejeitada.')
        return status
