from kafka.models_messages import OrderItemPublic
from core.enums import OrderItemStatus, OrderStatus

def get_order_status(order_items: list[OrderItemPublic]):
    received_order_items = [order_item for order_item in order_items if order_item.status == OrderItemStatus.received]
    canceled_order_items = [order_item for order_item in order_items if order_item.status == OrderItemStatus.canceled]

    if len(received_order_items) == len(order_items):
        return OrderStatus.finished
    
    if len(canceled_order_items) == len(order_items):
        return OrderStatus.canceled
    
    if len(received_order_items) + len(canceled_order_items) == len(order_items):
        return OrderStatus.partially_finished

    if [OrderItemStatus.receivable] * (len(order_items) - len(received_order_items) - len(canceled_order_items)) == [order_item.status for order_item in order_items]:
        return OrderStatus.receive_pending
    
    if OrderItemStatus.receivable in [order_item.status for order_item in order_items]:
        return OrderStatus.partially_delivered
    
    return OrderStatus.on_delivery