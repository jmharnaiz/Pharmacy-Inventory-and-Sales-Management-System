# Reusable Components

Based on the Deliverable 1 wireframes, we have identified the following reusable UI components:

## 1. Layout & Navigation
*   **Sidebar** (`sidebar.html`): Left-hand navigation menu with branding and user profile. Used on all internal pages.
*   **Top Header** (`header.html`): Top bar containing page title, breadcrumbs, notifications, and date. Used on all internal pages.

## 2. Data Display
*   **Data Table** (`table.html` / `list_row.html`): A standard table structure with sortable headers, pagination, and a standard row format (Avatar/ID, Name, Meta, Status Badge, Actions).
*   **Status Badge** (`status_badge.html`): Pill-shaped badges indicating state (e.g., `In Stock` [Green], `Low Stock` [Orange], `Out of Stock` [Red], `Active`, `Inactive`).
*   **Stat Card** (`stat_card.html`): Used primarily on the dashboard for high-level metrics (e.g., Total Medicines, Today's Sales).

## 3. Forms & Inputs
*   **Form Group** (`form_group.html`): A standardized wrapper for a label, input field (text, select, date), and validation error text.
*   **Action Buttons** (`button.html`): Standardized primary (Green), secondary (Outline/Gray), and danger (Red) buttons.

## 4. UI States
*   **Empty State** (`empty_state.html`): An illustration, title, and "Add New" button shown when a table has 0 records.
*   **Loading State** (`spinner.html`): A visual spinner for async data fetching.
*   **Error State** (`error_banner.html`): A red banner/toast shown when a request fails or a 404 occurs.

## Screen to Component Mapping
*   **Medicines List**: Layout, Data Table, Status Badge, Action Buttons, Empty State.
*   **Add/Edit Medicine**: Layout, Form Groups, Action Buttons.
*   **Medicine Details**: Layout, Status Badge, Action Buttons.
*   **Login**: Form Groups, Action Buttons (No sidebar/header layout).
