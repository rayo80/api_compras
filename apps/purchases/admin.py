from django.contrib import admin

from apps.purchases.models import Purchase, Supplier, Item

# Register your models here.
admin.site.register(Purchase)
admin.site.register(Supplier)
admin.site.register(Item)
