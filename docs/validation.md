# Pharmacy Inventory and Sales Management System

## Week 4 Validation Matrix

This document contains the validation rules for all create and update routes in the Pharmacy Inventory and Sales Management System.

---

# Standard Error Response

All validation errors use the following format:

```json
{
  "status": 422,
  "error": "Medicine name is required",
  "field": "name"
}
```

Validation errors return:

```text
422 Unprocessable Entity
```

Authorization errors return:

```text
403 Forbidden
```

---

# Medicine Management

## POST /medicines

| Field           | Validation Rules                   |
| --------------- | ---------------------------------- |
| name            | Required, string, 1–100 characters |
| category        | Required, string, 1–50 characters  |
| brand           | Required, string, 1–50 characters  |
| supplier_id     | Required, valid supplier reference |
| unit_price      | Required, number, greater than 0   |
| stock_quantity  | Required, integer, 0–9999          |
| expiration_date | Required, valid date format        |

### Validation Rules

* Medicine name must not be empty.
* Medicine name must be between 1 and 100 characters.
* Category must be provided.
* Brand must be provided.
* Supplier ID must refer to an existing supplier.
* Unit price must be a number greater than 0.
* Stock quantity must be a whole number between 0 and 9999.
* Expiration date must use a valid date format.

---

## PUT /medicines/:id

| Field           | Validation Rules                   |
| --------------- | ---------------------------------- |
| name            | Required, string, 1–100 characters |
| category        | Required, string, 1–50 characters  |
| brand           | Required, string, 1–50 characters  |
| supplier_id     | Required, valid supplier reference |
| unit_price      | Required, number, greater than 0   |
| stock_quantity  | Required, integer, 0–9999          |
| expiration_date | Required, valid date format        |

---

# Supplier Management

## POST /suppliers

| Field          | Validation Rules                     |
| -------------- | ------------------------------------ |
| company_name   | Required, string, 1–100 characters   |
| contact_person | Required, string, 1–100 characters   |
| phone          | Required, string, valid phone format |
| email          | Required, string, valid email format |
| address        | Required, string, 1–200 characters   |

---

## PUT /suppliers/:id

| Field          | Validation Rules                     |
| -------------- | ------------------------------------ |
| company_name   | Required, string, 1–100 characters   |
| contact_person | Required, string, 1–100 characters   |
| phone          | Required, string, valid phone format |
| email          | Required, string, valid email format |
| address        | Required, string, 1–200 characters   |

---

# Customer Management

## POST /customers

| Field   | Validation Rules                     |
| ------- | ------------------------------------ |
| name    | Required, string, 1–100 characters   |
| phone   | Required, string, valid phone format |
| email   | Optional, valid email format         |
| address | Required, string, 1–200 characters   |

---

## PUT /customers/:id

| Field   | Validation Rules                     |
| ------- | ------------------------------------ |
| name    | Required, string, 1–100 characters   |
| phone   | Required, string, valid phone format |
| email   | Optional, valid email format         |
| address | Required, string, 1–200 characters   |

---

# Sales Management

## POST /sales

| Field          | Validation Rules                            |
| -------------- | ------------------------------------------- |
| customer_id    | Required, valid customer reference          |
| medicine_id    | Required, valid medicine reference          |
| quantity       | Required, integer, 1–999                    |
| payment_method | Required, allowed values: Cash, Card, GCash |
| sale_date      | Required, valid date format                 |

### Additional Rules

* Customer ID must refer to an existing customer.
* Medicine ID must refer to an existing medicine.
* Quantity must be a whole number.
* Quantity must be greater than 0.
* Quantity must not exceed available medicine stock.
* Payment method must be Cash, Card, or GCash.

---

## PUT /sales/:id

| Field          | Validation Rules                            |
| -------------- | ------------------------------------------- |
| customer_id    | Required, valid customer reference          |
| medicine_id    | Required, valid medicine reference          |
| quantity       | Required, integer, 1–999                    |
| payment_method | Required, allowed values: Cash, Card, GCash |
| sale_date      | Required, valid date format                 |

---

# Authorization Guard

The Delete Medicine route requires authorization.

## DELETE /medicines/:id

Before deleting a medicine record, the system checks whether the current user has permission.

```text
IF user is not authorized
    RETURN 403 Forbidden
```

Example response:

```json
{
  "status": 403,
  "error": "You are not allowed to delete this medicine"
}
```

---

# Break-It Test Log

| Route                 | Test                   | Invalid Input              | Expected Result | Actual Result |
| --------------------- | ---------------------- | -------------------------- | --------------- | ------------- |
| POST /medicines       | Missing medicine name  | name missing               | 422             | 422           |
| POST /medicines       | Invalid price          | unit_price = "abc"         | 422             | 422           |
| POST /medicines       | Invalid stock          | stock_quantity = -1        | 422             | 422           |
| PUT /medicines/:id    | Empty category         | category = ""              | 422             | 422           |
| POST /suppliers       | Invalid email          | email = "invalid"          | 422             | 422           |
| PUT /suppliers/:id    | Missing company name   | company_name missing       | 422             | 422           |
| POST /customers       | Invalid phone          | phone = "abc"              | 422             | 422           |
| PUT /customers/:id    | Empty address          | address = ""               | 422             | 422           |
| POST /sales           | Invalid quantity       | quantity = 0               | 422             | 422           |
| POST /sales           | Invalid payment method | payment_method = "Bitcoin" | 422             | 422           |
| POST /sales           | Invalid medicine ID    | medicine_id does not exist | 422             | 422           |
| DELETE /medicines/:id | Unauthorized user      | user has no permission     | 403             | 403           |

---

# Summary

All create and update routes validate incoming data before processing it.

* Invalid input returns `422`.
* Forbidden actions return `403`.
* All validation errors use a consistent error response format.
* Validation is performed before the main route logic.
* Invalid input should never cause a `500` server error.
