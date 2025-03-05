from flask import Flask, render_template
from extensions import db, migrate
from MyS3Local import get_photo_url


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    db.init_app(app)
    migrate.init_app(app, db)

    from models import Product, CharacteristicType  # Убираем неиспользуемый импорт

    @app.route('/product/<int:product_id>')
    def view_product(product_id):
        product = Product.query.get_or_404(product_id)

        # Получаем фотографии через связь
        photos = [get_photo_url("photos", photo.storage_path) for photo in product.photos]

        characteristics = {}
        for char in product.characteristics:  # Если есть проблемы здесь, добавьте аналогичную связь
            char_type = CharacteristicType.query.get(char.characteristic_type_id)
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
    app.run(debug=True)