from confluent_kafka import Consumer

from core.config import kafka_consumer_config, kafka_consumer_topics
from kafka.models_messages import KafkaMessage, kafka_models
from db.repository import db_work


if __name__ == "__main__":
    consumer = Consumer(kafka_consumer_config)
    consumer.subscribe(kafka_consumer_topics)

    try:
        while True:
            msg = consumer.poll(0.5)

            if not msg:
                continue

            if msg.error():
                print("Consumer error:", msg.error())
                continue
            
            try:
                kafka_message = KafkaMessage.model_validate_json(msg.value().decode("utf-8"))
                model = kafka_models.get(kafka_message.task).model_validate(kafka_message.payload)
                db_work(model)
            except:
                import traceback
                print(traceback.format_exc())
            

    except KeyboardInterrupt:
        print("Consumer is terminating...")
        consumer.close()
            
            