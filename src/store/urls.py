from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login', template_name='store/login.html'), name='logout'),
    path('register/', views.register, name='register'),
    path('products/', views.product_list, name='product_list'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order/create/', views.create_order, name='create_order'),
    path('order/<int:order_id>/pdf/', views.order_pdf, name='order_pdf'),
    
    # Dashboard views (previously admin views)
    path('dashboard/orders/', views.admin_orders, name='admin_orders'),
    path('dashboard/order/<int:order_id>/update/', views.admin_update_order, name='admin_update_order'),
]
