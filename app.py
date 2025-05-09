#app.py
from flask import Flask, render_template
from extensions import db, migrate
from MyS3Local import get_photo_url

from kafka import KafkaProducer
from kafka.errors import KafkaError, NoBrokersAvailable
import json
import threading
import logging


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    app.logger.setLevel(logging.INFO)

    db.init_app(app)
    migrate.init_app(app, db)

    from models import Product, CharacteristicType

    # Инициализация Kafka Producer
    app.producer = None

    def init_kafka_producer():
        try:
            app.producer = KafkaProducer(
                bootstrap_servers=app.config['KAFKA_BOOTSTRAP_SERVERS'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                retries=3,
                acks='all',
                request_timeout_ms=30000,
                reconnect_backoff_max_ms=10000
            )
            app.logger.info("Kafka producer initialized successfully")
        except NoBrokersAvailable as e:
            app.logger.error(f"Kafka brokers not available: {str(e)}")
        except Exception as e:
            app.logger.error(f"Failed to initialize Kafka producer: {str(e)}")

    init_kafka_producer()

    def send_products_update():
        while True:
            try:
                with app.app_context():
                    products = Product.query.filter(Product.id != 1).all()
                    app.logger.info(f"Preparing to send {len(products)} products")

                    products_data = []
                    for product in products:
                        try:
                            # Получаем главное фото
                            main_photo = next((p for p in product.photos if p.is_main), None)
                            photo_url = get_photo_url("photos", main_photo.storage_path) if main_photo else None

                            # Ищем характеристику веса
                            weight_char = next(
                                (c for c in product.characteristics
                                 if c.characteristic_type.name.lower() == 'weight'),
                                None
                            )
                            weight = None
                            if weight_char and weight_char.characteristic_type:
                                weight = f"{weight_char.value} {weight_char.characteristic_type.unit}"

                            products_data.append({
                                'id': product.id,
                                'name': product.name,
                                'price': float(product.price) if product.price else 0.0,
                                'photo_url': photo_url,
                                'weight': weight
                            })
                        except Exception as e:
                            app.logger.error(f"Error processing product {product.id}: {str(e)}")
                            continue

                    if products_data and app.producer:
                        future = app.producer.send(
                            app.config['KAFKA_PRODUCT_TOPIC'],
                            value=products_data
                        )
                        # Блокировка до подтверждения отправки
                        future.get(timeout=10)
                        app.logger.info(f"Sent {len(products_data)} products")

                threading.Event().wait(30)

            except NoBrokersAvailable as e:
                app.logger.error(f"Kafka brokers unavailable: {str(e)}. Reconnecting...")
                init_kafka_producer()
                threading.Event().wait(10)
            except KafkaError as e:
                app.logger.error(f"Kafka error: {str(e)}. Reinitializing producer...")
                try:
                    if app.producer:
                        app.producer.close()
                except:
                    pass
                init_kafka_producer()
                threading.Event().wait(5)
            except Exception as e:
                app.logger.error(f"Unexpected error: {str(e)}")
                threading.Event().wait(5)

    threading.Thread(target=send_products_update, daemon=True).start()


    @app.route('/product/<int:product_id>')
    def view_product(product_id):
        product = Product.query.get_or_404(product_id)

        # Получаем фотографии через связь
        photos = [get_photo_url("photos", photo.storage_path) for photo in product.photos]

        characteristics = {}
        for char in product.characteristics:  # Если есть проблемы здесь, добавьте аналогичную связь
            char_type = db.session.get(CharacteristicType, char.characteristic_type_id)
            characteristics[char_type.name] = {
                'value': char.value,
                'unit': char_type.unit
            }

        return render_template(
            'product.html',
            product=product,
            photos=photos,
            characteristics=characteristics
        )

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)