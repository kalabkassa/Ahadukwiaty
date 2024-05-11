from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
        path("", views.index, name="home"),
        path("aboutus/", views.aboutus, name='aboutus' ),
        path("contactus/", views.contact, name="contactus"),
        path("flower/", views.flowers, name="flower"),
        path("delivery/", views.delivery, name="delivery"),
        path("wishlist/", views.wishlist, name="wishlist"),
        path("products/<int:id>/", views.products, name="products"),
        path("checkout/", views.checkout, name="checkout"),
        path('add_to_cart/', views.add_to_cart, name="add_to_cart"),
        path('remove_from_cart/', views.remove_from_cart, name="remove_from_cart"),
        path('get_cart/', views.get_cart, name="get_cart"),
        path('updatedb_cart/', views.updatedb_cart, name="updatedb_cart"),
        path("payment/create_payment/", views.create_payment, name="payment"),
        path("signup/", views.signup, name='signup'),
        path("login/" , views.login_view, name='login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)