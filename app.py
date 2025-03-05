from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from MyS3Local import minio_client, get_photo_url

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Импорт моделей после инициализации db
from models import *


@app.route('/product/<int:product_id>')
def view_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        abort(404, description="Товар не найден")

    photos = [get_photo_url("photos", photo.storage_path) for photo in product.photos]

    characteristics = {}
    for char in product.characteristics:
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


if __name__ == '__main__':
    app.run(debug=True)