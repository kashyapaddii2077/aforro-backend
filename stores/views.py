from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Store, Inventory
from .serializers import InventorySerializer


class StoreInventoryView(APIView):

    def get(self, request, store_id):
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return Response(
                {"detail": "Store not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        inventory = (
            Inventory.objects
            .filter(store=store)
            .select_related(
                "product",
                "product__category",
            )
            .order_by("product__title")
        )

        serializer = InventorySerializer(
            inventory,
            many=True,
        )

        return Response(serializer.data)