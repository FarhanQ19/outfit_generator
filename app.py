from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from models import db, Category, Item, SavedOutfit

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///outfits.db'
app.config['UPLOAD_FOLDER'] = 'static/images'
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generator')
def generator():
    return render_template('generator.html')

@app.route('/saved_outfits')
def saved_outfits():
    return render_template('saved_outfits.html')

@app.route('/outfits', methods=['GET'])
def get_outfits():
    items = Item.query.all()
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'category': item.category_id,
        'brand': item.brand,
        'color': item.color,
        'secondary_color': item.secondary_color,
        'tertiary_color': item.tertiary_color,
        'style': item.style,
        'season': item.season,
        'image_url': item.image_url
    } for item in items])

@app.route('/add_sample_data', methods=['GET'])
def add_sample_data():
    tops = Category(name="Tops")
    bottoms = Category(name="Bottoms")
    shoes = Category(name="Shoes")
    hats = Category(name="Hats")
    bags = Category(name="Bags")
    accessories = Category(name="Accessories")
    jackets = Category(name="Jackets")
    db.session.add(tops)
    db.session.add(bottoms)
    db.session.add(shoes)
    db.session.add(hats)
    db.session.add(bags)
    db.session.add(accessories)
    db.session.add(jackets)
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
    secondary_color = request.form.get('secondaryColor')
    if secondary_color == 'No Secondary Color':
        secondary_color = None
    tertiary_color = request.form.get('tertiaryColor')
    if tertiary_color == 'No Tertiary Color':
        tertiary_color = None
    style = request.form.get('style')
    season = request.form.get('season')
    category_id = request.form.get('category')

    if file and name and brand and color and style and season and category_id:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        image_url = f"/static/images/{filename}"

        new_item = Item(name=name, brand=brand, color=color, secondary_color=secondary_color, tertiary_color=tertiary_color, style=style, season=season, category_id=category_id, image_url=image_url)
        db.session.add(new_item)
        db.session.commit()

        return jsonify({'image_url': image_url})
    return "Failed to upload", 400

@app.route('/delete_item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted successfully'})
    return jsonify({'message': 'Item not found'}), 404

@app.route('/edit_item/<int:item_id>', methods=['POST'])
def edit_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'message': 'Item not found'}), 404

    name = request.form.get('name')
    brand = request.form.get('brand')
    color = request.form.get('color')
    secondary_color = request.form.get('secondaryColor')
    if secondary_color == 'No Secondary Color':
        secondary_color = None
    tertiary_color = request.form.get('tertiaryColor')
    if tertiary_color == 'No Tertiary Color':
        tertiary_color = None
    style = request.form.get('style')
    season = request.form.get('season')
    category_id = request.form.get('category')

    if name and brand and color and style and season and category_id:
        item.name = name
        item.brand = brand
        item.color = color
        item.secondary_color = secondary_color
        item.tertiary_color = tertiary_color
        item.style = style
        item.season = season
        item.category_id = category_id

        db.session.commit()
        return jsonify({'message': 'Item updated successfully'})
    return jsonify({'message': 'Failed to update item'}), 400

@app.route('/view_items', methods=['GET'])
def view_items():
    items = Item.query.all()
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'category': item.category_id,
        'brand': item.brand,
        'color': item.color,
        'secondary_color': item.secondary_color,
        'tertiary_color': item.tertiary_color,
        'style': item.style,
        'season': item.season,
        'image_url': item.image_url
    } for item in items])

@app.route('/save_outfit', methods=['POST'])
def save_outfit():
    data = request.json
    saved_outfit = SavedOutfit(
        hat_id=data.get('hat_id'),
        top_id=data.get('top_id'),
        jacket_id=data.get('jacket_id'),
        bottom_id=data.get('bottom_id'),
        shoes_id=data.get('shoes_id'),
        bag_id=data.get('bag_id'),
        accessory_id=data.get('accessory_id')
    )
    db.session.add(saved_outfit)
    db.session.commit()
    return jsonify({'message': 'Outfit saved successfully'})

@app.route('/get_saved_outfits', methods=['GET'])
def get_saved_outfits():
    saved_outfits = SavedOutfit.query.all()
    return jsonify([{
        'id': outfit.id,
        'hat': outfit.hat.image_url if outfit.hat else None,
        'top': outfit.top.image_url if outfit.top else None,
        'jacket': outfit.jacket.image_url if outfit.jacket else None,
        'bottom': outfit.bottom.image_url if outfit.bottom else None,
        'shoes': outfit.shoes.image_url if outfit.shoes else None,
        'bag': outfit.bag.image_url if outfit.bag else None,
        'accessory': outfit.accessory.image_url if outfit.accessory else None
    } for outfit in saved_outfits])

# Add this route to delete a saved outfit
@app.route('/delete_saved_outfit/<int:outfit_id>', methods=['DELETE'])
def delete_saved_outfit(outfit_id):
    saved_outfit = SavedOutfit.query.get(outfit_id)
    if saved_outfit:
        db.session.delete(saved_outfit)
        db.session.commit()
        return jsonify({'message': 'Saved outfit deleted successfully'})
    return jsonify({'message': 'Saved outfit not found'}), 404

# Ensure this route is added in your app.py
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


