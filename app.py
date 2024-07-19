from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from models import db, Category, Item  # Import from models.py

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///outfits.db'
app.config['UPLOAD_FOLDER'] = 'static/images'
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/outfits', methods=['GET'])
def get_outfits():
    items = Item.query.all()
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'category': item.category_id,
        'brand': item.brand,
        'color': item.color,
        'style': item.style,
        'season': item.season,
        'image_url': item.image_url
    } for item in items])

@app.route('/add_sample_data', methods=['GET'])
def add_sample_data():
    tops = Category(name="Tops")
    bottoms = Category(name="Bottoms")
    shoes = Category(name="Shoes")
    db.session.add(tops)
    db.session.add(bottoms)
    db.session.add(shoes)
    db.session.commit()

    return "Sample data added!"

@app.route('/upload', methods=['POST'])
def upload():
    if 'photo' not in request.files:
        return "No file part", 400
    file = request.files['photo']
    if file.filename == '':
        return "No selected file", 400

    name = request.form.get('name')
    brand = request.form.get('brand')
    color = request.form.get('color')
    style = request.form.get('style')
    season = request.form.get('season')
    category_id = request.form.get('category')

    if file and name and brand and color and style and season and category_id:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        image_url = f"/static/images/{filename}"

        new_item = Item(name=name, brand=brand, color=color, style=style, season=season, category_id=category_id, image_url=image_url)
        db.session.add(new_item)
        db.session.commit()

        return jsonify({'image_url': image_url})
    return "Failed to upload", 400

@app.route('/view_items', methods=['GET'])
def view_items():
    items = Item.query.all()
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'category': item.category_id,
        'brand': item.brand,
        'color': item.color,
        'style': item.style,
        'season': item.season,
        'image_url': item.image_url
    } for item in items])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
