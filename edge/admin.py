from django.contrib import admin
from .models import Flower, CartItem

# Register your models here.
admin.site.register(Flower)
admin.site.register(CartItem)