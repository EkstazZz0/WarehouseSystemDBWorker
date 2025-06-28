from functools import singledispatch
from typing import Any
from sqlmodel import select
from sqlalchemy import func, or_

from kafka.models_messages import UpdateByNewOrder, UpdateBySupply, OrderItemPublic
from db.session import get_session
from db.models import Item, OrderItem, Order
from core.utils import get_order_status
from core.enums import OrderItemStatus


@singledispatch
def db_work(model: Any):
    raise NotImplementedError(f"Unavailable model {type(model)}")


@db_work.register
def _(order: UpdateByNewOrder):
    with get_session() as session:
        db_order_items = []
        for order_item in order.items:
            db_item = session.get(Item, order_item.item_id)
            db_item.reserved += order_item.quantity
            
            db_order_item = session.get(OrderItem, order_item.order_item_id)

            if db_item.quantity >= db_item.reserved:
                db_order_item.status = OrderItemStatus.receivable
            else:
                db_order_item.status = OrderItemStatus.on_delivery
            
            session.add(db_order_item)
            session.commit()
            session.refresh(db_order_item)
            db_order_items.append(db_order_item)
        
        db_order = session.get(Order, order.order_id)
        db_order.status = get_order_status(order_items=db_order_items)
        session.add(db_order)
        session.commit()
        

@db_work.register
def _(model: UpdateBySupply):
    print("NEW SUPPLY")
    with get_session() as session:
        for item in model.items:
            db_item = session.get(Item, item.item_id)
            order_ids = session.exec(select(OrderItem.order_id)
                                     .where((OrderItem.item_id == item.item_id) & (OrderItem.status == OrderItemStatus.on_delivery))).all()

            if not order_ids:
                continue

            orders = session.exec(select(Order).where(Order.order_id.in_(order_ids)).order_by(Order.created_at)).all()

            for order in orders:
                receivable_quantity = session.exec(select(func.sum(OrderItem.quantity))
                                                   .where((OrderItem.item_id == item.item_id) & (OrderItem.status == OrderItemStatus.receivable))
                                                   .group_by(OrderItem.item_id)).first()
                
                if not receivable_quantity:
                    receivable_quantity = 0
                
                db_order_item = session.exec(select(OrderItem)
                                                .where((OrderItem.order_id == order.order_id) & 
                                                       (OrderItem.item_id == item.item_id) & 
                                                       (OrderItem.status == OrderItemStatus.on_delivery))).first()
                
                if not db_order_item:
                    continue

                if db_order_item.quantity + receivable_quantity <= db_item.quantity:
                    db_order_item.status = OrderItemStatus.receivable
                    session.add(db_order_item)
            
            session.commit()

            order_ids = session.exec(select(OrderItem.order_id).where(OrderItem.item_id == item.item_id)).all()

            orders = session.exec(select(Order).where(Order.order_id.in_(order_ids))).all()

            for order in orders:
                order_items = session.exec(select(OrderItem)
                                              .where((OrderItem.order_id == order.order_id) & 
                                                     or_(OrderItem.status == OrderItemStatus.on_delivery, OrderItem.status == OrderItemStatus.receivable)))
                new_order_status = get_order_status(order_items=[OrderItemPublic.model_validate(order_item) for order_item in order_items])
                if new_order_status != order.status:
                    order.status = new_order_status
                    session.add(order)
            
        session.commit()
            


