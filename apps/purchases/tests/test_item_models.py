from django.test import TestCase
from apps.purchases.models import Product, Item
from ddf import G


class ItemModel(TestCase):

    def setUp(self):
        self.product1 = G(Product, stock=100)
        self.product2 = G(Product, stock=20)
        self.item_product_1 = G(Item, producto=self.product1, cantidad=10)
        self.item_product_2 = G(Item, producto=self.product2, cantidad=23)
        self.item_product_3 = G(Item, producto=self.product1, cantidad=10)

    def test_item_increment_stock(self):
        self.item_product_1.increment_stock()
        self.assertEqual(self.product1.stock, 110)

    def test_item_decrement_stock(self):
        self.item_product_1.decrement_stock()
        self.assertEqual(self.product1.stock, 90)

    def test_item_decrement_to_negative_stock(self):
        self.item_product_2.decrement_stock()
        self.assertEqual(self.product2.stock, -3)

    def test_item_update_correctly(self):
        self.item_product_1.decrement_stock()
        self.item_product_1.increment_stock()
        self.assertEqual(self.product1.stock, 100)

    def test_item_update_correctly_with_diferent_items(self):
        self.item_product_3.decrement_stock()
        self.item_product_1.increment_stock()
        self.assertEqual(self.product1.stock, 100)