from flask import Blueprint, request, jsonify
from controllers.sales import (get_all_sales, get_sale_by_id, get_sale_items,
                               create_sale, update_sale, delete_sale, SaleError)
from controllers.settings import get_setting
import db
import uuid
import datetime

sales_bp = Blueprint('sales', __name__)


def validate_items(items):
    if not isinstance(items, list) or len(items) == 0:
        return {"status": 422, "error": "a sale requires at least one line item", "field": "items"}

    for index, item in enumerate(items):
        label = "item %s" % (index + 1)
        if not isinstance(item, dict):
            return {"status": 422, "error": "%s: each line item must be an object" % label, "field": "items"}

        medicine_id = item.get('medicine_id')
        if type(medicine_id) is not int or medicine_id <= 0:
            return {"status": 422, "error": "%s: medicine_id must be a positive integer" % label, "field": "items"}

        quantity = item.get('quantity')
        if type(quantity) is not int or quantity <= 0 or quantity > 2147483647:
            return {"status": 422, "error": "%s: quantity must be a positive integer" % label, "field": "items"}

        unit_price = item.get('unit_price')
        if unit_price is not None and (type(unit_price) not in [int, float] or unit_price < 0):
            return {"status": 422, "error": "%s: unit_price must be a non-negative number" % label, "field": "items"}

    return None


def validate_sale(data, require_items=False):
    items = data.get('items')

    if require_items or items is not None:
        validation_error = validate_items(items)
        if validation_error:
            return validation_error
    elif type(data.get('total_amount')) not in [int, float] or data.get('total_amount') < 0:
        return {"status": 422, "error": "total_amount must be a positive number", "field": "total_amount"}

    if not data.get('payment_method'):
        return {"status": 422, "error": "payment_method is required", "field": "payment_method"}
    return None


def sale_error_response(error):
    return jsonify({"status": error.status, "error": error.message, "field": error.field}), error.status


@sales_bp.route('/', methods=['GET'])
def list_sales():
    return jsonify({"status": 200, "data": get_all_sales()}), 200


@sales_bp.route('/<int:sale_id>', methods=['GET'])
def get_sale(sale_id):
    sale = get_sale_by_id(sale_id)
    if not sale:
        return jsonify({"status": 404, "error": "Sale not found."}), 404
    sale['items'] = get_sale_items(sale_id)
    return jsonify({"status": 200, "data": sale}), 200


@sales_bp.route('/', methods=['POST'])
def add_sale():
    data = request.json or {}

    validation_error = validate_sale(data, require_items=True)
    if validation_error:
        return jsonify(validation_error), 422

    if not data.get('invoice_no'):
        data['invoice_no'] = "%s%s" % (get_setting('invoice_prefix', 'INV-'), uuid.uuid4().hex[:8].upper())
    if not data.get('date_time'):
        data['date_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        new_sale = create_sale(data)
    except SaleError as error:
        return sale_error_response(error)
    except db.integrity_errors():
        return jsonify({"status": 422, "error": "invoice_no already exists",
                        "field": "invoice_no"}), 422

    return jsonify({"status": 201, "data": new_sale}), 201


@sales_bp.route('/<int:sale_id>', methods=['PUT'])
def edit_sale(sale_id):
    data = request.json or {}

    validation_error = validate_sale(data)
    if validation_error:
        return jsonify(validation_error), 422
    if not get_sale_by_id(sale_id):
        return jsonify({"status": 404, "error": "Sale not found."}), 404

    try:
        updated_sale = update_sale(sale_id, data)
    except SaleError as error:
        return sale_error_response(error)
    except db.integrity_errors():
        return jsonify({"status": 422, "error": "invoice_no already exists",
                        "field": "invoice_no"}), 422

    return jsonify({"status": 200, "data": updated_sale}), 200


@sales_bp.route('/<int:sale_id>', methods=['DELETE'])
def remove_sale(sale_id):
    if not get_sale_by_id(sale_id):
        return jsonify({"status": 404, "error": "Sale not found."}), 404

    delete_sale(sale_id)
    return jsonify({"status": 200, "message": "Sale deleted successfully."}), 200
