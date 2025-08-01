from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('cart/', views.view_cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('upload-csv/', views.upload_csv, name='upload_csv'),
    path('upload-success/', views.upload_success, name='upload_success'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # New Customer Authentication Routes
    path('register/', views.register_customer, name='register'),
    path('login/', views.login_customer, name='login'),
    path('logout/', views.logout_customer, name='logout'),
]
