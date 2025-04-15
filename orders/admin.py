from django.contrib import admin
from django.utils.html import format_html
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo_servico', 'quantidade_servico', 'preco_unitario', 
                    'total_price', 'status_badge', 'created_by', 'approved_by', 
                    'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['tipo_servico', 'created_by__username', 'approved_by__username']
    readonly_fields = ['created_at', 'updated_at', 'total_price']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    list_per_page = 20

    fieldsets = (
        ('Informações do Serviço', {
            'fields': ('tipo_servico', 'quantidade_servico', 'preco_unitario', 'total_price')
        }),
        ('Status e Observações', {
            'fields': ('status', 'observacoes')
        }),
        ('Informações do Sistema', {
            'fields': ('created_by', 'approved_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'pendente': 'warning',
            'aprovada': 'success',
            'rejeitada': 'danger'
        }
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            colors[obj.status],
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        elif 'status' in form.changed_data:  # If status was changed
            obj.approved_by = request.user
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ['https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css']
        }

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('created_by',)
        return self.readonly_fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)

    def has_change_permission(self, request, obj=None):
        if not obj:
            return True
        if request.user.is_superuser:
            return True
        if request.user.is_staff:
            return True
        return obj.created_by == request.user and obj.status == 'pendente'

    def has_delete_permission(self, request, obj=None):
        if not obj:
            return True
        if request.user.is_superuser:
            return True
        return obj.created_by == request.user and obj.status == 'pendente'
