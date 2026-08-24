from unicodedata import category

from django.shortcuts import render

# Create your views here.
from django.db.models import Q, OuterRef, Subquery, Case, When, Value, IntegerField
from rest_framework import generics
from stores.models import Inventory
from products.models import Product
from .pagination import ProductSearchPagination
from .serializers import ProductSearchSerializer, ProductAutocompleteSerializer
from rest_framework.response import Response



class ProductAutocompleteView(generics.ListAPIView):
    serializer_class = ProductAutocompleteSerializer
    pagination_class = None

    def get_queryset(self):
        query = self.request.query_params.get("q", "").strip()

        if not query:
            return Product.objects.none()

        return Product.objects.filter(
            title__icontains=query
        ).order_by("title")[:10]


    

class ProductSearchView(generics.ListAPIView):
    serializer_class = ProductSearchSerializer
    pagination_class = ProductSearchPagination

    def get_queryset(self):
        queryset = Product.objects.select_related("category")

        query = self.request.query_params.get("q")

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(category__name__icontains=query)
            )

        category = self.request.query_params.get("category")

        if category:
            queryset = queryset.filter(category_id=category)

        #Price part
        min_price = self.request.query_params.get("min_price")

        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        max_price = self.request.query_params.get("max_price")

        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Store and stock part
        store_id = self.request.query_params.get("store_id")

        in_stock = self.request.query_params.get("in_stock")

        if store_id:
            if in_stock == "true":
                queryset = queryset.filter(
                    inventory__store_id=store_id,
                    inventory__quantity__gt=0
                )
            elif in_stock == "false":
                queryset = queryset.filter(
                    inventory__store_id=store_id,
                    inventory__quantity=0
                )
            else:
                queryset = queryset.filter(
                    inventory__store_id=store_id
                )
        else:
            if in_stock == "true":
                queryset = queryset.filter(
                    inventory__quantity__gt=0
                )
            elif in_stock == "false":
                queryset = queryset.filter(
                    inventory__quantity=0
                )

        if store_id:
            inventory_quantity = Inventory.objects.filter(
                store_id=store_id,
                product=OuterRef("pk")
            ).values("quantity")[:1]

            queryset = queryset.annotate(
                inventory_quantity=Subquery(inventory_quantity)
            )

        sort = self.request.query_params.get("sort")

        if sort == "price":
            queryset = queryset.order_by("price")
        elif sort == "newest":
            queryset = queryset.order_by("-created_at")
        elif sort == "relevance" and query:
            queryset = queryset.annotate(
                relevance=Case(
                    When(title__iexact=query, then=Value(3)),
                    When(title__icontains=query, then=Value(2)),
                    When(description__icontains=query, then=Value(1)),
                    When(category__name__icontains=query, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            ).order_by("-relevance", "title")

        return queryset
    