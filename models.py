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
    style = db.Column(db.String(80))
    season = db.Column(db.String(80))
    image_url = db.Column(db.String(200))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
