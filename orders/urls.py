from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order_list'),
    path('novo/', views.OrderCreateView.as_view(), name='order_create'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/editar/', views.OrderUpdateView.as_view(), name='order_update'),
    path('<int:pk>/excluir/', views.OrderDeleteView.as_view(), name='order_delete'),
]
