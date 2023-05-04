from django.db import models
from services.mixins import DateMixin
from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
from services.uploader import Uploader

User = get_user_model()

# Create your models here.


from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

class Category(MPTTModel, DateMixin):
    name = models.CharField(max_length=50)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self) -> str:
        return self.name


class Product(DateMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    description = RichTextField(blank=True, null=True)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    wishlist = models.ManyToManyField(User, blank=True, related_name='product_wishlist')

    def __str__(self) -> str:
        return self.name



class ProductImage(DateMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=Uploader.upload_image_to_product)

    def __str__(self) -> str:
        return self.product.name


class Basket(DateMixin):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.email} --> {self.user.fullname}"

    class Meta:
        ordering = ('-created_at', )
        verbose_name = 'Basket'
        verbose_name_plural = 'Basket'