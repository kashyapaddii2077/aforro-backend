from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product
from stores.models import Store, Inventory

from .models import Order, OrderItem
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
)


class OrderCreateView(APIView):

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        store_id = serializer.validated_data["store_id"]
        items = serializer.validated_data["items"]

        store = get_object_or_404(Store, id=store_id)

        with transaction.atomic():

            product_ids = [
                item["product_id"]
                for item in items
            ]

            products = Product.objects.filter(
                id__in=product_ids
            )

            product_map = {
                product.id: product
                for product in products
            }

            # Check that every requested product exists
            missing_products = [
                product_id
                for product_id in product_ids
                if product_id not in product_map
            ]

            if missing_products:
                return Response(
                    {
                        "detail": "One or more products do not exist.",
                        "product_ids": missing_products,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Lock inventory rows while processing the order
            inventory_rows = (
                Inventory.objects
                .select_for_update()
                .filter(
                    store=store,
                    product_id__in=product_ids,
                )
            )

            inventory_map = {
                inventory.product_id: inventory
                for inventory in inventory_rows
            }

            # Check whether all requested products have inventory
            missing_inventory = [
                product_id
                for product_id in product_ids
                if product_id not in inventory_map
            ]

            if missing_inventory:
                order = Order.objects.create(
                    store=store,
                    status=Order.Status.REJECTED,
                )

                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product_id=item["product_id"],
                        quantity_requested=item["quantity_requested"],
                    )

                return Response(
                    OrderSerializer(order).data,
                    status=status.HTTP_201_CREATED,
                )

            # Check stock BEFORE changing anything
            insufficient_items = []

            for item in items:
                product_id = item["product_id"]
                requested = item["quantity_requested"]

                inventory = inventory_map[product_id]

                if inventory.quantity < requested:
                    insufficient_items.append({
                        "product_id": product_id,
                        "requested": requested,
                        "available": inventory.quantity,
                    })

            # If even one item has insufficient stock
            if insufficient_items:
                order = Order.objects.create(
                    store=store,
                    status=Order.Status.REJECTED,
                )

                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product_id=item["product_id"],
                        quantity_requested=item["quantity_requested"],
                    )

                response = OrderSerializer(order).data
                response["insufficient_items"] = insufficient_items

                return Response(
                    response,
                    status=status.HTTP_201_CREATED,
                )

            # Everything is available → deduct stock
            order = Order.objects.create(
                store=store,
                status=Order.Status.CONFIRMED,
            )

            for item in items:
                product_id = item["product_id"]
                quantity = item["quantity_requested"]

                inventory = inventory_map[product_id]

                inventory.quantity -= quantity
                inventory.save(update_fields=["quantity"])

                OrderItem.objects.create(
                    order=order,
                    product_id=product_id,
                    quantity_requested=quantity,
                )

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )
    

class StoreOrderListView(APIView):

    def get(self, request, store_id):
        try:
            Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return Response(
                {"detail": "Store not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        orders = (
            Order.objects
            .filter(store_id=store_id)
            .annotate(
                total_items=Sum("items__quantity_requested")
            )
            .order_by("-created_at")
        )

        serializer = OrderListSerializer(
            orders,
            many=True,
        )

        return Response(serializer.data)