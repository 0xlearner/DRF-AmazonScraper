from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    CategorySerializer,
    SellerSerializer,
    ProductSerializer,
    ProductsAllInfoSerializer,
)
from .models import Products, Category, Seller


class ProductList(APIView):
    """
    List all Products, or create a new product.
    """

    def get(self, request):
        products = Products.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductListApiView(ListAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer

    filter_fields = ("category__id",)

    search_fields = ("title",)


class AllProductsViewset(ListAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductsAllInfoSerializer


class CategoryViewset(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SellerViewset(ModelViewSet):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer
