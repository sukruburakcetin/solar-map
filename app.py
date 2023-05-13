import PIL
from PIL import Image
from flask import Flask, render_template, request, jsonify
from shapely import Point
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
    polygon = point.buffer(0.0002)  # 0.0002 is roughly equivalent to 20 meters
    feature = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [list(polygon.exterior.coords)]
        },
    }

    return jsonify(feature)


if __name__ == "__main__":
    app.run(debug=True)

#
# polygon = point.buffer(0.0002)  # 0.0002 is roughly equivalent to 20 meters
#
#    with open('./static/IHE_UYGUNLUK_2.json', 'r',
#              encoding='utf-8') as f:
#        ihe_uygunluk_geojson = json.load(f)
#
#    # url = 'https://raw.githubusercontent.com/sukruburakcetin/interactive_map/main/static/IHE_UYGUNLUK_2.json'
#    # kres_uygunluk_geojson = requests.get(url).json()
#    # url_mah = 'https://raw.githubusercontent.com/sukruburakcetin/interactive_map/main/static/mahalle_ilce.json'
#    # mahalle_geojson = requests.get(url_mah).json()
#
#    with open('./static/mahalle_ilce.json', 'r', encoding='utf-8') as f:
#        mahalle_geojson = json.load(f)
#
#    mah_ad = ""
#    ilce_ad = ""
#
#    for k in range(0, len(mahalle_geojson['features'])):
#        current_mahalle_geojson = shape(mahalle_geojson['features'][k]['geometry'])
#        if point.intersects(current_mahalle_geojson):
#            mah_ad = mahalle_geojson['features'][k]['properties']['MAH_AD']
#            ilce_ad = mahalle_geojson['features'][k]['properties']['ILCE_AD']
#
#    # print("mah_ad: ", mah_ad)
#    # print("ilce_ad: ", ilce_ad)
#
#    # Find all the shapes that intersect with the polygon
#    intersecting_shapes = []
#    intersecting_shapes_indexes = []
#    # her iki alanı kontrol eder ve indislerini array'e assign eder
#    for i in range(0, len(ihe_uygunluk_geojson['features'])):
#        current_ihe_uygunluk_shape = shape(ihe_uygunluk_geojson['features'][i]['geometry'])
#        if point.intersects(current_ihe_uygunluk_shape) and \
#                ihe_uygunluk_geojson['features'][i]['properties']['gridcode'] == 0:
#            break
#        if polygon.intersects(current_ihe_uygunluk_shape):
#            intersecting_shapes.append(current_ihe_uygunluk_shape)
#            intersecting_shapes_indexes.append(i)
#
#    # eger birden fazla polygon varsa buraya girer
#    if len(intersecting_shapes) > 1:
#        suitability_values = []
#        for current_ihe_uygunluk_shape in intersecting_shapes:
#            intersection = polygon.intersection(current_ihe_uygunluk_shape)
#            # kesisim alanını, marker'ın kesisim alanına bölüyorum
#            # misal 0.80/1 gibi
#            proportion_within_shape = intersection.area / polygon.area
#            print("proportion within shape: ", proportion_within_shape)
#            print("proportion within shape: ", current_ihe_uygunluk_shape)
#            suitability_values.append({
#                'gridcode': ihe_uygunluk_geojson['features'][intersecting_shapes_indexes[index_no]]['properties'][
#                    'gridcode'],
#                'proportion_within_shape': proportion_within_shape  # burada proporsiyonu saklıyorum
#            })
#            index_no += 1
#
#        # Calculate the weighted average of the suitability values based on the proportion of the polygon within each shape
#        total_proportion = sum([value['proportion_within_shape'] for value in suitability_values])
#        weighted_suitability_values = []
#        for value in suitability_values:
#            weighted_suitability_values.append({
#                'weighted_suitability': value['gridcode'] * (value['proportion_within_shape'] / total_proportion)
#                # burada kesisen altlık polygonlarının gridcodelarını(yani uygunluk kodlarını), yukarda hesapladığım proporsiyonla isleme sokuyorum
#            })
#
#        # her bir polygondan 1.3 ve 1.6 gibi degerler geliyor, hangisinde daha çok kesişmisse o daha büyük oluyor( değerlerin 3'ün altında gelmesi yukardaki işlemde normalize edilmesinden yani oradaki 2 polygonla kesisiyor ya onların 2 ve 3 geliyor bunların agırlıkları diyelim)
#        # bunları topluyorum GRIDCODE: 2.5532738460809687 böyle geliyor bu da ne  2 ne 3 ama 2li olanından ne kadar 2liği o alanla kesisiyor ne kadar 3lüğü o alanla kesisiyor bu sayı artıyor ya da  azalıyor ama 2 ve 3 le kesistiği için 2 ile 3 arasında oluyor
#        # eger polygonun alanı 2 lik kısımda daha çok olsaydı 2 ye daha yakın olacaktı ama burda 3 lük kırmızı alanda o yuvarlak polygon daha cok oldugu için 2.5 gibi geldi
#        # Calculate the final suitability value as the sum of the weighted suitability values
#
#        # sonra burada toplatılmıs value'ye göre tekrardan uygunluk description ataması yapıyorum
#        final_suitability_value = sum([value['weighted_suitability'] for value in weighted_suitability_values])
#        if 3 < final_suitability_value < 4:  # misal bizim GRIDCODE: 2.5532738460809687 degeri bu aralıkta o yüzden uygun - az uygun
#            suitability = "Uygun"
#        elif 2 < final_suitability_value < 3:  # misal bizim GRIDCODE: 2.5532738460809687 degeri bu aralıkta o yüzden uygun - az uygun
#            suitability = "Uygun - Az Uygun"
#
#        elif 1 < final_suitability_value < 2:
#            suitability = "Az Uygun - Uygun Değil"
#
#        elif 0 < final_suitability_value < 1:
#            suitability = "Uygun Değil"
#
#        # sonra bu degeri marker'a bind edip html tarafında ajax koduyla bu veriyi consume edip ekrana yansıtıyorum
#        feature = {
#            'type': 'Feature',
#            'geometry': {
#                'type': 'Polygon',
#                'coordinates': [list(polygon.exterior.coords)]
#            },
#            'id': 0,
#            'gridcode': final_suitability_value,
#            'suitability': suitability
#        }
#        intersecting_shapes.clear()
#        intersecting_shapes_indexes.clear()
#        suitability_values.clear()
#        weighted_suitability_values.clear()
#
#    else:
#
#        thereIsAPolygon = 0
#        for i in range(0, len(ihe_uygunluk_geojson['features'])):
#            current_ihe_uygunluk_shape = shape(ihe_uygunluk_geojson['features'][i]['geometry'])
#            if polygon.within(current_ihe_uygunluk_shape):
#                thereIsAPolygon = 1
#                # print(kres_uygunluk_geojson['features'][i]['properties']['Id'])
#                # print(kres_uygunluk_geojson['features'][i]['properties']['gridcode'])
#                suitability_condition = ["Konum atilamaz" if gridcode == "0" else "Uygun Degil" if gridcode == "1"
#                else "Az Uygun" if gridcode == "2" else "Uygun" if gridcode == "3" else "Çok Uygun" for gridcode
#                                         in str(ihe_uygunluk_geojson['features'][i]['properties']['gridcode'])]
#
#                # Convert the Shapely Polygon object to a GeoJSON Feature object
#                feature = {
#                    'type': 'Feature',
#                    'geometry': {
#                        'type': 'Polygon',
#                        'coordinates': [list(polygon.exterior.coords)]
#                    },
#                    'id': ihe_uygunluk_geojson['features'][i]['properties']['Id'],
#                    'gridcode': ihe_uygunluk_geojson['features'][i]['properties']['gridcode'],
#                    'suitability': suitability_condition,
#                    'mahalle_ad': mah_ad,
#                    'ilce_ad': ilce_ad
#                }
#        if thereIsAPolygon == 0:
#            feature = {
#                'type': 'Feature',
#                'geometry': {
#                    'type': 'Polygon',
#                    'coordinates': [list(polygon.exterior.coords)]
#                },
#                'id': "No Suitability Polygon",
#                'gridcode': " ",
#                'suitability': " ",
#                'mahalle_ad': " ",
#                'ilce_ad': " "
#            }
#        # Return the GeoJSON Feature object as a JSON response
