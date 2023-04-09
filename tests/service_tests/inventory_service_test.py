import unittest
import uuid
from unittest.mock import patch

from data_adapter.inventory import Item
from models.base import GenericResponseModel
from models.inventory import ItemModel, ItemInsertModel, ItemCategory
from service.inventory_service import InventoryService


class TestInventoryService(unittest.TestCase):

    def setUp(self):
        self.item_insert_model = ItemInsertModel(
            category=ItemCategory.ELECTRONICS,
            name="Laptop",
            price=1000.00,
            description="A high performance laptop",
            image="https://example.com/image.jpg",
            quantity=10
        )

    @patch.object(Item, 'get_all_items')
    def test_get_all_items_in_inventory_success(self, mock_get_all_items):
        mock_items = [
            ItemModel(
                id=1,
                uuid=uuid.uuid4(),
                created_at="2023-04-09T14:53:10.285Z",
                is_deleted=False,
                category=ItemCategory.ELECTRONICS,
                name="Laptop",
                price=1000.00,
                description="A high performance laptop",
                image="https://example.com/image.jpg",
                quantity=10
            ),
            ItemModel(
                id=2,
                uuid=uuid.uuid4(),
                created_at="2023-04-09T14:53:10.285Z",
                is_deleted=False,
                category=ItemCategory.ELECTRONICS,
                name="Television",
                price=500.00,
                description="A 32 inch smart television",
                image="https://example.com/image.jpg",
                quantity=5
            )
        ]
        mock_get_all_items.return_value = mock_items

        expected_response = GenericResponseModel(
            status_code=200,
            data=[
                mock_items[0].build_response_model(),
                mock_items[1].build_response_model()
            ]
        )

        response = InventoryService.get_all_items_in_inventory()
        self.assertEqual(response.status_code, expected_response.status_code)
        self.assertEqual(response.data, expected_response.data)

    @patch.object(Item, 'get_all_items')
    def test_get_all_items_in_inventory_not_found(self, mock_get_all_items):
        mock_get_all_items.return_value = []

        expected_response = GenericResponseModel(
            status_code=404,
            error="No items found in inventory",
            data=[]
        )

        response = InventoryService.get_all_items_in_inventory()
        self.assertEqual(response.status_code, expected_response.status_code)
        self.assertEqual(response.error, expected_response.error)
        self.assertEqual(response.data, expected_response.data)

    @patch.object(Item, 'get_by_name_and_category')
    @patch.object(Item, 'create_item')
    def test_add_item_to_inventory_success(self, mock_create_item, mock_get_by_name_and_category):
        mock_get_by_name_and_category.return_value = None
        mock_create_item.return_value = ItemModel(
            id=2,
            uuid=uuid.uuid4(),
            created_at="2023-04-09T14:53:10.285Z",
            is_deleted=False,
            category=ItemCategory.ELECTRONICS,
            name="Television",
            price=500.00,
            description="A 32 inch smart television",
            image="https://example.com/image.jpg",
            quantity=5
        )

        expected_response = GenericResponseModel(
            status_code=201,
            data=mock_create_item.return_value.build_response_model()
        )

        response = InventoryService.add_item_to_inventory(self.item_insert_model)
        self.assertEqual(response.status_code, expected_response.status_code)
        self.assertEqual(response.data, expected_response.data)

    @patch.object(Item, 'get_by_name_and_category')
    def test_add_item_to_inventory_conflict(self, mock_get_by_name_and_category):
        mock_item = ItemModel(
            id=2,
            uuid=uuid.uuid4(),
            created_at="2023-04-09T14:53:10.285Z",
            is_deleted=False,
            category=ItemCategory.ELECTRONICS,
            name="Television",
            price=500.00,
            description="A 32 inch smart television",
            image="https://example.com/image.jpg",
            quantity=5
        )
        mock_get_by_name_and_category.return_value = mock_item

        expected_response = GenericResponseModel(
            status_code=409,
            error=InventoryService.ERROR_ITEM_ALREADY_IN_INVENTORY
        )

        response = InventoryService.add_item_to_inventory(self.item_insert_model)
        self.assertEqual(response.status_code, expected_response.status_code)
        self.assertEqual(response.error, expected_response.error)
        self.assertEqual(response.data, expected_response.data)

    def test_inventory_item_add(self):
        with self.assertRaises(ValueError):
            ItemModel(
                id=2,
                uuid=uuid.uuid4(),
                created_at="2023-04-09T14:53:10.285Z",
                is_deleted=False,
                category=ItemCategory.ELECTRONICS,
                name="Television",
                price=500.00,
                description="A 32 inch smart television",
                image="https://example.com/image.jpg",
                quantity=-1
            )
