from django.db import models
from django.conf import settings
from django.urls import reverse
from model_utils import FieldTracker

class Order(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
    ]

    tipo_servico = models.CharField('Tipo de Serviço', max_length=100)
    quantidade_servico = models.PositiveIntegerField('Quantidade')
    preco_unitario = models.DecimalField('Preço Unitário', max_digits=10, decimal_places=2)
    observacoes = models.TextField('Observações', blank=True, null=True)
    status = models.CharField(
        'Status',
        max_length=10,
        choices=STATUS_CHOICES,
        default='pendente'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Criado por',
        on_delete=models.CASCADE,
        related_name='orders_created'
    )
    
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Aprovado/Rejeitado por',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders_approved'
    )
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Ordem de Serviço'
        verbose_name_plural = 'Ordens de Serviço'
        ordering = ['-created_at']

    def __str__(self):
        return f'OS #{self.id} - {self.tipo_servico} ({self.status})'

    def get_absolute_url(self):
        return reverse('order_detail', args=[str(self.id)])

    @property
    def total_price(self):
        return self.quantidade_servico * self.preco_unitario

    # Track status changes for notifications
    tracker = FieldTracker(fields=['status'])
