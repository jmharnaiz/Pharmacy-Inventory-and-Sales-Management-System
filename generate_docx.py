import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

doc = docx.Document()

# Adjust margins
sections = doc.sections
for s in sections:
    s.top_margin = Inches(1)
    s.bottom_margin = Inches(1)
    s.left_margin = Inches(1)
    s.right_margin = Inches(1)

# Color Palette: Primary Emerald Green #0b8243, Slate #334155
PRIMARY_COLOR = RGBColor(11, 130, 67)
SLATE_COLOR = RGBColor(51, 65, 85)

# Title
title_p = doc.add_paragraph()
title_run = title_p.add_run("PHARMACY MANAGEMENT SYSTEM\nDEFENSE STUDY KIT & TECHNICAL REFERENCE")
title_run.font.name = 'Calibri'
title_run.font.size = Pt(22)
title_run.font.bold = True
title_run.font.color.rgb = PRIMARY_COLOR
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

subtitle_p = doc.add_paragraph()
sub_run = subtitle_p.add_run("Comprehensive Defense Guide, Architecture Breakdown, 5-Member Role Delegation, and Q&A Manual\n")
sub_run.font.size = Pt(12)
sub_run.font.italic = True
sub_run.font.color.rgb = SLATE_COLOR
subtitle_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph("─" * 60)

# Section 1: Executive Overview & Tech Stack
doc.add_heading("1. Executive Overview & Tech Stack", level=1)
p = doc.add_paragraph(
    "The Pharmacy Management System is a full-stack, layered monolith built for pharmaceutical retail operations. "
    "It addresses common store pain points: inaccurate inventory valuation, unmonitored medicine expiry/spoilage, "
    "untracked customer history, and sluggish manual reconciliation."
)
p_stack = doc.add_paragraph()
p_stack.add_run("Core Architecture Stack:\n").bold = True
p_stack.add_run("• Backend Framework: ").bold = True
p_stack.add_run("Python 3 + Flask (Modular Blueprints)\n")
p_stack.add_run("• Persistence Layer: ").bold = True
p_stack.add_run("SQLite 3 with foreign key schema constraints and ACID compliance\n")
p_stack.add_run("• Client/Frontend: ").bold = True
p_stack.add_run("Semantic HTML5, Jinja2 templating, Custom CSS (Emerald/Slate design system), Phosphor Icons\n")
p_stack.add_run("• Asynchronous View Binding: ").bold = True
p_stack.add_run("Vanilla JavaScript fetch API intercepted on form submissions to prevent full-page reloads\n")
p_stack.add_run("• Test Automation & QA: ").bold = True
p_stack.add_run("pytest with isolated file-based SQLite test runners\n")

# Section 2: How to Run the Application
doc.add_heading("2. How to Run the Application (Step-by-Step)", level=1)
run_steps = [
    ("Step 1: Open Terminal & Navigate to Directory", "Open PowerShell or Command Prompt:\ncd C:\\Users\\Administrator\\.gemini\\antigravity\\scratch\\pharmacy_management"),
    ("Step 2: Environment & Dependencies", "Install necessary packages:\npip install flask pytest python-docx python-pptx"),
    ("Step 3: Database Initialization & Seeding", "Generate schemas and populate 10+ realistic records per entity:\npython -c \"import db; db.init_db()\"\npython seed.py"),
    ("Step 4: Launch Flask Web Server", "Start the application:\npython app.py\n(Server listens on http://127.0.0.1:5000)"),
    ("Step 5: Sign In", "Open your web browser at http://127.0.0.1:5000\nDefault Admin Credentials:\n• Username: admin\n• Password: admin123"),
    ("Step 6: Execute Automated Test Suite", "Validate regression and adversarial protections:\npytest tests/")
]
for title, desc in run_steps:
    p_step = doc.add_paragraph()
    p_step.add_run(f"{title}\n").bold = True
    p_step.add_run(desc)

# Section 3: 5-Member Team Role Delegation
doc.add_heading("3. 5-Member Team Role Assignments (For Presentation & Defense)", level=1)
doc.add_paragraph(
    "To satisfy the academic rubric requirements (individual unassisted code defense), responsibilities are assigned across 5 distinct domains:"
)

roles_data = [
    ("Member 1: Project Lead & Auth/Routing Architect", 
     "app.py, routes/extras.py, session filters", 
     "System narrative, login guard clause (@app.before_request), session state management, and high-level routing."),
    ("Member 2: Inventory & Medicine Module Lead", 
     "routes/medicines.py, controllers/medicines.py", 
     "Medicines CRUD, adversarial guard validation (XSS prevention, 32-bit max integer capping), and standard JSON response envelope."),
    ("Member 3: Sales, Customers & Transaction Engine Lead", 
     "routes/sales.py, routes/customers.py, controllers/sales.py", 
     "Invoice generation, foreign key relationships, customer binding, and input sanitization on financial amounts."),
    ("Member 4: Procurement, Inventory Adjustment & Reports Lead", 
     "controllers/suppliers.py, routes/extras.py, db.py", 
     "Supplier pipelines, stock adjustments that directly alter inventory levels (current_stock = current_stock + qty), and live report revenue calculations."),
    ("Member 5: Frontend Experience & QA/Test Automation Lead", 
     "static/css/style.css, templates/*.html, tests/*", 
     "Async fetch lifecycle handling (spinners, disabling submit buttons, inline 422 error display without page reload), and pytest test matrix.")
]

for name, files, resp in roles_data:
    p_role = doc.add_paragraph()
    r_title = p_role.add_run(f"• {name}\n")
    r_title.bold = True
    r_title.font.color.rgb = PRIMARY_COLOR
    p_role.add_run(f"  - Owned Files: {files}\n")
    p_role.add_run(f"  - Defense Focus: {resp}\n")

# Section 4: Oral Defense Q&A Cheatsheet
doc.add_heading("4. Oral Defense Questions & Answers (Unassisted Preparation)", level=1)
qa_list = [
    ("Q1: Where does input validation live in this system, and why?",
     "Answer: Validation is implemented as strict 'guard clauses' located at the very beginning of route handlers (e.g. routes/medicines.py::validate_medicine) before hitting controllers. This protects database integrity, ensures malicious inputs or missing keys never execute SQL queries, and provides consistent 422 Unprocessable Entity responses with exact field names."),
    ("Q2: How does the frontend handle form submissions without refreshing the browser?",
     "Answer: We intercept the standard HTML form submit event with event.preventDefault(). A JavaScript listener extracts inputs into a FormData object, formats it as JSON, and sends an asynchronous fetch() request. If a 422 error returns, it paints inline error messages under the target inputs; if 200/201 returns, it updates the view or redirects cleanly."),
    ("Q3: What happened during adversarial testing in Week 10, and how was it resolved?",
     "Answer: Adversarial QA identified two critical vulnerabilities: (1) XSS injection via <script> tags in medicine names, and (2) SQLite database overflow when current_stock was sent as a huge integer exceeding 32-bit limits. In Week 11, we hardened the validation guard to block <script> strings and enforce stock limits (<= 2,147,483,647). Both are verified via automated pytest test cases."),
    ("Q4: How does the Stock Adjustment module affect inventory?",
     "Answer: Unlike passive logging tables, the adjustment endpoint runs an UPDATE statement: 'UPDATE medicines SET current_stock = current_stock + ? WHERE id = ?'. This dynamically recalculates inventory levels so physical counts or damaged lots immediately sync across the dashboard and sales validation."),
    ("Q5: Why did you choose SQLite and Flask over larger frameworks?",
     "Answer: The lightweight modularity of Flask Blueprints coupled with SQLite provides complete transparent control over SQL execution, query performance, and test isolation without heavy ORM overhead, perfectly matching the requirements of an embedded local management system.")
]

for q, a in qa_list:
    p_qa = doc.add_paragraph()
    q_run = p_qa.add_run(f"{q}\n")
    q_run.bold = True
    q_run.font.color.rgb = PRIMARY_COLOR
    p_qa.add_run(f"{a}\n")

# Section 5: Live Demo Click-Path Script
doc.add_heading("5. Live Demo Rehearsal Click-Path Script", level=1)
script_steps = [
    "1. Start at Login: Show security by typing invalid credentials (see human-readable error), then log in with admin / admin123.",
    "2. View Dashboard: Point to the 4 top metrics (Medicines, Inventory Value, Sales, Customers) that update dynamically from database totals.",
    "3. Demonstrate Graceful Failure (Rubric Requirement): Go to 'Add Medicine', leave Medicine Name blank and enter a negative price (-5.00). Click Save. Point out that the page DOES NOT crash or reload; an inline red error appears.",
    "4. Happy Path Creation: Enter 'Amoxicillin 500mg', Price 15.00, Cost 7.00, Stock 250. Click Save. Show that it immediately renders in the medicines list.",
    "5. Sales & Inventory Sync: Navigate to Sales, record a sale. Navigate to Stock Adjustment to demonstrate active inventory updates.",
    "6. Conclude with Reports: Display the live financial breakdown (Total Revenue, Purchases, and Net Profit Margin)."
]
for s in script_steps:
    doc.add_paragraph(s)

doc.save("Study_Kit.docx")
print("Study_Kit.docx generated successfully!")
