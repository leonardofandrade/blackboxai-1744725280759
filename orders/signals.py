from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Order

User = get_user_model()

@receiver(post_save, sender=Order)
def notify_order_status(sender, instance, created, **kwargs):
    """
    Signal to send notifications when:
    1. A new order is created (notify staff)
    2. An order status is changed (notify creator)
    """
    if created:
        # Notify all staff users about new order
        staff_users = User.objects.filter(is_staff=True)
        staff_emails = [user.email for user in staff_users if user.email]
        
        if staff_emails:
            send_mail(
                subject='Nova Ordem de Serviço Criada',
                message=f'''Uma nova ordem de serviço foi criada:
                
Tipo de Serviço: {instance.tipo_servico}
Quantidade: {instance.quantidade_servico}
Preço Unitário: R$ {instance.preco_unitario}
Criado por: {instance.created_by.username}
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=staff_emails,
                fail_silently=True,
            )
    else:
        # Check if status has changed and notify the creator
        if instance.tracker.has_changed('status'):
            if instance.created_by.email:
                send_mail(
                    subject='Status da Ordem de Serviço Atualizado',
                    message=f'''O status da sua ordem de serviço foi atualizado:
                    
Ordem: {instance.tipo_servico}
Novo Status: {instance.get_status_display()}
Atualizado por: {instance.approved_by.username if instance.approved_by else "Sistema"}
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.created_by.email],
                    fail_silently=True,
                )

def ready():
    """
    Import and register signals when the app is ready.
    Add this to apps.py OrdersConfig.ready()
    """
    post_save.connect(notify_order_status, sender=Order)
