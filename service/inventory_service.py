from typing import List

from controller.context_manager import context_log_meta
from data_adapter.inventory import Item
from logger import logger
from models.base import GenericResponseModel
from models.inventory import ItemModel


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
            return GenericResponseModel(status_code=404, error=InventoryService.ERROR_NO_ITEMS_IN_INVENTORY,
                                        data=[])
        return GenericResponseModel(status_code=200, data=[item.build_response_model() for item in items])
