# AI Prompt Log (Week 6)

*AI use is ON and required for this phase.*

**AI Assistant Used**: Antigravity (Gemini)

## 1. Scaffolding the Data Table & Empty State
**Prompt**: "Generate a semantic HTML table for the Medicines list based on the wireframe. It should have columns for #, Medicine Name, Generic Name, Category, Stock, Unit Price, Status, and Actions. Also, generate the HTML for the empty state shown in the wireframes (a box illustration with 'No medicines found'). Provide the CSS to match the wireframe's green/white styling, including the status badges."
**Result**: AI-generated. The AI produced clean semantic HTML (`<table>`, `<thead>`, `<tbody>`). I manually reviewed and added the Jinja templating conditional (`{% if medicines %}`) to toggle between the table and the empty state.

## 2. Scaffolding the Add/Edit Form
**Prompt**: "Generate a static HTML form for 'Add New Medicine' matching the wireframe. It needs sections for Medicine Information, Pricing & Stock Information, Supplier Information, and an Image Upload area. Use semantic HTML5 inputs."
**Result**: AI-generated, hand-modified. The AI built a solid grid layout. I had to manually adjust the column spanning for the "Description" field to match the wireframe layout exactly, and I added the Jinja `value="{{ medicine.name }}"` tags to support reusing it for the Edit state.

## 3. Scaffolding the Login Screen
**Prompt**: "Generate the Login screen HTML and CSS matching the wireframe. It has a split design or a centered card with the Pharmacy logo, Username, Password, Remember Me checkbox, and a green Login button."
**Result**: AI-generated. The AI provided the layout. I made minor tweaks to the padding and shadow CSS to better match the specific visual weight of the wireframe.

**Integrity Signature**: All AI output was reviewed line-by-line for accessibility, semantics, and wireframe fidelity before committing.
