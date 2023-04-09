import unittest
import uuid
from http import HTTPStatus
from unittest.mock import patch

from controller.context_manager import context_actor_user_data
from data_adapter.cart import CartItem, CustomerCart
from data_adapter.inventory import Item
from models.base import GenericResponseModel
from models.cart import CartModel, CartItemQuantity, CartItemModel
from models.inventory import ItemModel, ItemCategory
from models.user import UserModel, UserTokenData
from service.cart_service import CartService
from utils.password_hasher import PasswordHasher


class TestCartService(unittest.TestCase):

    def setUp(self):
        self.customer_uuid = uuid.uuid4()
        self.item_uuid = uuid.uuid4()
        self.customer_email = "johndoe@example.com"
        self.customer = UserModel(
            id=1,
            uuid=self.customer_uuid,
            created_at="2023-04-09T14:53:10.285Z",
            is_deleted=False,
            first_name="John",
            last_name="Doe",
            email=self.customer_email,
            role="customer",
            status="active",
            password_hash=PasswordHasher.get_password_hash("Password123@12")
        )
        context_actor_user_data.set(
            UserTokenData(uuid=str(self.customer_uuid), role="customer", email=self.customer_email))

        self.add_item_request = CartItemQuantity(quantity=1)
        self.item = ItemModel(
            id=1,
            uuid=self.item_uuid,
            created_at="2023-04-09T14:53:10.285Z",
            is_deleted=False,
            category=ItemCategory.ELECTRONICS,
            name="Laptop",
            price=1000.00,
            description="A high performance laptop",
            image="https://example.com/image.jpg",
            quantity=10
        )
        self.customer_cart = CartModel(
            id=1,
            uuid=uuid.uuid4(),
            created_at="2023-04-09T14:53:10.285Z",
            is_deleted=False,
            cart_items=[],
            customer=self.customer,
            customer_id=1
        )
        self.cart_item_added = CartItemModel(
            id=1,
            uuid=uuid.uuid4(),
            created_at="2023-04-09T14:53:10.285Z",
            is_deleted=False,
            cart_id=self.customer_cart.id,
            item_id=self.item.id, quantity_in_cart=1,
            original_item=self.item
        )

    @patch('service.cart_service.CustomerCart.get_by_customer_uuid')
    def test_get_cart_for_customer_success(self, mock_customer_cart):
        mock_cart = self.customer_cart
        mock_customer_cart.return_value = mock_cart
        expected_response = GenericResponseModel(
            status_code=200,
            data=mock_cart.build_response_model()

        )
        response = CartService.get_cart_for_customer()
        self.assertEqual(response, expected_response)

    @patch('service.cart_service.CustomerCart.get_by_customer_uuid')
    def test_get_cart_for_customer_no_cart(self, mock_customer_cart):
        expected_response = GenericResponseModel(status_code=HTTPStatus.NOT_FOUND,
                                                 error=CartService.ERROR_NO_CART_FOR_CUSTOMER)
        mock_customer_cart.return_value = None

        response = CartService.get_cart_for_customer()

        self.assertEqual(response, expected_response)

    @patch.object(Item, 'get_by_uuid')
    def test_add_item_to_cart_item_not_found(self, mock_item):
        mock_item.return_value = None

        response = CartService.add_item_to_cart(uuid.uuid4(), CartItemQuantity(quantity=1))

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response.error, CartService.ERROR_ITEM_NOT_FOUND)

    @patch.object(Item, 'get_by_uuid')
    def test_add_item_to_cart_item_out_of_stock(self, mock_item):
        item = self.item.copy(deep=True)
        item.quantity = 0
        mock_item.return_value = item

        response = CartService.add_item_to_cart(self.item.uuid, CartItemQuantity(quantity=1))

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.error, CartService.ERROR_ITEM_OUT_OF_STOCK)

    @patch.object(Item, 'get_by_uuid')
    def test_add_item_to_cart_item_quantity_not_enough(self, mock_item):
        mock_item.return_value = self.item

        response = CartService.add_item_to_cart(self.item.uuid, CartItemQuantity(quantity=11))

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.error, CartService.ERROR_ITEM_QUANTITY_NOT_ENOUGH)

    @patch.object(Item, 'get_by_uuid')
    @patch.object(CartItem, 'add_item_to_cart')
    @patch.object(CustomerCart, 'get_by_customer_uuid')
    @patch.object(Item, 'decrease_item_quantity')
    def test_add_item_to_cart_success(self, mock_decrease_item_quantity, mock_get_cart_by_customer_uuid,
                                      mock_add_item_to_cart, mock_get_item_by_uuid):
        quantity_to_add = 2
        mock_get_item_by_uuid.return_value = self.item
        cart_item_added = self.cart_item_added.copy(deep=True)
        cart_item_added.quantity_in_cart = quantity_to_add
        mock_add_item_to_cart.return_value = cart_item_added
        mock_get_cart_by_customer_uuid.return_value = self.customer_cart
        mock_decrease_item_quantity.return_value = self.item

        response = CartService.add_item_to_cart(self.item.uuid, CartItemQuantity(quantity=quantity_to_add))

        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(len(response.data.cart_items), 1)
        #  Check for quantity balance
        response_item_expected = self.item.build_response_model().copy(deep=True)
        response_item_expected.quantity += quantity_to_add
        self.assertEqual(response.data.cart_items[0].original_item, response_item_expected)
        self.assertEqual(response.data.cart_items[0].quantity_in_cart, quantity_to_add)
        mock_add_item_to_cart.assert_called_once_with(cart_id=1, item_id=1, quantity=quantity_to_add)

    @patch.object(Item, 'get_by_uuid')
    @patch.object(CartItem, 'update_item_quantity_in_cart')
    @patch.object(CustomerCart, 'get_by_customer_uuid')
    @patch.object(Item, 'decrease_item_quantity')
    def test_add_item_to_cart_item_exists_in_cart(self, mock_decrease_item_quantity,
                                                  mock_get_cart_by_customer_uuid, mock_update_item_quantity,
                                                  mock_get_item_by_uuid):
        """if item already exists in the cart then update the quantity instead of adding it again"""
        quantity_to_add = 5
        add_item_request = CartItemQuantity(quantity=quantity_to_add)
        mock_get_item_by_uuid.return_value = self.item
        customer_cart = self.customer_cart.copy(deep=True)
        #  cart has already added data
        customer_cart.cart_items.append(self.cart_item_added)
        mock_get_cart_by_customer_uuid.return_value = customer_cart
        mock_decrease_item_quantity.return_value = self.item

        response = CartService.add_item_to_cart(self.item_uuid, add_item_request)

        mock_get_item_by_uuid.assert_called_once_with(self.item_uuid)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.data.cart_items), 1)
        self.assertEqual(response.data.cart_items[0].quantity_in_cart, self.cart_item_added.quantity_in_cart)
        response_item_expected = self.item.build_response_model().copy(deep=True)
        self.assertEqual(response.data.cart_items[0].original_item, response_item_expected)

    @patch.object(CartItem, 'get_by_uuid')
    @patch.object(CustomerCart, 'get_by_customer_uuid')
    @patch.object(Item, 'increase_item_quantity')
    @patch.object(CartItem, 'delete_item_from_cart')
    def test_remove_item_from_cart_item_completely_removed(self, mock_delete_item_from_cart,
                                                           mock_increase_item_quantity,
                                                           mock_get_by_customer_uuid, mock_get_by_uuid):
        quantity_to_remove = 1
        cart_item = self.cart_item_added
        customer_cart = self.customer_cart.copy(deep=True)
        customer_cart.cart_items.append(cart_item)
        remove_item_request = CartItemQuantity(quantity=quantity_to_remove)
        mock_get_by_uuid.return_value = cart_item
        mock_get_by_customer_uuid.return_value = customer_cart

        response = CartService.remove_item_from_cart(cart_item_uuid=self.cart_item_added.uuid,
                                                     remove_item_request=remove_item_request)
        mock_increase_item_quantity.assert_called_once_with(str(cart_item.original_item.uuid),
                                                            remove_item_request.quantity)
        mock_delete_item_from_cart.assert_called_once_with(cart_item_id=self.cart_item_added.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.cart_items), 0)

    @patch.object(CartItem, 'get_by_uuid')
    @patch.object(CustomerCart, 'get_by_customer_uuid')
    def test_remove_item_from_cart_item_not_found(self, mock_get_by_customer_uuid, mock_get_by_uuid):
        # Arrange
        cart_item_uuid = uuid.uuid4()
        mock_get_by_uuid.return_value = None
        mock_get_by_customer_uuid.return_value = self.customer_cart

        response = CartService.remove_item_from_cart(cart_item_uuid=cart_item_uuid,
                                                     remove_item_request=CartItemQuantity(quantity=1))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.error, CartService.ERROR_CART_ITEM_NOT_FOUND)

    @patch.object(CartItem, 'get_by_uuid')
    @patch.object(CustomerCart, 'get_by_customer_uuid')
    def test_remove_item_from_cart_customer_cart_not_found(self, mock_get_by_customer_uuid, mock_get_by_uuid):
        cart_item_uuid = uuid.uuid4()
        mock_get_by_uuid.return_value = self.cart_item_added
        mock_get_by_customer_uuid.return_value = None

        response = CartService.remove_item_from_cart(cart_item_uuid=cart_item_uuid,
                                                     remove_item_request=CartItemQuantity(quantity=1))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.error, CartService.ERROR_CUSTOMER_CART_NOT_FOUND)

    @patch.object(CartItem, 'get_by_uuid')
    @patch.object(CustomerCart, 'get_by_customer_uuid')
    @patch.object(Item, 'increase_item_quantity')
    @patch.object(CartItem, 'update_item_quantity_in_cart')
    def test_remove_item_from_cart_item_quantity_reduced(self, mock_update_item_quantity_in_cart,
                                                         mock_increase_item_quantity,
                                                         mock_get_by_customer_uuid, mock_get_by_uuid):
        #  remove only one quantity from the cart item
        quantity_to_remove = 1
        existing_quantity_in_cart = 2
        cart_item = self.cart_item_added.copy(deep=True)
        cart_item.quantity_in_cart = existing_quantity_in_cart
        customer_cart = self.customer_cart.copy(deep=True)
        customer_cart.cart_items.append(cart_item)
        remove_item_request = CartItemQuantity(quantity=quantity_to_remove)
        mock_get_by_uuid.return_value = cart_item
        mock_get_by_customer_uuid.return_value = customer_cart

        response = CartService.remove_item_from_cart(cart_item_uuid=self.cart_item_added.uuid,
                                                     remove_item_request=remove_item_request)
        mock_increase_item_quantity.assert_called_once_with(str(cart_item.original_item.uuid),
                                                            remove_item_request.quantity)
        mock_update_item_quantity_in_cart.assert_called_once_with(
            cart_item_id=self.cart_item_added.id, quantity=existing_quantity_in_cart - quantity_to_remove)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.cart_items), 1)
        self.assertEqual(response.data.cart_items[0].quantity_in_cart, existing_quantity_in_cart - quantity_to_remove)
