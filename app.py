from idlelib import window

import PIL
import cv2
import numpy as np
from PIL import Image, ImageOps, ImageDraw
from flask import Flask, render_template, request, jsonify
from rasterio import features

from shapely import Point, Polygon
from shapely.geometry import shape
from pprint import pprint
from pyproj import Proj, transform
import rasterio as rio

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/save-points", methods=["POST"])
def save_points():
    # Get the points data from the AJAX request
    points = request.json.get('points')
    PIL.Image.MAX_IMAGE_PIXELS = 610644368
    # print(points)  # do something with the points data here
    # center point provided by the user
    # Get the RGB pixel values at the given point
    x, y = points['geometry']['coordinates']
    point = Point(x, y)
    # Load the image using PIL
    image = Image.open(r"C:\Users\BURAK\Desktop\solar-map\static\kadikoy_jpeg.jpeg")
    # width, height = image.size
    # print("width: ", width)
    # print("height: ", height)
    print("x", x)
    print("y", y)

    # if x < 0 or x >= width or y < 0 or y >= height:
    #     raise ValueError('Pixel coordinates are outside image boundary')

    def image_latlon_pxpy(latitude, longitude):
        dataset = rio.open(r'C:\Users\BURAK\Desktop\solar-map\static\kadikoy_jpeg.jpeg', crs='epsg:4326')
        # coords = transform(Proj(init='epsg:4326'), Proj(init='epsg:3857'), longitude, latitude)
        px, py = latitude, longitude
        px_pc = (px - dataset.bounds.left) / (dataset.bounds.right - dataset.bounds.left)
        py_pc = (dataset.bounds.top - py) / (dataset.bounds.top - dataset.bounds.bottom)
        return (px_pc * dataset.width, py_pc * dataset.height)

    print(image_latlon_pxpy(x, y))
    pixel = image.getpixel((image_latlon_pxpy(x, y)[0], image_latlon_pxpy(x, y)[1]))
    red, green, blue = pixel
    print("red: ", red)
    print("green: ", green)
    print("blue: ", blue)
    # Create a buffer around the Point object with a radius of 20 meters
    print(point)
    feature = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': points['geometry']['coordinates'],
            'red': red,
            'green': green,
            'blue': blue,
        },
    }

    return jsonify(feature)


@app.route("/save-polygons", methods=["POST"])
def save_polygons():
    # Get the points data from the AJAX request
    polygons = request.json.get('polygons')
    polygon_coordinates = polygons['geometry']['coordinates'][0]
    dataset = rio.open(r'C:\Users\BURAK\Desktop\solar-map\static\kadikoy_jpeg.jpeg', crs='epsg:4326')

    # Convert the polygon coordinates to pixel coordinates and create a geometry object
    px_coords = []
    py_coords = []
    for px, py in polygon_coordinates:
        px_pc = (px - dataset.bounds.left) / (dataset.bounds.right - dataset.bounds.left)
        py_pc = (dataset.bounds.top - py) / (dataset.bounds.top - dataset.bounds.bottom)
        a, b = (px_pc * dataset.width, py_pc * dataset.height)
        px_coords.append(a)
        py_coords.append(b)
    polygon = {'type': 'Polygon', 'coordinates': [list(zip(px_coords, py_coords))]}

    # Convert the mask vertices to integers
    mask_vertices = [(int(x), int(y)) for x, y in polygon['coordinates'][0]][:4]

    # Crop the image based on the mask vertices
    PIL.Image.MAX_IMAGE_PIXELS = 610644368
    image = Image.open(r"C:\Users\BURAK\Desktop\solar-map\static\kadikoy_jpeg.jpeg")
    image2 = image.copy()
    draw = ImageDraw.Draw(image2)

    draw.polygon(mask_vertices, outline="red")
    # Create a mask for the polygon area
    mask = Image.new('L', image.size, 0)
    ImageDraw.Draw(mask).polygon(mask_vertices, outline=1, fill=1)
    mask = np.array(mask)

    # Invert the mask and fill the outside area with black color
    mask = 1 - mask

    image2.putalpha(Image.fromarray(np.uint8(mask * 255)))

    image2.paste((0, 0, 0), mask=image2.split()[3])

    # Crop the image based on the mask vertices
    left = min(mask_vertices, key=lambda x: x[0])[0]
    upper = min(mask_vertices, key=lambda x: x[1])[1]
    right = max(mask_vertices, key=lambda x: x[0])[0]
    lower = max(mask_vertices, key=lambda x: x[1])[1]

    # Crop the image based on the sorted mask vertices
    cropped_img = image2.crop((left, upper, right, lower))
    cropped_img_raw = image.crop((left, upper, right, lower))

    # Convert images to numpy arrays
    cropped_img_np = np.array(cropped_img)
    cropped_img_raw_np = np.array(cropped_img_raw)

    # Convert cropped_img to grayscale
    cropped_img_gray = cv2.cvtColor(cropped_img_np, cv2.COLOR_BGR2GRAY)

    # Threshold the grayscale image to create a binary mask
    _, mask = cv2.threshold(cropped_img_gray, 1, 255, cv2.THRESH_BINARY)

    # Apply the mask to cropped_img_raw
    result = cv2.bitwise_and(cropped_img_raw_np, cropped_img_raw_np, mask=mask)

    # Convert the result back to PIL image format
    result_image = Image.fromarray(result)

    # Save the result image
    result_image.save("result.jpg")

    def get_mean_rgb(image):
        width, height = image.size
        r_total, g_total, b_total, count = 0, 0, 0, 0
        for x in range(width):
            for y in range(height):
                r, g, b = image.getpixel((x, y))
                if r != 0 or g != 0 or b != 0:
                    r_total += r
                    g_total += g
                    b_total += b
                    count += 1
        return (r_total // count, g_total // count, b_total // count)

    print(get_mean_rgb(result_image))

    feature = {
        'type': 'Feature',
        'geometry': {
            'type': 'Polygon',
            'coordinates': [polygon_coordinates],
            'rgb_mean_value': get_mean_rgb(result_image)
        },
    }
    return jsonify(feature)


if __name__ == "__main__":
    app.run(debug=True)
