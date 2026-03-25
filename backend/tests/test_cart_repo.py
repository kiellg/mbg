"""Unit tests for cart_repo.py"""

#pylint: disable=protected-access
from app.data import cart_data
from app.repositories import cart_repo

def setup_function():
    """Reset cart data before each test."""
    cart_data._CARTDB.clear()
    cart_data.NEXT_CART_ID = 1
    cart_data.NEXT_ITEM_ID = 1

# for create cart function
def test_create_cart():
    """Creating a cart should return a properly structured cart record."""
    cart = cart_repo.create_cart(customer_id=1, restaurant_id=2)

    assert cart["id"] == 1
    assert cart["customer_id"] == 1
    assert cart["restaurant_id"] == 2
    assert not cart["items"]
    assert 1 in cart_data._CARTDB

def test_create_cart_increments_counter():
    """Creating multiple carts should increment the cart ID counter."""
    cart_repo.create_cart(customer_id=1, restaurant_id=1)
    cart_repo.create_cart(customer_id=2, restaurant_id=1)

    assert cart_data.NEXT_CART_ID == 3
    assert len(cart_data._CARTDB) == 2

# for get cart by id function
def test_get_cart_by_id_returns_correct_cart():
    """Retrieving a cart by ID should return the correct cart record."""
    cart_repo.create_cart(customer_id=1, restaurant_id=2)
    cart = cart_repo.get_cart_by_id(1)

    assert cart is not None
    assert cart["id"] == 1

def test_get_cart_by_id_returns_none_when_not_found():
    """Retrieving a non-existent cart ID should return None."""
    result = cart_repo.get_cart_by_id(999)
    assert result is None

# for get cart by customer and restaurant function
def test_get_cart_by_customer_and_restaurant_returns_correct_cart():
    """Retrieving a cart by customer and restaurant should return the correct cart record."""
    cart_repo.create_cart(customer_id=5, restaurant_id=3)
    cart = cart_repo.get_cart_by_customer_and_restaurant(customer_id=5, restaurant_id=3)

    assert cart is not None
    assert cart["customer_id"] == 5
    assert cart["restaurant_id"] == 3


def test_get_cart_by_customer_and_restaurant_returns_none_when_not_found():
    """Retrieving a cart with non-existent customer and restaurant IDs should return None."""
    result = cart_repo.get_cart_by_customer_and_restaurant(customer_id=99, restaurant_id=99)
    assert result is None

# for add item to cart function
def test_add_item_to_cart_appends_item():
    """Adding an item to the cart should append it to the cart's items list."""
    cart_repo.create_cart(customer_id=1, restaurant_id=1)
    item = cart_repo.add_item_to_cart(cart_id=1, menu_item_id=7, quantity=2)

    assert item is not None
    assert item["menu_item_id"] == 7
    assert item["quantity"] == 2
    assert len(cart_data._CARTDB[1]["items"]) == 1


def test_add_item_to_cart_increments_item_counter():
    """Adding multiple items to the cart should increment the item ID counter."""
    cart_repo.create_cart(customer_id=1, restaurant_id=1)
    cart_repo.add_item_to_cart(cart_id=1, menu_item_id=7, quantity=1)
    cart_repo.add_item_to_cart(cart_id=1, menu_item_id=8, quantity=3)

    assert cart_data.NEXT_ITEM_ID == 3
    assert len(cart_data._CARTDB[1]["items"]) == 2


def test_add_item_to_cart_returns_none_for_missing_cart():
    """Adding an item to a non-existent cart should return None."""
    result = cart_repo.add_item_to_cart(cart_id=999, menu_item_id=7, quantity=1)
    assert result is None

# for update cart item function
def test_update_item_quantity_changes_quantity():
    """Updating the quantity of an existing cart item should change its quantity in the cart."""
    cart_repo.create_cart(customer_id=1, restaurant_id=1)
    cart_repo.add_item_to_cart(cart_id=1, menu_item_id=7, quantity=2)

    updated = cart_repo.update_item_quantity(cart_id=1, item_id=1, quantity=5)

    assert updated is not None
    assert updated["quantity"] == 5
    assert cart_data._CARTDB[1]["items"][0]["quantity"] == 5


def test_update_item_quantity_returns_none_for_missing_item():
    """Updating the quantity of a non-existent item should return None."""
    cart_repo.create_cart(customer_id=1, restaurant_id=1)
    result = cart_repo.update_item_quantity(cart_id=1, item_id=999, quantity=3)
    assert result is None


def test_update_item_quantity_returns_none_for_missing_cart():
    """Updating the quantity of an item in a non-existent cart should return None."""
    result = cart_repo.update_item_quantity(cart_id=999, item_id=1, quantity=3)
    assert result is None

# for remove cart item function
def test_remove_item_from_cart_removes_correct_item():
    """Removing an item from the cart should remove the correct item based on its ID."""
    cart_repo.create_cart(customer_id=1, restaurant_id=1)
    cart_repo.add_item_to_cart(cart_id=1, menu_item_id=7, quantity=2)
    cart_repo.add_item_to_cart(cart_id=1, menu_item_id=8, quantity=1)

    result = cart_repo.remove_item_from_cart(cart_id=1, item_id=1)

    assert result is True
    assert len(cart_data._CARTDB[1]["items"]) == 1
    assert cart_data._CARTDB[1]["items"][0]["menu_item_id"] == 8


def test_remove_item_from_cart_returns_false_for_missing_item():
    """Removing a non-existent item from the cart should return False."""
    cart_repo.create_cart(customer_id=1, restaurant_id=1)
    result = cart_repo.remove_item_from_cart(cart_id=1, item_id=999)
    assert result is False


def test_remove_item_from_cart_returns_false_for_missing_cart():
    """Removing an item from a non-existent cart should return False."""
    result = cart_repo.remove_item_from_cart(cart_id=999, item_id=1)
    assert result is False

# for get cart items function
def test_get_cart_items_returns_items():
    """Retrieving items from the cart should return a list of items in the cart."""
    cart_repo.create_cart(customer_id=1, restaurant_id=1)
    cart_repo.add_item_to_cart(cart_id=1, menu_item_id=7, quantity=2)

    items = cart_repo.get_cart_items(cart_id=1)

    assert items is not None
    assert len(items) == 1
    assert items[0]["menu_item_id"] == 7


def test_get_cart_items_returns_none_for_missing_cart():
    """Retrieving items from a non-existent cart should return None."""
    result = cart_repo.get_cart_items(cart_id=999)
    assert result is None
