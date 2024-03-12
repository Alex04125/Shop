import requests, os
import jsonify


def order_details(request, order_id):
    response = requests.get(
        f"http://{os.environ.get('ORDER_SVC_ADDRESS')}/order_details/{order_id}"
    )

    if response.status_code == 200:
        return response, response.status_code
    else:
        return jsonify({"error": "Failed to find order"}), 500
