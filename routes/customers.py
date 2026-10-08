from flask import Blueprint, request, jsonify
from controllers.customers import get_all_customers, get_customer_by_id, create_customer, update_customer, delete_customer

customers_bp = Blueprint('customers', __name__)

def validate_customer_data(data):
    errors = {}
    if not data.get('customer_name'):
        errors['customer_name'] = 'Customer name is required.'
    return errors

@customers_bp.route('/', methods=['GET'])
def list_customers():
    return jsonify({"status": 200, "data": get_all_customers()}), 200

@customers_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = get_customer_by_id(customer_id)
    if not customer:
        return jsonify({"status": 404, "error": "Customer not found."}), 404
    return jsonify({"status": 200, "data": customer}), 200

@customers_bp.route('/', methods=['POST'])
def add_customer():
    data = request.json or {}
    errors = validate_customer_data(data)
    if errors:
        return jsonify({"status": 422, "error": errors.get('customer_name'), "field": "customer_name"}), 422
        
    new_customer = create_customer(data)
    return jsonify({"status": 201, "data": new_customer}), 201

@customers_bp.route('/<int:customer_id>', methods=['PUT'])
def edit_customer(customer_id):
    if not get_customer_by_id(customer_id):
        return jsonify({"status": 404, "error": "Customer not found."}), 404
        
    data = request.json or {}
    errors = validate_customer_data(data)
    if errors:
        return jsonify({"status": 422, "error": errors.get('customer_name'), "field": "customer_name"}), 422
        
    updated_customer = update_customer(customer_id, data)
    return jsonify({"status": 200, "data": updated_customer}), 200

@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
def remove_customer(customer_id):
    if not get_customer_by_id(customer_id):
        return jsonify({"status": 404, "error": "Customer not found."}), 404
        
    delete_customer(customer_id)
    return jsonify({"status": 200, "message": "Customer deleted successfully."}), 200
