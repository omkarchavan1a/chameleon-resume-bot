# CONVENTIONS

## Backend (Python)
- **Framework conventions**: Leverages FastAPI's dependency injection and Pydantic for request/response serialization.
- **Code Style**: Implicit adherence to standard Python PEP 8 conventions for naming and structure. 
- **Documentation**: Use of docstrings to define the purpose of API endpoints. Pydantic models document the expected payload schemas.

## Frontend (JavaScript / HTML / CSS)
- **Structure**: Vanilla implementation; separation of concerns (HTML for structure, CSS for presentation, JS for behavior). 
- **Styling**: Class-based CSS with variables. 
- **DOM**: Direct DOM interactions with `document.querySelector` / `document.getElementById`. Event delegation is likely used given the Vanilla JS nature.
