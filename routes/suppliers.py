from flask import Blueprint, request, jsonify
from controllers.suppliers import get_all_suppliers, get_supplier_by_id, create_supplier, update_supplier, delete_supplier

suppliers_bp = Blueprint('suppliers', __name__)

def validate_supplier(data):
    name = data.get('supplier_name')
    if not name:
        return {"status": 422, "error": "supplier_name is required", "field": "supplier_name"}
    if '<script>' in name.lower() or '</script>' in name.lower():
        return {"status": 422, "error": "invalid characters in supplier_name", "field": "supplier_name"}
    return None

@suppliers_bp.route('/', methods=['GET'])
def list_suppliers():
    return jsonify({"status": 200, "data": get_all_suppliers()}), 200

@suppliers_bp.route('/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    supplier = get_supplier_by_id(supplier_id)
    if not supplier:
        return jsonify({"status": 404, "error": "Supplier not found."}), 404
    return jsonify({"status": 200, "data": supplier}), 200

@suppliers_bp.route('/', methods=['POST'])
def add_supplier():
    data = request.json or {}
    validation_error = validate_supplier(data)
    if validation_error:
        return jsonify(validation_error), 422
    new_supplier = create_supplier(data)
    return jsonify({"status": 201, "data": new_supplier}), 201

@suppliers_bp.route('/<int:supplier_id>', methods=['PUT'])
def edit_supplier(supplier_id):
    data = request.json or {}
    validation_error = validate_supplier(data)
    if validation_error:
        return jsonify(validation_error), 422
    if not get_supplier_by_id(supplier_id):
        return jsonify({"status": 404, "error": "Supplier not found."}), 404
    updated_supplier = update_supplier(supplier_id, data)
    return jsonify({"status": 200, "data": updated_supplier}), 200

@suppliers_bp.route('/<int:supplier_id>', methods=['DELETE'])
def remove_supplier(supplier_id):
    if not get_supplier_by_id(supplier_id):
        return jsonify({"status": 404, "error": "Supplier not found."}), 404
    delete_supplier(supplier_id)
    return jsonify({"status": 200, "message": "Supplier deleted successfully."}), 200
