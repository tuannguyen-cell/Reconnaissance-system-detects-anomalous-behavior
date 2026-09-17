# Behavior Monitor Expo App

The mobile demo runs with Expo and uses mock detection data.

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

The app currently uses a simulated camera feed. Backend integration can be added later through `src/services/mockApi.ts`.