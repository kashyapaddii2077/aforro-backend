'''from django.contrib import admin
from .models import Store, Inventory


admin.site.register(Store)
admin.site.register(Inventory)'''

from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Store, Inventory


@admin.register(Store)
class StoreAdmin(ModelAdmin):
    list_display = ("id", "name", "location")
    search_fields = ("name", "location")
    ordering = ("name",)


@admin.register(Inventory)
class InventoryAdmin(ModelAdmin):
    list_display = ("id", "store", "product", "quantity")
    search_fields = ("store__name", "product__title")
    list_filter = ("store",)
    ordering = ("store", "product")