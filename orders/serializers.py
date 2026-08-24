from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity_requested = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    store_id = serializers.IntegerField(min_value=1)
    items = OrderItemInputSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError(
                "At least one item is required."
            )

        product_ids = [item["product_id"] for item in value]

        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError(
                "A product cannot appear more than once in an order."
            )

        return value


class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(
        source="product.title",
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_title",
            "quantity_requested",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "store",
            "status",
            "created_at",
            "items",
        ]


class OrderListSerializer(serializers.ModelSerializer):
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "created_at",
            "total_items",
        ]