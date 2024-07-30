from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///outfits.db'
db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    brand = db.Column(db.String(80))
    color = db.Column(db.String(80))
    secondary_color = db.Column(db.String(80))
    tertiary_color = db.Column(db.String(80))  # Add this line
    style = db.Column(db.String(80))
    season = db.Column(db.String(80))
    image_url = db.Column(db.String(200))

class SavedOutfit(db.Model):  # Add this class
    id = db.Column(db.Integer, primary_key=True)
    hat_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)
    top_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)
    jacket_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)
    bottom_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)
    shoes_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)
    bag_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)
    accessory_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)

    hat = db.relationship('Item', foreign_keys=[hat_id])
    top = db.relationship('Item', foreign_keys=[top_id])
    jacket = db.relationship('Item', foreign_keys=[jacket_id])
    bottom = db.relationship('Item', foreign_keys=[bottom_id])
    shoes = db.relationship('Item', foreign_keys=[shoes_id])
    bag = db.relationship('Item', foreign_keys=[bag_id])
    accessory = db.relationship('Item', foreign_keys=[accessory_id])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
