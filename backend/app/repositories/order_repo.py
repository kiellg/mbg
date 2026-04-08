"""Repository functions for order records."""

# pylint: disable=protected-access, too-many-branches, duplicate-code
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import shortuuid
from app.data import order_data


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
    customer_phone: str = "",
    scheduled_time: Optional[str] = None,
    coupon_code: Optional[str] = None,
    coupon_snapshot: Optional[Dict[str, Any]] = None,
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
                "menu_item_id": item.get("menu_item_id"),
                "item_name": item.get("item_name"),
            }
        )

    order_record: Dict[str, Any] = {
        "order_id": order_id,
        "created_at": datetime.now(timezone.utc),
        "status": status,
        "customer_id": customer_id,
        "restaurant_id": restaurant_id,
        "delivery_address": delivery_address,
        "customer_phone": customer_phone,
        "delivery_method": delivery_method,
        "coupon_code": coupon_code,
        "coupon_snapshot": coupon_snapshot,
        "subtotal": "0.00",
        "discount": "0.00",
        "discounted_subtotal": "0.00",
        "tax": "0.00",
        "delivery_fee": "0.00",
        "total": "0.00",
        "items": stored_items,
        "delivery_time": "",
        "delivery_time_actual": 0.0,
        "delivery_delay": 0.0,
        "delivery_distance": 0.0,
        "driver_id": "",
        "driver_name": "",
        "route_taken": "",
        "scheduled_time": scheduled_time,
        "is_scheduled": scheduled_time is not None,
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
    if "coupon_code" in patch:
        order["coupon_code"] = patch["coupon_code"]
    if "coupon_snapshot" in patch:
        order["coupon_snapshot"] = patch["coupon_snapshot"]
    if "subtotal" in patch:
        order["subtotal"] = f"{patch['subtotal']:.2f}"
    if "discount" in patch:
        order["discount"] = f"{patch['discount']:.2f}"
    if "discounted_subtotal" in patch:
        order["discounted_subtotal"] = f"{patch['discounted_subtotal']:.2f}"
    if "tax" in patch:
        order["tax"] = f"{patch['tax']:.2f}"
    if "delivery_fee" in patch:
        order["delivery_fee"] = f"{patch['delivery_fee']:.2f}"
    if "total" in patch:
        order["total"] = f"{patch['total']:.2f}"

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
                    "menu_item_id": item.get("menu_item_id"),
                    "item_name": item.get("item_name"),
                }
            )
        order["items"] = replaced_items

    if "is_scheduled" in patch:
        order["is_scheduled"] = patch["is_scheduled"]

    if "scheduled_time" in patch:
        order["scheduled_time"] = patch["scheduled_time"]

    return order


def set_order_status(order_id: str, new_status: str) -> Optional[Dict[str, Any]]:
    """Set the status of an order record."""
    return update_order_record(order_id, {"status": new_status})


def cancel_order_record(order_id: str) -> Optional[Dict[str, Any]]:
    """Set an order status to Cancelled."""
    return set_order_status(order_id, "Cancelled")


def assign_driver_to_order(
    order_id: str,
    driver_id: str,
    driver_name: str,
) -> Optional[Dict[str, Any]]:
    """Assign a driver to an order record."""
    order = order_data._ORDERDB.get(order_id)
    if order is None:
        return None

    order["driver_id"] = driver_id
    order["driver_name"] = driver_name
    return order


def get_orders_assigned_to_driver(driver_id: str) -> List[Dict[str, Any]]:
    """Return all orders assigned to a specific driver."""
    return [
        order for order in order_data._ORDERDB.values()
        if order.get("driver_id") == driver_id
        and order.get("status") in  ("Cooking","Out for Delivery")
    ]

def clear_driver_reference(user_id: str) -> None:
    """Clear driver_id from any order assigned to this user."""
    for order in order_data._ORDERDB.values():
        if order.get("driver_id") == user_id:
            order["driver_id"] = ""
