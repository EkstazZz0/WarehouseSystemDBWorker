from enum import Enum

class OrderStatus(Enum):
    pending = 'pending'
    on_delivery = 'on_delivery'
    partially_delivered = 'partially_delivered'
    receive_pending = 'receive_pending'
    partially_finished = 'partially_finished'
    finished = 'finished'
    canceled = 'canceled'


class OrderItemStatus(Enum):
    pending = 'pending'
    receivable = 'receivable'
    on_delivery = 'on_delivery'
    received = 'received'
    canceled = 'canceled'


class ReceiveOrderItemStatus(Enum):
    received = 'received'
    canceled = 'canceled'


class TaskTypes(Enum):
    items_delivered = "items_delivered"
    new_order = "new_order"