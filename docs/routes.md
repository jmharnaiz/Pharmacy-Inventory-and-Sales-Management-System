# Pharmacy Inventory and Sales Management System

# Week 3 Routing Table

## Medicine Management

| Method | Path             | Handler        | User Story                   |
| ------ | ---------------- | -------------- | ---------------------------- |
| POST   | `/medicines`     | createMedicine | US-001 Add Medicine          |
| GET    | `/medicines`     | listMedicines  | US-002 View Medicine List    |
| GET    | `/medicines/:id` | showMedicine   | US-003 View Medicine Details |
| PUT    | `/medicines/:id` | updateMedicine | US-004 Edit Medicine         |
| DELETE | `/medicines/:id` | deleteMedicine | US-005 Delete Medicine       |

## Supplier Management

| Method | Path             | Handler        | User Story                   |
| ------ | ---------------- | -------------- | ---------------------------- |
| POST   | `/suppliers`     | createSupplier | US-006 Add Supplier          |
| GET    | `/suppliers`     | listSuppliers  | US-007 View Supplier List    |
| GET    | `/suppliers/:id` | showSupplier   | US-008 View Supplier Details |
| PUT    | `/suppliers/:id` | updateSupplier | US-009 Edit Supplier         |
| DELETE | `/suppliers/:id` | deleteSupplier | US-010 Delete Supplier       |

## Customer Management

| Method | Path             | Handler        | User Story                   |
| ------ | ---------------- | -------------- | ---------------------------- |
| POST   | `/customers`     | createCustomer | US-011 Add Customer          |
| GET    | `/customers`     | listCustomers  | US-012 View Customer List    |
| GET    | `/customers/:id` | showCustomer   | US-013 View Customer Details |
| PUT    | `/customers/:id` | updateCustomer | US-014 Edit Customer         |
| DELETE | `/customers/:id` | deleteCustomer | US-015 Delete Customer       |

## Sales Management

| Method | Path         | Handler    | User Story               |
| ------ | ------------ | ---------- | ------------------------ |
| POST   | `/sales`     | createSale | US-016 Record Sale       |
| GET    | `/sales`     | listSales  | US-017 View Sales List   |
| GET    | `/sales/:id` | showSale   | US-018 View Sale Details |
| PUT    | `/sales/:id` | updateSale | US-019 Edit Sale         |
| DELETE | `/sales/:id` | deleteSale | US-020 Delete Sale       |

## Reports

| Method | Path                 | Handler                 | User Story                       |
| ------ | -------------------- | ----------------------- | -------------------------------- |
| GET    | `/reports/sales`     | generateSalesReport     | US-021 Generate Sales Report     |
| GET    | `/reports/inventory` | generateInventoryReport | US-022 Generate Inventory Report |

## Authentication

| Method | Path                    | Handler        | User Story             |
| ------ | ----------------------- | -------------- | ---------------------- |
| POST   | `/auth/login`           | login          | US-023 Login           |
| POST   | `/auth/logout`          | logout         | US-024 Logout          |
| PUT    | `/auth/change-password` | changePassword | US-025 Change Password |
