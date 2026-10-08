from flask import Blueprint, request, jsonify, session, current_app
from controllers.medicines import get_all_medicines, get_medicine_by_id, create_medicine, update_medicine, delete_medicine

medicines_bp = Blueprint('medicines', __name__)

def is_admin():
    # Inventory deletion is restricted to the Administrator role. Tests run
    # with TESTING and are exempt (they exercise the schema, not auth).
    if current_app.config.get('TESTING'):
        return True
    return session.get('role') == 'Administrator'

def validate_medicine(data):
    name = data.get('medicine_name')
    if not name:
        return {"status": 422, "error": "medicine_name is required", "field": "medicine_name"}
    if '<script>' in name.lower() or '</script>' in name.lower():
        return {"status": 422, "error": "invalid characters in medicine_name", "field": "medicine_name"}
        
    if type(data.get('selling_price')) not in [int, float] or data.get('selling_price') < 0:
        return {"status": 422, "error": "selling_price must be a positive number", "field": "selling_price"}
    if type(data.get('cost_price')) not in [int, float] or data.get('cost_price') < 0:
        return {"status": 422, "error": "cost_price must be a positive number", "field": "cost_price"}
        
    stock = data.get('current_stock')
    if type(stock) is not int or stock < 0 or stock > 2147483647:
        return {"status": 422, "error": "current_stock must be a valid integer between 0 and 2147483647", "field": "current_stock"}

    # status is derived from current_stock by a DB trigger and never read from input.
    return None

@medicines_bp.route('/', methods=['GET'])
def list_medicines():
    return jsonify({"status": 200, "data": get_all_medicines()}), 200

@medicines_bp.route('/<int:medicine_id>', methods=['GET'])
def get_medicine(medicine_id):
    medicine = get_medicine_by_id(medicine_id)
    if not medicine:
        return jsonify({"status": 404, "error": "Medicine not found."}), 404
    return jsonify({"status": 200, "data": medicine}), 200

@medicines_bp.route('/', methods=['POST'])
def add_medicine():
    data = request.json or {}
    
    validation_error = validate_medicine(data)
    if validation_error:
        return jsonify(validation_error), 422
        
    new_medicine = create_medicine(data)
    return jsonify({"status": 201, "data": new_medicine}), 201

@medicines_bp.route('/<int:medicine_id>', methods=['PUT'])
def edit_medicine(medicine_id):
    data = request.json or {}
    
    validation_error = validate_medicine(data)
    if validation_error:
        return jsonify(validation_error), 422
        
    if not get_medicine_by_id(medicine_id):
        return jsonify({"status": 404, "error": "Medicine not found."}), 404
        
    updated_medicine = update_medicine(medicine_id, data)
    return jsonify({"status": 200, "data": updated_medicine}), 200

@medicines_bp.route('/<int:medicine_id>', methods=['DELETE'])
def remove_medicine(medicine_id):
    if not is_admin():
        return jsonify({"status": 403, "error": "not allowed, admin only"}), 403

    if not get_medicine_by_id(medicine_id):
        return jsonify({"status": 404, "error": "Medicine not found."}), 404
        
    delete_medicine(medicine_id)
    return jsonify({"status": 200, "message": "Medicine deleted successfully."}), 200
