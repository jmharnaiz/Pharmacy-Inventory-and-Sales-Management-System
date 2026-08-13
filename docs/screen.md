# System Screens

This document contains the list and description of the screens included in the Pharmacy Inventory and Sales Management System.

## Screen List

| #  | Screen              | File                      | Description                                                           |
| -- | ------------------- | ------------------------- | --------------------------------------------------------------------- |
| 1  | Login               | `login.png`               | Allows authorized users to securely access the system.                |
| 2  | Dashboard           | `dashboard.png`           | Displays an overview of the pharmacy system and key information.      |
| 3  | Medicines           | `medicines.png`           | Displays the list of medicines and available management actions.      |
| 4  | Medicine Details    | `medicine-details.png`    | Displays complete information about a selected medicine.              |
| 5  | Add Medicine        | `add-medicine.png`        | Allows users to add a new medicine record.                            |
| 6  | Edit Medicine       | `edit-medicine.png`       | Allows users to modify existing medicine information.                 |
| 7  | Suppliers           | `suppliers.png`           | Displays supplier records and available management actions.           |
| 8  | Customers           | `customer.png`            | Displays customer records and available management actions.           |
| 9  | Sales               | `sales.png`               | Displays sales transactions and allows users to manage sales records. |
| 10 | Sale Details        | `sale-details.png`        | Displays complete information about a selected sale.                  |
| 11 | Delete Confirmation | `delete-confirmation.png` | Confirms before deleting a record.                                    |
| 12 | Empty State         | `empty-state.png`         | Displays when there are no records or search results available.       |

---

# 1. Login Screen

**File:** `login.png`

The Login Screen is the entry point of the system. Users must provide valid credentials before accessing the Pharmacy Inventory and Sales Management System.

### Components

* Username field
* Password field
* Login button
* System logo/branding
* Error or validation message

---

# 2. Dashboard Screen

**File:** `dashboard.png`

The Dashboard provides an overview of the pharmacy system after successful login.

### Components

* Navigation menu
* Total medicines
* Low-stock medicines
* Total suppliers
* Total customers
* Daily sales
* Recent sales
* Quick actions
* System overview

### Purpose

Allows authorized users to quickly view important pharmacy information.

---

# 3. Medicines Screen

**File:** `medicines.png`

The Medicines Screen displays the medicines currently recorded in the pharmacy inventory.

### Components

* Medicine table
* Medicine ID
* Medicine name
* Category
* Price
* Stock quantity
* Expiration date
* Search functionality
* Add Medicine button
* View action
* Edit action
* Delete action

### Purpose

Allows authorized users to view and manage medicine records.

---

# 4. Medicine Details Screen

**File:** `medicine-details.png`

The Medicine Details Screen displays complete information about a selected medicine.

### Components

* Medicine ID
* Medicine name
* Category
* Brand
* Supplier
* Unit price
* Stock quantity
* Expiration date
* Medicine status
* Edit button
* Delete button
* Back button

### Purpose

Allows users to review complete medicine information.

---

# 5. Add Medicine Screen

**File:** `add-medicine.png`

The Add Medicine Screen is used to add a new medicine to the pharmacy inventory.

### Components

* Medicine name
* Category
* Brand
* Supplier
* Unit price
* Stock quantity
* Expiration date
* Save button
* Cancel button

### Purpose

Allows users to create a new medicine record.

---

# 6. Edit Medicine Screen

**File:** `edit-medicine.png`

The Edit Medicine Screen allows users to update information belonging to an existing medicine.

### Components

* Existing medicine information
* Medicine name
* Category
* Brand
* Supplier
* Unit price
* Stock quantity
* Expiration date
* Update button
* Cancel button

### Purpose

Allows users to correct or update medicine information.

---

# 7. Suppliers Screen

**File:** `suppliers.png`

The Suppliers Screen displays supplier records registered in the system.

### Components

* Supplier table
* Supplier ID
* Company name
* Contact person
* Phone number
* Email address
* Address
* Search functionality
* Add Supplier button
* Edit action
* Delete action

### Purpose

Allows users to view and manage supplier information.

---

# 8. Customers Screen

**File:** `customer.png`

The Customers Screen displays customer records registered in the system.

### Components

* Customer table
* Customer ID
* Customer name
* Contact number
* Email address
* Address
* Search functionality
* Add Customer button
* Edit action
* Delete action

### Purpose

Allows users to view and manage customer information.

---

# 9. Sales Screen

**File:** `sales.png`

The Sales Screen displays sales transactions recorded by the pharmacy.

### Components

* Sales table
* Sale ID
* Transaction date
* Customer
* Total amount
* Payment method
* Search functionality
* Add Sale button
* View action
* Edit action
* Delete action

### Purpose

Allows users to record and manage pharmacy sales transactions.

---

# 10. Sale Details Screen

**File:** `sale-details.png`

The Sale Details Screen displays complete information about a selected sales transaction.

### Components

* Sale ID
* Transaction date
* Customer
* Medicines purchased
* Quantity
* Unit price
* Total amount
* Payment method
* Back button

### Purpose

Allows users to review complete sales transaction information.

---

# 11. Delete Confirmation Screen

**File:** `delete-confirmation.png`

The Delete Confirmation Screen appears when a user attempts to delete a record.

### Components

* Confirmation message
* Record information
* Delete/Confirm button
* Cancel button

### Purpose

Prevents accidental deletion of medicine, supplier, customer, or sales records.

---

# 12. Empty State Screen

**File:** `empty-state.png`

The Empty State Screen is displayed when there are no available records or data.

### Examples

* No medicines registered
* No suppliers registered
* No customers registered
* No sales records
* No search results

### Purpose

Provides clear feedback instead of displaying a blank screen.

---

# Screen Navigation Flow

```text
Login
  |
  v
Dashboard
  |
  +----> Medicines
  |         |
  |         +----> Medicine Details
  |         |
  |         +----> Add Medicine
  |         |
  |         +----> Edit Medicine
  |         |
  |         +----> Delete Confirmation
  |
  +----> Suppliers
  |         |
  |         +----> Add / Edit / Delete Supplier
  |
  +----> Customers
  |         |
  |         +----> Add / Edit / Delete Customer
  |
  +----> Sales
            |
            +----> Sale Details
            |
            +----> Add / Edit / Delete Sale
```
