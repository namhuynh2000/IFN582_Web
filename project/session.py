from project.db import get_tour
from project.models import Basket, BasketItem
from project.models import UserInfo, Order, OrderStatus

from flask import session

def get_user():
    user_dict = session.get('user')
    if user_dict:
        return UserInfo(
            id=str(user_dict['user_id']),
            firstname=user_dict['firstname'],
            surname=user_dict['surname'],
            email=user_dict['email'],
            phone=user_dict['phone']
        )
    return None

def get_basket():
    basket_data = session.get('basket')
    basket = Basket()
    if isinstance(basket_data, dict):
        for item in basket_data.get('items', []):
            tour = get_tour(item['tour']['id'])
            if tour:
                basket.add_item(BasketItem(
                    id=str(item['id']),
                    tour=tour,
                    quantity=item['quantity']
                ))
    return basket

def _save_basket_to_session(basket):
    session['basket'] = {
        'items': [
            {
                'id': item.id,
                'quantity': item.quantity,
                'tour': {
                    'id': item.tour.id
                }
            } for item in basket.items
        ]
    }

def add_to_basket(tour_id, quantity=1):
    basket = get_basket()
    basket.add_item(BasketItem(tour=get_tour(tour_id), quantity=quantity))
    _save_basket_to_session(basket)

def remove_from_basket(basket_item_id):
    basket = get_basket()
    basket.remove_item(basket_item_id)
    _save_basket_to_session(basket)

def empty_basket():
    session['basket'] = {
        'items': []
    }

def convert_basket_to_order(basket):
    return Order(
        id=None,
        status=OrderStatus.PENDING,
        user=get_user(),
        total_cost=basket.total_cost(),
        items=basket.items
    )
