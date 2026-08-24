from django.db.models import Sum, Count
import json
from products.models import Product, Category
from stores.models import Store, Inventory
from orders.models import Order


LOW_STOCK_THRESHOLD = 5


def dashboard_callback(request, context):
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_stores = Store.objects.count()
    total_inventory_records = Inventory.objects.count()

    category_data = (
    Category.objects
    .annotate(product_count=Count("products"))
    .order_by("-product_count")
    )
    category_chart_data = json.dumps({
        "labels": [category.name for category in category_data],
        "datasets": [
            {
                "label": "Products",
                "data": [category.product_count for category in category_data],
            }
        ],
    })

    total_stock_units = (
        Inventory.objects.aggregate(total=Sum("quantity"))["total"] or 0
    )

    low_stock_count = Inventory.objects.filter(
        quantity__gt=0,
        quantity__lte=LOW_STOCK_THRESHOLD,
    ).count()

    out_of_stock_count = Inventory.objects.filter(
        quantity=0
    ).count()

    in_stock_count = (
    total_inventory_records
    - low_stock_count
    - out_of_stock_count
    )

    if total_inventory_records:
        in_stock_percentage = round(
        (in_stock_count / total_inventory_records) * 100, 1
        )
        low_stock_percentage = round(
        (low_stock_count / total_inventory_records) * 100, 1
        )
        out_of_stock_percentage = round(
            (out_of_stock_count / total_inventory_records) * 100, 1
        )
    else:
        in_stock_percentage = 0
        low_stock_percentage = 0
        out_of_stock_percentage = 0

    
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(
        status=Order.Status.PENDING
    ).count()
    confirmed_orders = Order.objects.filter(
        status=Order.Status.CONFIRMED
    ).count()
    rejected_orders = Order.objects.filter(
        status=Order.Status.REJECTED
    ).count()
    recent_orders = (
    Order.objects
    .select_related("store")
    .order_by("-created_at")[:5]
    )

    context.update({
        "dashboard_stats": {
            "products": total_products,
            "categories": total_categories,
            "stores": total_stores,
            "inventory_records": total_inventory_records,
            "stock_units": total_stock_units,
            "low_stock": low_stock_count,
            "out_of_stock": out_of_stock_count,
            "orders": total_orders,
            "pending_orders": pending_orders,
            "confirmed_orders": confirmed_orders,
            "rejected_orders": rejected_orders,
            "in_stock": in_stock_count,
            "in_stock_percentage": in_stock_percentage,
            "low_stock_percentage": low_stock_percentage,
            "out_of_stock_percentage": out_of_stock_percentage,
            
        },
        "recent_orders": recent_orders,
        "category_chart_data": category_chart_data,
    })

    return context