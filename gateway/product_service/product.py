import requests, os
from flask import jsonify


def get_all_products(request):
    response = requests.get(f"http://{os.environ.get('PRODUCT_SVC_ADDRESS')}/products")
    if response.status_code == 200:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({"error": "Failed to get products"}), 500


def get_product(request, product_id):
    response = requests.get(
        f"http://{os.environ.get('PRODUCT_SVC_ADDRESS')}/products/{product_id}"
    )
    if response.status_code == 200:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({"error": "Failed to get products"}), 500


def create_product(request):
    data = request.get_json()
    name = data["name"]
    description = data["description"]
    price = data["price"]
    quantity = data["quantity"]
    category = data["category"]

    response = requests.post(
        f"http://{os.environ.get('PRODUCT_SVC_ADDRESS')}/products",
        json={
            "name": name,
            "description": description,
            "price": price,
            "quantity": quantity,
            "category": category,
        },
    )

    if response.status_code == 200:
        return jsonify(response.json()), response.status_code
    else:
        return jsonify({"error": "Failed to create a product"}), 500
