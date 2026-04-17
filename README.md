# AEC Seismic Risk Platform

A comprehensive geospatial platform for portfolio exposure and seismic vulnerability analysis, following RPA 99/2003 regulations.

## Project Structure

- `backend/`: FastAPI server processing portfolio data and seismic risk evaluation.
- `web_dashboard/`: React (Vite) based analytics dashboard for underwriters.
- `mobile_dashboard/`: Expo (React Native) mobile application for field agents.
- `data/`: Storage for portfolio files (XLSX), GeoJSON maps, and processed caches.
- `docs/`: Regulatory documents, specifications, and extracted text from RPA documents.

## Getting Started

### Backend
1. `cd backend`
2. `pip install -r requirements.txt` (Make sure to generate this if missing)
3. `python main.py`

### Web Dashboard
1. `cd web_dashboard`
2. `npm install`
3. `npm run dev`

### Mobile Dashboard
1. `cd mobile_dashboard`
2. `npm install`
3. `npx expo start`

## Technologies
- **Python/FastAPI**: Backend logic and AI scoring.
- **CatBoost**: Machine learning for premium assessment.
- **Leaflet/React-Leaflet**: Geospatial visualization.
- **React/Vite**: Modern web frontend.
- **Expo**: Cross-platform mobile development.
