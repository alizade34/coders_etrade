from rest_framework.response import Response
from rest_framework import generics
from products.models import Product
from .serializers import ProductListSerializer, ProductCreateSerializer
from django.db.models import F, FloatField
from django.db.models.functions import Coalesce
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .paginations import CustomPagination
from .permissions import IsOwnerOrReadOnly
from .filters import ProductFilter
from django_filters.rest_framework.backends import DjangoFilterBackend


class ProductListView(generics.ListAPIView):

    pagination_class = CustomPagination
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = ProductFilter

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user).annotate(
            discount=Coalesce('discount_price', 0, output_field=FloatField()),
            total_price=F("price")-F('discount')
        )

    def get_serializer_class(self):
        return ProductListSerializer

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.annotate(
        discount=Coalesce('discount_price', 0, output_field=FloatField()),
        total_price=F("price") - F('discount')
    ).all()

    def get_serializer_class(self):
        return ProductListSerializer

    def get_object(self):
        return self.queryset.get(id=int(self.kwargs.get("id")))

    lookup_field = "id"


class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductCreateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ProductUpdateView(generics.UpdateAPIView):

    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    queryset = Product.objects.annotate(
        discount=Coalesce('discount_price', 0, output_field=FloatField()),
        total_price=F("price") - F('discount')
    ).all()
    serializer_class = ProductListSerializer
    lookup_field = "id"


class ProductDeleteView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    queryset = Product.objects.annotate(
        discount=Coalesce('discount_price', 0, output_field=FloatField()),
        total_price=F("price") - F('discount')
    ).all()
    serializer_class = ProductListSerializer
    lookup_field = "id"


