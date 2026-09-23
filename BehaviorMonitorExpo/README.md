# Behavior Monitor Expo App

The mobile app connects to the FastAPI backend and sends camera frames as base64 images.

## Run the backend

From the repository root:

```powershell
python -m pip install -r backend/requirements.txt
cd backend
python run_server.py
```

The API is available at `http://localhost:8000/api/v1`. On the connection screen,
enter a server URL, username, and password with at least 8 characters. A new user
is registered automatically when the username does not exist.

For an Android emulator use `http://10.0.2.2:8000`. For a physical phone, use
the computer's LAN IP, for example `http://192.168.1.10:8000`, and ensure both
devices are on the same network.

## Run on Android Emulator

```powershell
cd BehaviorMonitorExpo
npx expo start --android
```

If Expo selects another port, accept it. The Android emulator can be opened from the Expo terminal with `a`.

## Validate the project

```powershell
npx tsc --noEmit
npx expo export --platform android
```

The monitoring screen requests camera permission, captures frames, and sends them
to `/api/v1/detection/detect`. The JWT token is stored locally for subsequent
history and statistics requests.