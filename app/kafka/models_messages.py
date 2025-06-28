from sqlmodel import SQLModel, Field
from enum import Enum
from uuid import UUID
from pydantic import conlist
from datetime import datetime

from core.enums import TaskTypes, OrderItemStatus, OrderStatus

class PayloadFromKafka(SQLModel):
    pass


kafka_models: dict[str, PayloadFromKafka] = {}


def register_kafka_model(model_type: TaskTypes):
    def decorator(cls):
        kafka_models[model_type] = cls
        return cls
    
    return decorator


class KafkaMessage(SQLModel):
    task: TaskTypes
    payload: dict


class Items(SQLModel):
    item_id: UUID
    quantity: int

class OrderItemPublic(SQLModel):
    order_item_id: UUID = Field()
    item_id: UUID = Field()
    quantity: int = Field(gt=0)
    status: OrderItemStatus = Field()


@register_kafka_model(TaskTypes.items_delivered)
class UpdateBySupply(PayloadFromKafka):
    items: list[Items]


@register_kafka_model(TaskTypes.new_order)
class UpdateByNewOrder(PayloadFromKafka):
    order_id: UUID = Field()
    queue_number: int | None = Field(default=None)
    status: OrderStatus = Field()
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemPublic] = Field()
