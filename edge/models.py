from django.contrib.auth.models import User
from django.db import models

SIZE_CHOICES = [
    ('S', 'S'),
    ('M', 'SM'),
    ('L', 'L'),
    ('XL', 'XL'),
    ('XXL', 'XXL'),
    ('S M', 'S M'),
    ('M L', 'M L'),
    ('L XL', 'L XL'),
    ('XL XXL', 'XL XXL'),
    ('S M L', 'S M L'),
    ('M L XL', 'M L XL'),
    ('L XL XXL', 'L XL XXL'),
    ('S M L XL', 'S M L XL'),
    ('M L XL XXL', 'M L XL XXL'),
    ('S M L XL XXL', 'S M L XL XXL'),
]
class Flower(models.Model):

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    size = models.CharField(max_length=12, choices=SIZE_CHOICES)
    price_s = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Price for size S")
    price_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Price for size M")
    price_l = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Price for size L")
    price_xl = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Price for size XL")
    price_xxl = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Price for size XXL")
    image = models.ImageField(upload_to='flower_images/')  # Add image field

    def __str__(self):
        return self.name
    
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flower_id = models.IntegerField()
    flower_size = models.CharField(max_length=12, choices=SIZE_CHOICES)
    flower_num = models.IntegerField()

    def __str__(self):
        return f"User: {self.user}, Flower ID: {self.flower_id}, Size: {self.flower_size}, Quantity: {self.flower_num}" 