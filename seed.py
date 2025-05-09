from faker import Faker
import random
import tempfile
import os

from extensions import db
from models import *
from MyS3Local import upload_photo_to_minio
from app import create_app

fake = Faker('ru_RU')

# Функция для загрузки тестового изображения из локального каталога
def get_local_image_path(file_name):
    return os.path.join("imgs", file_name)

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

        # Пути к тестовым изображениям
        IMAGE_PATHS = [
            "brick.jpg",
            "iron_bucket.jpg",
            "parket.jpg"
        ]

        # Создаем 30 товаров
        for i in range(1, 31):  # Изменяем диапазон так, чтобы начиналось с 1
            if i == 1:  # Условие для создания "Пустого товара"
                product = Product(
                    name="Пустой товар",
                    description=None,
                    sku=None,
                    barcode=None,
                    category_id=None,
                    manufacturer_id=None,
                    base_unit="шт",  # Если это поле не может быть пустым, оставляем "шт"
                    price=0.0  # Устанавливаем цену в 0
                )
                db.session.add(product)
                db.session.commit()  # Сохраняем "Пустой товар"

                # Загрузка специального изображения для Пустого товара
                img_path = get_local_image_path("emp_goods.jpg")  # Убедитесь, что файл существует
                object_name = f"product_{product.id}.jpg"
                if upload_photo_to_minio(img_path, "photos", object_name):
                    photo = Photo(
                        product_id=product.id,
                        storage_path=object_name,
                        is_main=True
                    )
                    db.session.add(photo)

            else:  # Создаем остальные товары
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


                img_path = get_local_image_path(random.choice(IMAGE_PATHS))  # Выбираем случайное изображение из локального каталога
                object_name = f"product_{product.id}.jpg"
                if upload_photo_to_minio(img_path, "photos", object_name):
                    photo = Photo(
                        product_id=product.id,
                        storage_path=object_name,
                        is_main=True
                    )
                    db.session.add(photo)

        db.session.commit()
        print("Тестовые данные успешно созданы!")

if __name__ == "__main__":
    create_test_data()



# from faker import Faker
# import random
# import tempfile
# import requests
# import os
#
# from extensions import db
# from models import *
# from MyS3Local import upload_photo_to_minio
# from app import create_app
#
# fake = Faker('ru_RU')
#
#
# def download_test_image(url, product_id):
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             temp_dir = tempfile.gettempdir()
#             file_path = f"{temp_dir}/product_{product_id}.jpg"
#
#             with open(file_path, 'wb') as f:
#                 f.write(response.content)
#
#             return file_path
#     except Exception as e:
#         print(f"Ошибка загрузки тестового изображения: {e}")
#     return None
#
#
# def create_test_data():
#     app = create_app()
#     with app.app_context():
#         db.drop_all()
#         db.create_all()
#
#         # Создаем категории
#         categories = [
#             Category(name="forTest_Кирпичи"),
#             Category(name="forTest_Бетон"),
#             Category(name="forTest_Металл")
#         ]
#         db.session.add_all(categories)
#
#         # Производители
#         manufacturers = [
#             Manufacturer(
#                 name=f"forTest_Завод_{i}",
#                 country=fake.country(),
#                 contact_info=fake.address()
#             ) for i in range(5)
#         ]
#         db.session.add_all(manufacturers)
#
#         # Характеристики
#         chars = [
#             CharacteristicType(name="Вес", unit="кг", data_type="number"),
#             CharacteristicType(name="Цвет", data_type="string"),
#             CharacteristicType(name="Огнестойкость", data_type="boolean")
#         ]
#         db.session.add_all(chars)
#         db.session.commit()
#
#         # URL тестовых изображений
#         IMAGE_URLS = [
#             "https://reclaimedbrickcompany.co.uk/cdn/shop/files/reclaimed-baldwin-pressed-bricks-or-pack-of-250-bricks-or-free-delivery-reclaimed-brick-company-1.jpg?v=1713391189",  # Замените на реальные URL
#             "https://reclaimedbrickcompany.co.uk/cdn/shop/files/reclaimed-york-stone-roof-slate-tile-reclaimed-brick-company-1.jpg?v=1696265775",
#             "https://reclaimedbrickcompany.co.uk/cdn/shop/files/fornace-s-anselmo-corso-aqua-white-linear-brick-or-free-delivery-reclaimed-brick-company-1.jpg?v=1696266835&width=1125"
#         ]
#
#         # Создаем 30 товаров
#         for i in range(1, 31):  # Изменяем диапазон так, чтобы начиналось с 1
#             if i == 1:  # Условие для создания "Пустого товара"
#                 product = Product(
#                     name="Пустой товар",
#                     description=None,
#                     sku=None,
#                     barcode=None,
#                     category_id=None,
#                     manufacturer_id=None,
#                     base_unit="шт",  # Если это поле не может быть пустым, оставляем "шт"
#                     price=0.0  # Устанавливаем цену в 0
#                 )
#                 db.session.add(product)
#                 db.session.commit()  # Сохраняем "Пустой товар"
#
#             else:  # Создаем остальные товары
#                 product = Product(
#                     name=f"forTest_Товар_{i}",
#                     description=fake.text(max_nb_chars=200),
#                     sku=f"SKU-{i:04d}",
#                     barcode=fake.isbn13(),
#                     category_id=random.choice(categories).id,
#                     manufacturer_id=random.choice(manufacturers).id,
#                     base_unit="шт",
#                     price=round(random.uniform(100, 5000), 2)
#                 )
#                 db.session.add(product)
#                 db.session.commit()
#
#                 # Добавляем характеристики
#                 char_weight = ProductCharacteristic(
#                     product_id=product.id,
#                     characteristic_type_id=1,
#                     value=str(random.randint(10, 100))
#                 )
#                 db.session.add(char_weight)
#
#                 char_color = ProductCharacteristic(
#                     product_id=product.id,
#                     characteristic_type_id=2,
#                     value=random.choice(["красный", "серый", "белый"])
#                 )
#                 db.session.add(char_color)
#
#                 char_fire = ProductCharacteristic(
#                     product_id=product.id,
#                     characteristic_type_id=3,
#                     value=str(random.choice([True, False]))
#                 )
#                 db.session.add(char_fire)
#
#                 # Загрузка фото
#                 if product.id == 1:  # Если id товара равен 1
#                     img_url = "https://img.freepik.com/premium-photo/white-square-podium-white-background-product-display_509562-30.jpg"  # Задаем специальный URL
#                 else:
#                     img_url = random.choice(IMAGE_URLS)  # Иначе выбираем случайный URL из списка
#
#                 temp_file = download_test_image(img_url, product.id)
#
#                 if temp_file:
#                     object_name = f"product_{product.id}.jpg"
#                     if upload_photo_to_minio(temp_file, "photos", object_name):
#                         photo = Photo(
#                             product_id=product.id,
#                             storage_path=object_name,
#                             is_main=True
#                         )
#                         db.session.add(photo)
#                         os.remove(temp_file)
#
#         db.session.commit()
#         print("Тестовые данные успешно созданы!")
#
#         # # Создаем 30 товаров
#         # for i in range(1, 31):
#         #     product = Product(
#         #         name=f"forTest_Товар_{i}",
#         #         description=fake.text(max_nb_chars=200),
#         #         sku=f"SKU-{i:04d}",
#         #         barcode=fake.isbn13(),
#         #         category_id=random.choice(categories).id,
#         #         manufacturer_id=random.choice(manufacturers).id,
#         #         base_unit="шт",
#         #         price=round(random.uniform(100, 5000), 2)
#         #     )
#         #     db.session.add(product)
#         #     db.session.commit()
#         #
#         #     # Добавляем характеристики
#         #     char_weight = ProductCharacteristic(
#         #         product_id=product.id,
#         #         characteristic_type_id=1,
#         #         value=str(random.randint(10, 100))
#         #     )
#         #     db.session.add(char_weight)
#         #
#         #     char_color = ProductCharacteristic(
#         #         product_id=product.id,
#         #         characteristic_type_id=2,
#         #         value=random.choice(["красный", "серый", "белый"])
#         #     )
#         #     db.session.add(char_color)
#         #
#         #     char_fire = ProductCharacteristic(
#         #         product_id=product.id,
#         #         characteristic_type_id=3,
#         #         value=str(random.choice([True, False]))
#         #     )
#         #     db.session.add(char_fire)
#         #
#         #     # Загрузка фото
#         #     img_url = random.choice(IMAGE_URLS)
#         #     temp_file = download_test_image(img_url, product.id)
#         #
#         #     if temp_file:
#         #         object_name = f"product_{product.id}.jpg"
#         #         if upload_photo_to_minio(temp_file, "photos", object_name):
#         #             photo = Photo(
#         #                 product_id=product.id,
#         #                 storage_path=object_name,
#         #                 is_main=True
#         #             )
#         #             db.session.add(photo)
#         #             os.remove(temp_file)
#         #
#         # db.session.commit()
#         # print("Тестовые данные успешно созданы!")
#
#
# if __name__ == "__main__":
#     create_test_data()