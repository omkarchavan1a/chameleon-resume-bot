# ROADMAP

## Phase 0: Codebase Mapping
- [x] Auto-map the project architecture
- [x] Create the STACK, ARCHITECTURE, CONVENTIONS, and CONCERNS documentation.

## Phase 1: Project Organization
- [x] Setup `.planning/` directory
- [x] Create PROJECT, ROADMAP, REQUIREMENTS

## Phase 2: Security Refactor
- [x] Move API key to `.env` file
- [x] Update `main.py` referencing `os.getenv`
- [x] Update `requirements.txt`

## Phase 3: PDF Resume Upload & Optimization
- [x] Integrate `pdfplumber` for text extraction
- [x] Add PDF upload UI to frontend
- [x] Integrate extracted text into generation flow

## Phase 4: MongoDB Integration
- [ ] Add `motor` and `pymongo` dependencies
- [ ] Configure `MONGODB_URI` in `.env`
- [ ] Implement persistent generation history
- [ ] Implement history viewing in the frontend logic
