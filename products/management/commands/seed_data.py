from decimal import Decimal
import random

from django.core.management.base import BaseCommand
from faker import Faker

from products.models import Category, Product
from stores.models import Store, Inventory


class Command(BaseCommand):
    help = "Generate seed data for categories, products, stores, and inventory"

    def handle(self, *args, **options):
        fake = Faker()

        # -------------------------
        # 1. Categories
        # -------------------------
        category_names = [
            "Electronics",
            "Clothing",
            "Home & Kitchen",
            "Books",
            "Sports",
            "Beauty",
            "Grocery",
            "Toys",
            "Automotive",
            "Furniture",
            "Accessories",
            "Stationery",
        ]

        categories = []

        for name in category_names:
            category, _ = Category.objects.get_or_create(name=name)
            categories.append(category)

        self.stdout.write(
            self.style.SUCCESS(
                f"Categories ready: {len(categories)}"
            )
        )

        # -------------------------
        # 2. Products
        # -------------------------
        existing_products = Product.objects.count()

        products_to_create = []

        for _ in range(max(0, 1000 - existing_products)):
            product = Product(
                title=fake.unique.catch_phrase(),
                description=fake.text(max_nb_chars=200),
                price=Decimal(str(round(random.uniform(10, 5000), 2))),
                category=random.choice(categories),
            )

            products_to_create.append(product)

        Product.objects.bulk_create(
            products_to_create,
            batch_size=500,
        )

        products = list(Product.objects.all())

        self.stdout.write(
            self.style.SUCCESS(
                f"Products ready: {len(products)}"
            )
        )

        # -------------------------
        # 3. Stores
        # -------------------------
        store_names = [
            "Central Store",
            "City Mart",
            "Smart Shop",
            "Daily Needs",
            "Super Store",
            "Metro Market",
            "Prime Store",
            "Value Mart",
            "Fresh Market",
            "Quick Shop",
            "Urban Store",
            "Mega Mart",
            "Best Buy Store",
            "Neighborhood Mart",
            "Express Store",
            "Green Market",
            "Family Store",
            "Choice Mart",
            "Grand Store",
            "Local Market",
        ]

        stores = []

        for name in store_names:
            store, _ = Store.objects.get_or_create(
                name=name,
                defaults={
                    "location": fake.city(),
                },
            )
            stores.append(store)

        self.stdout.write(
            self.style.SUCCESS(
                f"Stores ready: {len(stores)}"
            )
        )

        # -------------------------
        # 4. Inventory
        # -------------------------
        inventory_to_create = []

        for store in stores:
            selected_products = random.sample(
                products,
                min(300, len(products)),
            )

            existing_product_ids = set(
                Inventory.objects.filter(
                    store=store,
                    product__in=selected_products,
                ).values_list("product_id", flat=True)
            )

            for product in selected_products:
                if product.id not in existing_product_ids:
                    inventory_to_create.append(
                        Inventory(
                            store=store,
                            product=product,
                            quantity=random.randint(1, 100),
                        )
                    )

        Inventory.objects.bulk_create(
            inventory_to_create,
            batch_size=1000,
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Seed data generation completed successfully!"
            )
        )