from django.test import TestCase
from rest_framework.test import APIClient
from api.models import User, Business, Menu, MenuCategory, MenuItem


class ReorderMenuTests(TestCase):
    """Consolidated tests for the /menus/{id}/reorder/ endpoint.

    The tests create a business owner, a menu, categories and items via the API
    (using JSON posts) and then exercise happy and error paths for the reorder endpoint.
    """

    def setUp(self):
        # Business owner and business
        self.owner = User.objects.create_user(email='owner2@example.com', password='pass1234', account_type='business')
        self.business = Business.objects.create(name='ReorderBiz', owner=self.owner)

        # Authenticated test client
        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

        # Create menu
        resp = self.client.post('/api/v1/menus/', {'name': 'Reorder Menu', 'business': self.business.business_id}, format='json')
        self.assertEqual(resp.status_code, 201)
        self.menu_id = resp.data.get('menu_id')

        # Create two categories
        r = self.client.post('/api/v1/menu-categories/', {'menu': self.menu_id, 'name': 'Cat A', 'order': 0}, format='json')
        self.assertEqual(r.status_code, 201)
        self.cat_a_id = r.data.get('category_id')

        r = self.client.post('/api/v1/menu-categories/', {'menu': self.menu_id, 'name': 'Cat B', 'order': 1}, format='json')
        self.assertEqual(r.status_code, 201)
        self.cat_b_id = r.data.get('category_id')

        # Create items
        r1 = self.client.post('/api/v1/menu-items/', {'menu': self.menu_id, 'category': self.cat_a_id, 'name': 'Item 1', 'price': '10.00', 'currency': 'ZAR', 'available': True}, format='json')
        self.assertEqual(r1.status_code, 201)
        self.item1_id = r1.data.get('item_id')

        r2 = self.client.post('/api/v1/menu-items/', {'menu': self.menu_id, 'category': self.cat_b_id, 'name': 'Item 2', 'price': '20.00', 'currency': 'ZAR', 'available': True}, format='json')
        self.assertEqual(r2.status_code, 201)
        self.item2_id = r2.data.get('item_id')

    def test_reorder_happy_path(self):
        payload = {
            'categories': [
                {'category_id': self.cat_a_id, 'order': 1},
                {'category_id': self.cat_b_id, 'order': 0},
            ],
            'items': [
                {'item_id': self.item1_id, 'category_id': self.cat_b_id, 'order': 0},
                {'item_id': self.item2_id, 'category_id': self.cat_a_id, 'order': 0},
            ]
        }

        resp = self.client.post(f'/api/v1/menus/{self.menu_id}/reorder/', payload, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.get('status'), 'ok')

        # Refresh from DB and assert
        ca = MenuCategory.objects.get(category_id=self.cat_a_id)
        cb = MenuCategory.objects.get(category_id=self.cat_b_id)
        i1 = MenuItem.objects.get(item_id=self.item1_id)
        i2 = MenuItem.objects.get(item_id=self.item2_id)

        self.assertEqual(ca.order, 1)
        self.assertEqual(cb.order, 0)
        self.assertEqual(i1.category.category_id, self.cat_b_id)
        self.assertEqual(i2.category.category_id, self.cat_a_id)
        self.assertEqual(i1.order, 0)
        self.assertEqual(i2.order, 0)

    def test_reorder_invalid_category(self):
        invalid_cat = 999999
        payload = {'categories': [{'category_id': invalid_cat, 'order': 0}], 'items': []}
        resp = self.client.post(f'/api/v1/menus/{self.menu_id}/reorder/', payload, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('errors', resp.data)

    def test_reorder_invalid_item(self):
        invalid_item = 999999
        payload = {'categories': [], 'items': [{'item_id': invalid_item, 'category_id': self.cat_a_id, 'order': 0}]}
        resp = self.client.post(f'/api/v1/menus/{self.menu_id}/reorder/', payload, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('errors', resp.data)

    def test_reorder_fails_with_foreign_category(self):
        # create another business/menu/category that doesn't belong to our owner
        other_user = User.objects.create_user(email='other@example.com', password='x', account_type='business')
        other_biz = Business.objects.create(name='OtherBiz', owner=other_user)
        other_menu = Menu.objects.create(name='Other', business=other_biz)
        foreign_cat = MenuCategory.objects.create(menu=other_menu, name='Foreign', order=0)

        payload = {'categories': [{'category_id': foreign_cat.category_id, 'order': 0}], 'items': []}
        resp = self.client.post(f'/api/v1/menus/{self.menu_id}/reorder/', payload, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('errors', resp.data)

    def test_reorder_fails_with_foreign_item(self):
        other_user = User.objects.create_user(email='other2@example.com', password='x', account_type='business')
        other_biz = Business.objects.create(name='OtherBiz2', owner=other_user)
        other_menu = Menu.objects.create(name='Other2', business=other_biz)
        foreign_item = MenuItem.objects.create(menu=other_menu, name='Bad', price='1.00', currency='ZAR', available=True)

        payload = {'categories': [], 'items': [{'item_id': foreign_item.item_id, 'category_id': None, 'order': 0}]}
        resp = self.client.post(f'/api/v1/menus/{self.menu_id}/reorder/', payload, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('errors', resp.data)

    def test_reorder_malformed_payloads(self):
        # categories not a list
        resp = self.client.post(f'/api/v1/menus/{self.menu_id}/reorder/', {'categories': 'invalid', 'items': []}, format='json')
        self.assertEqual(resp.status_code, 400)

        # items not a list
        resp2 = self.client.post(f'/api/v1/menus/{self.menu_id}/reorder/', {'categories': [], 'items': {'x': 1}}, format='json')
        self.assertEqual(resp2.status_code, 400)
from django.test import TestCase
from rest_framework.test import APIClient
from api.models import User, Business, Menu, MenuCategory, MenuItem


class ReorderMenuTests(TestCase):
    def setUp(self):
        # Business owner
        self.owner = User.objects.create_user(email='owner2@example.com', password='pass1234', account_type='business')
        self.business = Business.objects.create(name='TestBiz2', owner=self.owner)

        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

    def _create_menu_with_categories_items(self):
        resp = self.client.post('/api/v1/menus/', {'name': 'ReorderMenu', 'business': self.business.business_id})
        menu_id = resp.data.get('menu_id')

        # categories
        r1 = self.client.post('/api/v1/menu-categories/', {'menu': menu_id, 'name': 'Cat A', 'order': 0})
        r2 = self.client.post('/api/v1/menu-categories/', {'menu': menu_id, 'name': 'Cat B', 'order': 1})
        cat_a = r1.data.get('category_id')
        cat_b = r2.data.get('category_id')

        # items
        i1 = self.client.post('/api/v1/menu-items/', {'menu': menu_id, 'category': cat_a, 'name': 'Item 1', 'price': '10.00', 'currency': 'ZAR', 'available': True}).data.get('item_id')
        i2 = self.client.post('/api/v1/menu-items/', {'menu': menu_id, 'category': cat_a, 'name': 'Item 2', 'price': '5.00', 'currency': 'ZAR', 'available': True}).data.get('item_id')

        return menu_id, cat_a, cat_b, i1, i2

    def test_reorder_happy_path(self):
        menu_id, cat_a, cat_b, i1, i2 = self._create_menu_with_categories_items()

        payload = {
            'categories': [
                {'category_id': cat_b, 'order': 0},
                {'category_id': cat_a, 'order': 1},
            ],
            'items': [
                {'item_id': i1, 'category_id': cat_b, 'order': 0},
                {'item_id': i2, 'category_id': cat_a, 'order': 1},
            ]
        }

        resp = self.client.post(f'/api/v1/menus/{menu_id}/reorder/', payload, format='json')
        self.assertEqual(resp.status_code, 200)

        # Verify DB changes
        ca = MenuCategory.objects.get(category_id=cat_a)
        cb = MenuCategory.objects.get(category_id=cat_b)
        self.assertEqual(ca.order, 1)
        self.assertEqual(cb.order, 0)

        item1 = MenuItem.objects.get(item_id=i1)
        item2 = MenuItem.objects.get(item_id=i2)
        self.assertEqual(item1.category.category_id, cb.category_id)
        self.assertEqual(item1.order, 0)
        self.assertEqual(item2.category.category_id, ca.category_id)
        self.assertEqual(item2.order, 1)

    def test_reorder_fails_with_foreign_category(self):
        # create primary menu
        menu_id, cat_a, cat_b, i1, i2 = self._create_menu_with_categories_items()

        # create another business and menu+category not belonging to owner
        other_user = User.objects.create_user(email='other@example.com', password='x', account_type='business')
        other_biz = Business.objects.create(name='OtherBiz', owner=other_user)
        other_menu = Menu.objects.create(name='Other', business=other_biz)
        foreign_cat = MenuCategory.objects.create(menu=other_menu, name='Foreign', order=0)

        payload = {'categories': [{'category_id': foreign_cat.category_id, 'order': 0}], 'items': []}
        resp = self.client.post(f'/api/v1/menus/{menu_id}/reorder/', payload, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('errors', resp.data)

    def test_reorder_fails_with_foreign_item(self):
        menu_id, cat_a, cat_b, i1, i2 = self._create_menu_with_categories_items()

        other_user = User.objects.create_user(email='other2@example.com', password='x', account_type='business')
        other_biz = Business.objects.create(name='OtherBiz2', owner=other_user)
        other_menu = Menu.objects.create(name='Other2', business=other_biz)
        foreign_item = MenuItem.objects.create(menu=other_menu, name='Bad', price='1.00', currency='ZAR', available=True)

        payload = {'categories': [], 'items': [{'item_id': foreign_item.item_id, 'category_id': None, 'order': 0}]}
        resp = self.client.post(f'/api/v1/menus/{menu_id}/reorder/', payload, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('errors', resp.data)

    def test_reorder_malformed_payloads(self):
        menu_id, cat_a, cat_b, i1, i2 = self._create_menu_with_categories_items()

        # categories not a list
        resp = self.client.post(f'/api/v1/menus/{menu_id}/reorder/', {'categories': 'invalid', 'items': []}, format='json')
        # Implementation returns 400 with errors or a 400; accept 400
        self.assertEqual(resp.status_code, 400)

        # items not a list
        resp2 = self.client.post(f'/api/v1/menus/{menu_id}/reorder/', {'categories': [], 'items': {'x': 1}}, format='json')
        self.assertEqual(resp2.status_code, 400)
from django.test import TestCase
from rest_framework.test import APIClient
from api.models import User, Business, Menu, MenuCategory, MenuItem


class ReorderMenuTests(TestCase):
    def setUp(self):
        # Setup a business owner and a menu with categories and items
        self.owner = User.objects.create_user(email='owner2@example.com', password='pass1234', account_type='business')
        self.business = Business.objects.create(name='BizTwo', owner=self.owner)

        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

        # Create a menu
        resp = self.client.post('/api/v1/menus/', {'name': 'Reorder Menu', 'business': self.business.business_id})
        self.menu_id = resp.data.get('menu_id')

        # Create two categories
        r1 = self.client.post('/api/v1/menu-categories/', {'menu': self.menu_id, 'name': 'Cat A', 'order': 0})
        r2 = self.client.post('/api/v1/menu-categories/', {'menu': self.menu_id, 'name': 'Cat B', 'order': 1})
        self.cat_a = r1.data.get('category_id')
        self.cat_b = r2.data.get('category_id')

        # Create items
        it1 = self.client.post('/api/v1/menu-items/', {'menu': self.menu_id, 'category': self.cat_a, 'name': 'Item 1', 'price': '10.00', 'currency': 'ZAR', 'available': True})
        it2 = self.client.post('/api/v1/menu-items/', {'menu': self.menu_id, 'category': self.cat_a, 'name': 'Item 2', 'price': '12.00', 'currency': 'ZAR', 'available': True})
        it3 = self.client.post('/api/v1/menu-items/', {'menu': self.menu_id, 'category': self.cat_b, 'name': 'Item 3', 'price': '8.00', 'currency': 'ZAR', 'available': True})
        self.item1 = it1.data.get('item_id')
        self.item2 = it2.data.get('item_id')
        self.item3 = it3.data.get('item_id')

    def test_reorder_success(self):
        # Swap category orders and reorder items
        payload = {
            'categories': [
                {'category_id': self.cat_b, 'order': 0},
                {'category_id': self.cat_a, 'order': 1},
            ],
            'items': [
                {'item_id': self.item3, 'category_id': self.cat_b, 'order': 0},
                {'item_id': self.item1, 'category_id': self.cat_a, 'order': 1},
                {'item_id': self.item2, 'category_id': self.cat_a, 'order': 0},
            ]
        }
        resp = self.client.post(f'/api/v1/menus/{self.menu_id}/reorder/', payload, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.get('status'), 'ok')

        # Fetch items and check orders
        i1 = MenuItem.objects.get(item_id=self.item1)
        i2 = MenuItem.objects.get(item_id=self.item2)
        i3 = MenuItem.objects.get(item_id=self.item3)
        self.assertEqual(i1.order, 1)
        self.assertEqual(i2.order, 0)
        self.assertEqual(i3.order, 0)

    def test_reorder_invalid_category(self):
        # Use an invalid category id that doesn't belong to menu
        payload = {'categories': [{'category_id': 999999, 'order': 0}], 'items': []}
        resp = self.client.post(f'/api/v1/menus/{self.menu_id}/reorder/', payload, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('errors', resp.data)

    def test_reorder_invalid_item(self):
        # Use an invalid item id
        payload = {'categories': [], 'items': [{'item_id': 999999, 'category_id': None, 'order': 0}]}
        resp = self.client.post(f'/api/v1/menus/{self.menu_id}/reorder/', payload, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('errors', resp.data)

    def test_reorder_malformed_payload(self):
        # categories should be list; send a wrong type
        payload = {'categories': 'not-a-list', 'items': 'also-not-list'}
        resp = self.client.post(f'/api/v1/menus/{self.menu_id}/reorder/', payload, format='json')
        # The endpoint should return 400 for malformed input
        self.assertEqual(resp.status_code, 400)
        self.assertIn('errors', resp.data)
