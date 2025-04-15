from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.db.models import Q
from .models import Order
from .forms import OrderForm, OrderStatusForm

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(created_by=self.request.user)
        return queryset.select_related('created_by', 'approved_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_staff'] = self.request.user.is_staff
        return context

class OrderDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def test_func(self):
        order = self.get_object()
        return self.request.user.is_staff or order.created_by == self.request.user

class OrderCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:order_list')
    success_message = "Ordem de serviço criada com sucesso!"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.status = 'pendente'
        response = super().form_valid(form)
        # Aqui você pode adicionar a lógica de notificação para os usuários staff
        return response

class OrderUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Order
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:order_list')
    success_message = "Ordem de serviço atualizada com sucesso!"

    def get_form_class(self):
        if self.request.user.is_staff:
            return OrderStatusForm
        return OrderForm

    def test_func(self):
        order = self.get_object()
        if self.request.user.is_staff:
            return True
        return order.created_by == self.request.user and order.status == 'pendente'

    def form_valid(self, form):
        order = form.instance
        if self.request.user.is_staff:
            order.approved_by = self.request.user
            # Aqui você pode adicionar a lógica de notificação para o usuário que criou a ordem
        response = super().form_valid(form)
        return response

    def handle_no_permission(self):
        messages.error(self.request, "Você não tem permissão para editar esta ordem de serviço.")
        return redirect('orders:order_list')

class OrderDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Order
    template_name = 'orders/order_confirm_delete.html'
    success_url = reverse_lazy('orders:order_list')
    success_message = "Ordem de serviço excluída com sucesso!"

    def test_func(self):
        order = self.get_object()
        return (order.created_by == self.request.user and 
                order.status == 'pendente') or self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def handle_no_permission(self):
        messages.error(self.request, "Você não tem permissão para excluir esta ordem de serviço.")
        return redirect('orders:order_list')
