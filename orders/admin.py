'''from django.contrib import admin
from .models import Order, OrderItem


admin.site.register(Order)
admin.site.register(OrderItem)'''

from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ("id", "store", "status", "created_at")
    list_filter = ("status", "store")
    ordering = ("-created_at",)


@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ("id", "order", "product", "quantity_requested")
    search_fields = ("product__title",)
    ordering = ("-id",)