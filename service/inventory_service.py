import http
from typing import List

from controller.context_manager import context_log_meta
from data_adapter.inventory import Item
from logger import logger
from models.base import GenericResponseModel
from models.inventory import ItemModel, ItemInsertModel


class InventoryService:
    ERROR_NO_ITEMS_IN_INVENTORY = "No items found in inventory"

    @staticmethod
    def get_all_items_in_inventory() -> GenericResponseModel:
        """
        Get all items from inventory
        :return: GenericResponseModel
        """
        items: List[ItemModel] = Item.get_all_items()
        if not items:
            logger.error(extra=context_log_meta.get(), msg=f"No items found in inventory")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND,
                                        error=InventoryService.ERROR_NO_ITEMS_IN_INVENTORY, data=[])
        return GenericResponseModel(status_code=http.HTTPStatus.OK,
                                    data=[item.build_response_model() for item in items])

    @staticmethod
    def add_item_to_inventory(item: ItemInsertModel) -> GenericResponseModel:
        """
        Add item to inventory
        :param item: ItemInsertModel
        :return: GenericResponseModel
        """
        item = Item.create_item(item.build_db_model())
        return GenericResponseModel(status_code=http.HTTPStatus.CREATED, data=item.build_response_model())
