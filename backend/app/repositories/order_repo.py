"""Repository functions for order records."""

# pylint: disable=protected-access
from typing import Any, Dict, List, Optional
import shortuuid

from backend.app.data import order_data


def get_order_record(order_id: str) -> Optional[Dict[str, Any]]:
    """Fetch an order record from the database."""
    return order_data._ORDERDB.get(order_id)


def list_order_records() -> List[Dict[str, Any]]:
    """Return all order records sorted by order_id."""
    return [order_data._ORDERDB[oid] for oid in sorted(order_data._ORDERDB.keys())]


def _alloc_order_id() -> str:
    """Allocate and return the next order_id."""
    return shortuuid.ShortUUID().random(length=7)


def _alloc_order_item_id() -> int:
    """Allocate and return the next order_item_id."""
    item_id = order_data.NEXT_ORDER_ITEM_ID
    order_data.NEXT_ORDER_ITEM_ID += 1
    return item_id


def create_order_record(# pylint: disable=too-many-arguments, too-many-positional-arguments
    customer_id: str,
    restaurant_id: int,
    delivery_address: str,
    items: List[Dict[str, Any]],
    delivery_method: str = "walk",
    status: str = "Pending",
) -> Dict[str, Any]:
    """Create and store a new order record.

    Delivery method must be one of: walk, bike, car.

    Items must include:
    - quantity
    - item_price
    """
    order_id = _alloc_order_id()

    stored_items: List[Dict[str, Any]] = []
    for item in items:
        if "quantity" not in item or "item_price" not in item:
            raise ValueError("Each item must include 'quantity' and 'item_price'.")

        stored_items.append(
            {
                "order_item_id": _alloc_order_item_id(),
                "order_id": order_id,
                "quantity": item["quantity"],
                "item_price": str(item["item_price"]),
            }
        )

    order_record: Dict[str, Any] = {
        "order_id": order_id,
        "status": status,
        "customer_id": customer_id,
        "restaurant_id": restaurant_id,
        "delivery_address": delivery_address,
        "delivery_method": delivery_method,
        "subtotal": "0.00",
        "tax": "0.00",
        "delivery_fee": "0.00",
        "total": "0.00",
        "items": stored_items,
        "delivery_time": "",
        "delivery_time_actual": 0.0,
        "delivery_delay": 0.0,
        "delivery_distance": 0.0,
        "driver_name": "",
        "route_taken": "",
        
    }

    order_data._ORDERDB[order_id] = order_record
    return order_record


def update_order_record(order_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update an existing order record with known fields only.

    If 'items' is provided, it replaces the entire items list.
    New items without order_item_id will be assigned one.
    """
    order = order_data._ORDERDB.get(order_id)
    if order is None:
        return None

    if "status" in patch:
        order["status"] = patch["status"]
    if "delivery_address" in patch:
        order["delivery_address"] = patch["delivery_address"]
    if "delivery_method" in patch:
        order["delivery_method"] = patch["delivery_method"]
    if "subtotal" in patch:
        order["subtotal"] = str(patch["subtotal"])
    if "tax" in patch:
        order["tax"] = str(patch["tax"])
    if "delivery_fee" in patch:
        order["delivery_fee"] = str(patch["delivery_fee"])
    if "total" in patch:
        order["total"] = str(patch["total"])

    if "items" in patch:
        replaced_items: List[Dict[str, Any]] = []
        for item in patch["items"]:
            if "quantity" not in item or "item_price" not in item:
                raise ValueError("Each item must include 'quantity' and 'item_price'.")

            order_item_id = item.get("order_item_id")
            if order_item_id is None:
                order_item_id = _alloc_order_item_id()

            replaced_items.append(
                {
                    "order_item_id": order_item_id,
                    "order_id": order_id,
                    "quantity": item["quantity"],
                    "item_price": str(item["item_price"]),
                }
            )
        order["items"] = replaced_items

    return order


def set_order_status(order_id: str, new_status: str) -> Optional[Dict[str, Any]]:
    """Set the status of an order record."""
    return update_order_record(order_id, {"status": new_status})


def cancel_order_record(order_id: str) -> Optional[Dict[str, Any]]:
    """Set an order status to Cancelled."""
    return set_order_status(order_id, "Cancelled")


def delete_order_record(order_id: str) -> bool:
    """Delete an order record by ID."""
    if order_id not in order_data._ORDERDB:
        return False
    del order_data._ORDERDB[order_id]
    return True
