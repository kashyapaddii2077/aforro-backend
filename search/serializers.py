from rest_framework import serializers

from products.models import Product



class ProductSearchSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name", read_only=True)

    inventory_quantity = serializers.IntegerField(
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "category",
            "inventory_quantity",
        ]


class ProductAutocompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "title",
        ]