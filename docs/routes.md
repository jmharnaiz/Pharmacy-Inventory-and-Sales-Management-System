# Routing Structure

| Resource | HTTP Method | Path | Handler | Story it serves |
|---|---|---|---|---|
| **Medicines** | | | | |
| Medicines | GET | `/api/medicines/` | `listMedicines` | View all medicines |
| Medicines | GET | `/api/medicines/<id>` | `showMedicine` | View one medicine |
| Medicines | POST | `/api/medicines/` | `createMedicine` | Create a medicine |
| Medicines | PUT | `/api/medicines/<id>` | `updateMedicine` | Edit a medicine |
| Medicines | DELETE | `/api/medicines/<id>` | `deleteMedicine` | Delete a medicine |
| **Customers** | | | | |
| Customers | GET | `/api/customers/` | `listCustomers` | View all customers |
| Customers | GET | `/api/customers/<id>` | `showCustomer` | View one customer |
| Customers | POST | `/api/customers/` | `createCustomer` | Create a customer |
| Customers | PUT | `/api/customers/<id>` | `updateCustomer` | Edit a customer |
| Customers | DELETE | `/api/customers/<id>` | `deleteCustomer` | Delete a customer |
| **Suppliers** | | | | |
| Suppliers | GET | `/api/suppliers/` | `listSuppliers` | View all suppliers |
| Suppliers | GET | `/api/suppliers/<id>` | `showSupplier` | View one supplier |
| Suppliers | POST | `/api/suppliers/` | `createSupplier` | Create a supplier |
| Suppliers | PUT | `/api/suppliers/<id>` | `updateSupplier` | Edit a supplier |
| Suppliers | DELETE | `/api/suppliers/<id>` | `deleteSupplier` | Delete a supplier |
| **Sales** | | | | |
| Sales | GET | `/api/sales/` | `listSales` | View all sales |
| Sales | GET | `/api/sales/<id>` | `showSale` | View one sale |
| Sales | POST | `/api/sales/` | `createSale` | Create a sale |
| Sales | PUT | `/api/sales/<id>` | `updateSale` | Edit a sale |
| Sales | DELETE | `/api/sales/<id>` | `deleteSale` | Delete a sale |


## Example Requests & Responses

Consistent Response Shape across all routes:
`{ "success": boolean, "message": string (optional), "data": object/array (optional), "id": integer (optional), "errors": object (optional) }`

### GET /api/suppliers/ (List)
**Request**: `GET /api/suppliers/`
**Response (200 OK)**:
```json
{
  "success": true,
  "message": "listSuppliers stub",
  "data": []
}
```

### GET /api/suppliers/1 (Show)
**Request**: `GET /api/suppliers/1`
**Response (200 OK)**:
```json
{
  "success": true,
  "message": "showSupplier stub",
  "id": 1,
  "data": {}
}
```

### POST /api/suppliers/ (Create)
**Request**: `POST /api/suppliers/`
```json
{
  "supplier_name": "MedSupply Pharma"
}
```
**Response (201 Created)**:
```json
{
  "success": true,
  "message": "createSupplier stub",
  "data": {}
}
```

### PUT /api/suppliers/1 (Update)
**Request**: `PUT /api/suppliers/1`
```json
{
  "supplier_name": "MedSupply Pharma Updated"
}
```
**Response (200 OK)**:
```json
{
  "success": true,
  "message": "updateSupplier stub",
  "id": 1,
  "data": {}
}
```

### DELETE /api/suppliers/1 (Delete)
**Request**: `DELETE /api/suppliers/1`
**Response (200 OK)**:
```json
{
  "success": true,
  "message": "deleteSupplier stub",
  "id": 1
}
```
