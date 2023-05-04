from rest_framework import serializers
from products.models import Product, Category
from django.contrib.auth import get_user_model

User = get_user_model()


class WishlistSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'fullname')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"


class ProductListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        # fields = "__all__"
        exclude = ('description', )
        extra_kwargs = {
            "user": {"read_only": True},
            "total_price": {"read_only": True}
        }

    def to_representation(self, instance):
        repr_ = super().to_representation(instance)
        repr_['total_price'] = instance.price - (instance.discount_price or 0)
        repr_["wish_count"] = instance.wishlist.count()
        repr_['category'] = CategorySerializer(instance.category).data
        repr_['wishlist'] = WishlistSerializer(instance.wishlist.all(), many=True).data
        return repr_


class ProductCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ("user", "name", "description", "price", "discount_price", "category")
        extra_kwargs = {
            "user": {"read_only": True},
        }

    def to_representation(self, instance):
        repr_ = super().to_representation(instance)
        repr_['category'] = CategorySerializer(instance.category).data
        repr_['user'] = instance.user.email
        return repr_

    def validate(self, attrs):
        price = attrs.get('price', None)
        if price < 0:
            raise serializers.ValidationError({"error": "Price must be positive number."})

        return super().validate(attrs)

    def create(self, validated_data):
        queryset = Product.objects.create(**validated_data)
        return queryset
