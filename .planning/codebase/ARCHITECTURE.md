# ARCHITECTURE

## Overview
The application follows a simple, monolithic client-server architecture. The backend serves both the API endpoints and the static frontend assets.

## Client (Frontend)
- **Vanilla SPA**: A single-page application built without heavy frameworks. 
- **State Management**: Local state managed dynamically within `app.js`.
- **Communication**: Interacts with the backend via RESTful JSON web services using the browser's native `fetch` API.

## Server (Backend)
- **FastAPI Application**: Stateless application logic.
- **Static File Serving**: Mounts the `frontend/` directory to serve the frontend directly.
- **REST API**: Exposes JSON endpoints (`/api/generate-resume`, `/api/refine-resume`) for the frontend to consume. Models are managed by Pydantic.
- **External Integration**: The backend acts as a proxy between the client and the NVIDIA NIM AI service, building prompts logically before sending out requests.
