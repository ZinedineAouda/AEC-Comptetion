@echo off
echo =======================================================
echo Starting AEC-Competition Dashboard Environment
echo =======================================================

echo.
echo Starting Python Backend Framework (Port 8000)...
start "AEC Backend" cmd /k "color 0B && title AEC Backend && cd backend && echo Starting API Server... && python -m uvicorn main:app --reload --port 8000"

echo.
echo Starting React Web Dashboard (Vite)...
start "AEC Frontend" cmd /k "color 0D && title AEC Frontend && cd web_dashboard && echo Starting React Local Server... && npm run dev"

echo.
echo =======================================================
echo All services have been launched in separate console windows.
echo   - Backend API: http://localhost:8000
echo   - Frontend UI: http://localhost:5173
echo =======================================================
