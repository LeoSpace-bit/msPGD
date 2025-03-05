from faker import Faker
import random
import tempfile
import requests
import os

from extensions import db
from models import *
from MyS3Local import upload_photo_to_minio
from app import create_app

fake = Faker('ru_RU')


def download_test_image(url, product_id):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            temp_dir = tempfile.gettempdir()
            file_path = f"{temp_dir}/product_{product_id}.jpg"

            with open(file_path, 'wb') as f:
                f.write(response.content)

            return file_path
    except Exception as e:
        print(f"Ошибка загрузки тестового изображения: {e}")
    return None


def create_test_data():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Создаем категории
        categories = [
            Category(name="forTest_Кирпичи"),
            Category(name="forTest_Бетон"),
            Category(name="forTest_Металл")
        ]
        db.session.add_all(categories)

        # Производители
        manufacturers = [
            Manufacturer(
                name=f"forTest_Завод_{i}",
                country=fake.country(),
                contact_info=fake.address()
            ) for i in range(5)
        ]
        db.session.add_all(manufacturers)

        # Характеристики
        chars = [
            CharacteristicType(name="Вес", unit="кг", data_type="number"),
            CharacteristicType(name="Цвет", data_type="string"),
            CharacteristicType(name="Огнестойкость", data_type="boolean")
        ]
        db.session.add_all(chars)
        db.session.commit()

        # URL тестовых изображений
        IMAGE_URLS = [
            "https://reclaimedbrickcompany.co.uk/cdn/shop/files/reclaimed-baldwin-pressed-bricks-or-pack-of-250-bricks-or-free-delivery-reclaimed-brick-company-1.jpg?v=1713391189",  # Замените на реальные URL
            "https://media.istockphoto.com/id/1321239966/vector/wall-grunge-texture-background.jpg?s=612x612&w=0&k=20&c=9hRlhrniqf8TH92eUA41tkRP-Jq25KqQZMhvqMJjZpg=",
            "https://www.admiralmetals.com/wp-content/uploads/2021/06/Metal-Products-bg.jpg"
        ]

        # Создаем 30 товаров
        for i in range(1, 31):
            product = Product(
                name=f"forTest_Товар_{i}",
                description=fake.text(max_nb_chars=200),
                sku=f"SKU-{i:04d}",
                barcode=fake.isbn13(),
                category_id=random.choice(categories).id,
                manufacturer_id=random.choice(manufacturers).id,
                base_unit="шт",
                price=round(random.uniform(100, 5000), 2)
            )
            db.session.add(product)
            db.session.commit()

            # Добавляем характеристики
            char_weight = ProductCharacteristic(
                product_id=product.id,
                characteristic_type_id=1,
                value=str(random.randint(10, 100))
            )
            db.session.add(char_weight)

            char_color = ProductCharacteristic(
                product_id=product.id,
                characteristic_type_id=2,
                value=random.choice(["красный", "серый", "белый"])
            )
            db.session.add(char_color)

            char_fire = ProductCharacteristic(
                product_id=product.id,
                characteristic_type_id=3,
                value=str(random.choice([True, False]))
            )
            db.session.add(char_fire)

            # Загрузка фото
            img_url = random.choice(IMAGE_URLS)
            temp_file = download_test_image(img_url, product.id)

            if temp_file:
                object_name = f"product_{product.id}.jpg"
                if upload_photo_to_minio(temp_file, "photos", object_name):
                    photo = Photo(
                        product_id=product.id,
                        storage_path=object_name,
                        is_main=True
                    )
                    db.session.add(photo)
                    os.remove(temp_file)

        db.session.commit()
        print("Тестовые данные успешно созданы!")


if __name__ == "__main__":
    create_test_data()