from django.urls import path
from . import views
from django.views.generic import TemplateView
urlpatterns = [
    path('product-details/<slug:slug>', views.product_details, name='product_details'),
    path('add-to-cart/<int:id>', views.add_to_cart, name='add_to_cart'),
    path('show-cart/', views.show_cart, name='show_cart'),
    path('increse-cart/', views.increase_cart, name='increase_cart'),
    path('checkout/', views.check_out, name='check_out'),
    path('placed-oder/', views.placed_oder, name='placed_oder'),
    path('cupon-apply/', views.cupon_apply, name='cupon_apply'),
    path('add-product-review/', views.add_product_review_and_rating, name='add_product_review_and_rating'),
    path('save-shipping-address/', views.save_shipping_address, name='save_shipping_address'),
    path('all-products/', views.all_products, name='all_products'),
    path('bottom-area/', views.bottom_area, name='bottom_area'),
    path('search/', views.search_products, name='search_products'),
    path('submit-complain/', views.submit_complain, name='submit_complain'),
    path('payment-methods/', views.payment_methods, name='payment_methods'),
    path('policies/', TemplateView.as_view(template_name="policies.html"), name="policies"),
    path("resell-products/", views.resell_products, name="resell_products"),
    path('add-address/', views.add_address, name='add_address'),

]