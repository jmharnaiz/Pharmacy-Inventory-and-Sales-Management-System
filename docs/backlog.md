# Pharmacy Inventory and Sales Management System
## Backlog

### Project Description
A web-based Pharmacy Inventory and Sales Management System that allows pharmacy staff to manage medicines, suppliers, customers, and sales transactions. The system tracks medicine inventory, expiration dates, suppliers, customer information, and daily sales.

---

# Record Type: Medicines

## MED-001 - Create Medicine
**User Story**
As a pharmacist, I want to add a new medicine so that it becomes available for inventory and sales.

**Acceptance Criteria**
- Medicine name is required.
- Quantity must be greater than or equal to zero.
- Expiration date must be valid.
- Medicine appears in the inventory list after saving.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

## MED-002 - View Medicines List
**User Story**
As a pharmacist, I want to view all medicines so that I can monitor inventory.

**Acceptance Criteria**
- Displays all medicines.
- Shows stock quantity.
- Shows expiration date.
- Search function filters medicines.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

## MED-003 - View Medicine Details
**User Story**
As a pharmacist, I want to view medicine details so that I can check complete information.

**Acceptance Criteria**
- Displays medicine name.
- Displays supplier.
- Displays category.
- Displays quantity.
- Displays expiration date.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

## MED-004 - Update Medicine
**User Story**
As a pharmacist, I want to edit medicine information so that inventory stays accurate.

**Acceptance Criteria**
- Existing medicine can be edited.
- Invalid values are rejected.
- Updated information is displayed.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

## MED-005 - Delete Medicine
**User Story**
As a pharmacist, I want to remove obsolete medicines so that inventory stays organized.

**Acceptance Criteria**
- Confirmation dialog appears.
- Medicine is deleted after confirmation.
- Inventory list updates automatically.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

# Record Type: Suppliers

## SUP-001 - Create Supplier
**User Story**
As a pharmacist, I want to add a supplier so that medicines can be assigned to suppliers.

**Acceptance Criteria**
- Supplier name is required.
- Contact information is saved.
- Supplier appears in the supplier list.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

## SUP-002 - View Supplier List
**User Story**
As a pharmacist, I want to view all suppliers so that I can manage supplier information.

**Acceptance Criteria**
- Displays supplier names.
- Displays contact information.
- Search function works.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

## SUP-003 - View Supplier Details
**User Story**
As a pharmacist, I want to view supplier details so that I can check supplier information.

**Acceptance Criteria**
- Shows supplier name.
- Shows address.
- Shows phone number.
- Shows medicines supplied.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

## SUP-004 - Update Supplier
**User Story**
As a pharmacist, I want to edit supplier information so that records stay updated.

**Acceptance Criteria**
- Existing supplier can be edited.
- Updated information is displayed.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

## SUP-005 - Delete Supplier
**User Story**
As a pharmacist, I want to delete inactive suppliers so that supplier records stay organized.

**Acceptance Criteria**
- Confirmation dialog appears.
- Supplier is removed after confirmation.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

# Record Type: Customers

## CUS-001 - Create Customer
**User Story**
As a pharmacist, I want to register a customer so that sales can be recorded properly.

**Acceptance Criteria**
- Customer name is required.
- Customer is saved successfully.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

## CUS-002 - View Customer List
**User Story**
As a pharmacist, I want to view all customers so that I can manage customer records.

**Acceptance Criteria**
- Displays all customers.
- Search feature works.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

## CUS-003 - View Customer Details
**User Story**
As a pharmacist, I want to view customer information so that I can review purchase history.

**Acceptance Criteria**
- Shows customer details.
- Shows previous purchases.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

## CUS-004 - Update Customer
**User Story**
As a pharmacist, I want to edit customer information so that records remain accurate.

**Acceptance Criteria**
- Existing customer can be edited.
- Changes are saved successfully.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

## CUS-005 - Delete Customer
**User Story**
As a pharmacist, I want to delete customer records when no longer needed.

**Acceptance Criteria**
- Confirmation dialog appears.
- Customer is removed.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

# Record Type: Sales

## SAL-001 - Create Sale
**User Story**
As a cashier, I want to record a sale so that medicine purchases are tracked.

**Acceptance Criteria**
- Medicine exists.
- Quantity does not exceed stock.
- Total amount is calculated automatically.
- Stock is updated after sale.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

## SAL-002 - View Sales List
**User Story**
As a cashier, I want to view all sales so that I can review completed transactions.

**Acceptance Criteria**
- Displays sales history.
- Displays customer name.
- Displays total amount.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

## SAL-003 - View Sale Details
**User Story**
As a cashier, I want to view transaction details so that I can verify completed sales.

**Acceptance Criteria**
- Displays purchased medicines.
- Displays payment details.
- Displays transaction total.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

## SAL-004 - Update Sale
**User Story**
As a cashier, I want to edit a sale before completion so that mistakes can be corrected.

**Acceptance Criteria**
- Sale can be edited before completion.
- Totals update automatically.
- Stock updates correctly.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

## SAL-005 - Delete Sale
**User Story**
As a cashier, I want to cancel an incorrect sale so that records remain accurate.

**Acceptance Criteria**
- Confirmation dialog appears.
- Sale is removed.
- Inventory is restored.

**Owner:** Jay-Ann Mariquit, Christine Ilonen, JM Harnaiz

---

# Summary

| Record Type | Stories |
|-------------|---------|
| Medicines | 5 |
| Suppliers | 5 |
| Customers | 5 |
| Sales | 5 |

**Total User Stories:** 20

---

## Screen Coverage

- Login
- Dashboard
- Medicines
- Medicine Details
- Add Medicine
- Edit Medicine
- Suppliers
- Customers
- Sales
- Sale Details
- Delete Confirmation
- Empty State
- Error State