@echo off
echo Starting port-forwards for Minikube deployment...
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8002
echo.
echo Press Ctrl+C to stop port-forwarding
echo.

start "Backend Port-Forward" kubectl port-forward service/todo-app-ai-todo-app-backend 8002:8000
timeout /t 2 /nobreak >nul
start "Frontend Port-Forward" kubectl port-forward service/todo-app-ai-todo-app-frontend 3000:3000

echo.
echo Port-forwards started in separate windows
echo Keep these windows open while testing
echo.
pause
