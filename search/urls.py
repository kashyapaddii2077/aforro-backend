from django.urls import path
from .views import ProductSearchView, ProductAutocompleteView

urlpatterns = [
    path(
        "products/",
        ProductSearchView.as_view(),
        name="product-search",
    ),
    path(
        "autocomplete/",
        ProductAutocompleteView.as_view(),
        name="product-autocomplete",
    ),
]