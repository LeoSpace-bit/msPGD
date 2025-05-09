#models
from extensions import db

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'))

class Manufacturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(50))
    contact_info = db.Column(db.String(200))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    sku = db.Column(db.String(50))
    barcode = db.Column(db.String(50))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturer.id'))
    base_unit = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    photos = db.relationship('Photo', backref='product', lazy=True)
    characteristics = db.relationship('ProductCharacteristic', backref='product', lazy=True)

class CharacteristicType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20))
    data_type = db.Column(db.String(20), nullable=False)


class ProductCharacteristic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    characteristic_type_id = db.Column(db.Integer, db.ForeignKey('characteristic_type.id'), nullable=False)
    value = db.Column(db.String(200))

    characteristic_type = db.relationship('CharacteristicType', backref='product_characteristics')

# class ProductCharacteristic(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
#     characteristic_type_id = db.Column(db.Integer, db.ForeignKey('characteristic_type.id'), nullable=False)
#     value = db.Column(db.String(200))

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    storage_path = db.Column(db.String(200), nullable=False)
    is_main = db.Column(db.Boolean, default=False)