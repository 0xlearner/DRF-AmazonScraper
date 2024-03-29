from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProductList,
    CategoryViewset,
    SellerViewset,
    ProductListApiView,
    AllProductsViewset,
    ReportView,
)

category_list = CategoryViewset.as_view({"get": "list", "post": "create"})
category_detail = CategoryViewset.as_view(
    {"get": "retrieve", "put": "update", "delete": "destroy"}
)

router = DefaultRouter(trailing_slash=False)
router.register("sellers", SellerViewset)

urlpatterns = [
    path("", include(router.urls)),
    path("products/", ProductList.as_view()),
    path("products-all/", AllProductsViewset.as_view()),
    path("product-filter/", ProductListApiView.as_view()),
    path("add-products/", ReportView.as_view()),
    path("categories/", category_list, name="categories-list"),
    path("categories/<int:pk>/", category_detail, name="categories-detail"),
]
