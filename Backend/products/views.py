import pytz
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status, exceptions

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


class ReportView(APIView):
    """
    POST method ONLY
    """

    def post(self, request):
        data = request.data
        self.validate(data)
        category = data.get("category")
        products = data.get("products")
        date = data.get("date")
        category_obj = self.get_category(category)
        response = self.handle_products(products, category_obj, date)
        return Response({"message": response})

    def handle_products(self, products, category_obj, date):
        response = []
        for product in products:
            seller_obj, _ = Seller.objects.get_or_create(name=product.get("seller"))
            date_formatted = datetime.strptime(date, "%d/%m/%Y %H:%M:%S")
            date_formatted = pytz.utc.localize(date_formatted)
            obj, created = Products.objects.update_or_create(
                asin=product.get("asin"),
                seller=seller_obj,
                category=category_obj,
                defaults={
                    "photo": product.get("photo"),
                    "updated": date_formatted,
                    "price": product.get("price"),
                    "title": product.get("title"),
                    "rating": product.get("rating"),
                    "review_count": product.get("review_count"),
                },
            )
            if created:
                response.append(f"{obj.asin} - {obj.title} - created")
            else:
                response.append(f"{obj.asin} - {obj.title} - updated")
        return response

    def get_category(self, category):
        obj, _ = Category.objects.get_or_create(name=category.title())
        return obj

    def validate(self, data):
        if data.get("category") is None:
            raise exceptions.ValidationError("category is null")
        if data.get("products") is None:
            raise exceptions.ValidationError("products is null")
        if data.get("date") is None:
            raise exceptions.ValidationError("date is null")
