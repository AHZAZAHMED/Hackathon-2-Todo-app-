# Minikube Testing Guide - Port-Forward Solution

## Problem
Port-forwards running in background keep stopping, causing 404 errors when accessing the application.

## Solution
Run port-forwards in separate terminal windows that stay open.

---

## Step 1: Start Port-Forwards

### Option A: Using Batch Script (Windows)

1. **Run the batch script**:
   ```
   E:\Hackathon-2\phase-4\start-port-forwards.bat
   ```

2. **Two new windows will open**:
   - Backend Port-Forward (port 8002)
   - Frontend Port-Forward (port 3000)

3. **Keep both windows open** while testing

### Option B: Manual (Two Separate Terminals)

**Terminal 1 - Backend**:
```bash
kubectl port-forward service/todo-app-ai-todo-app-backend 8002:8000
```

**Terminal 2 - Frontend**:
```bash
kubectl port-forward service/todo-app-ai-todo-app-frontend 3000:3000
```

Keep both terminals open.

---

## Step 2: Verify Connectivity

```bash
# Test backend
curl http://localhost:8002/api/health

# Test frontend
curl http://localhost:3000
```

---

## Step 3: Clear Browser Cache

**CRITICAL**: Clear browser data before testing

1. Press Ctrl+Shift+Delete
2. Select "Cookies and other site data"
3. Select "Cached images and files"
4. Click "Clear data"

---

## Step 4: Test Application

1. Open browser: http://localhost:3000
2. Sign up or login
3. Dashboard should load without 404 errors
4. Test task management (create, list, update, delete)
5. Test AI chatbot

---

## Troubleshooting

### Issue: 404 Error on /tasks

**Solution**:
1. Check if port-forward windows are still open
2. If closed, restart using batch script
3. Clear browser cache
4. Refresh page

### Issue: "Couldn't get access token"

**Solution**:
1. Clear browser cookies and cache
2. Logout and login again
3. Or use Incognito mode

---

**Port Configuration**: Backend=8002, Frontend=3000
