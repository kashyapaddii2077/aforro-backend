'''from django.contrib import admin
from .models import Category, Product


admin.site.register(Category)
admin.site.register(Product)'''
#Changes
from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ("id", "title", "category", "price", "created_at")
    search_fields = ("title", "description")
    list_filter = ("category",)
    ordering = ("-created_at",)