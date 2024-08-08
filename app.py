import cv2
import numpy as np
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from skimage import io
from skimage.color import rgb2lab, lab2rgb
from sklearn.cluster import KMeans
from models import db, Category, Item  # Import from models.py

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///outfits.db'
app.config['UPLOAD_FOLDER'] = 'static/images'
db.init_app(app)

# Define the color map
color_map = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'orange': (255, 165, 0),
    'pink': (255, 192, 203),
    'purple': (128, 0, 128),
    'brown': (165, 42, 42),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'gray': (128, 128, 128),
    'beige': (245, 245, 220),
    'navy': (0, 0, 128)
}

def closest_color(rgb):
    r, g, b = rgb
    color_diffs = []
    for color, color_rgb in color_map.items():
        cr, cg, cb = color_rgb
        color_diff = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2
        color_diffs.append((color_diff, color))
    return min(color_diffs)[1]

def detect_colors(image_path):
    image = io.imread(image_path)
    image = image[:, :, :3]  # Ignore alpha channel if it exists

    # Convert image to LAB color space
    image_lab = rgb2lab(image)

    # Reshape the image to a 2D array of LAB values
    pixels = image_lab.reshape((-1, 3))

    # Define number of clusters
    n_colors = 3

    # Use k-means to find clusters of colors
    kmeans = KMeans(n_clusters=n_colors, random_state=0).fit(pixels)
    cluster_centers = kmeans.cluster_centers_

    # Convert LAB clusters to RGB
    cluster_centers_rgb = lab2rgb(cluster_centers[np.newaxis, :, :])[0] * 255
    cluster_centers_rgb = cluster_centers_rgb.astype(int)

    # Get the closest named colors
    primary_color = closest_color(cluster_centers_rgb[0])
    secondary_color = closest_color(cluster_centers_rgb[1]) if n_colors > 1 else 'No Secondary Color'
    tertiary_color = closest_color(cluster_centers_rgb[2]) if n_colors > 2 else 'No Tertiary Color'

    return primary_color, secondary_color, tertiary_color

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generator')
def generator():
    return render_template('generator.html')


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
    style = request.form.get('style')
    season = request.form.get('season')
    category_id = request.form.get('category')

    manual_primary_color = request.form.get('primaryColor')
    manual_secondary_color = request.form.get('secondaryColor')
    manual_tertiary_color = request.form.get('tertiaryColor')

    if file and name and brand and style and season and category_id:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        image_url = f"/static/images/{filename}"

        primary_color, secondary_color, tertiary_color = detect_colors(filepath)

        # Use manual colors if provided
        primary_color = manual_primary_color or primary_color
        secondary_color = manual_secondary_color or secondary_color
        tertiary_color = manual_tertiary_color or tertiary_color

        new_item = Item(name=name, brand=brand, color=primary_color, secondary_color=secondary_color, tertiary_color=tertiary_color, style=style, season=season, category_id=category_id, image_url=image_url)
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
    tertiary_color = request.form.get('tertiaryColor')
    if secondary_color == 'No Secondary Color':
        secondary_color = None
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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
