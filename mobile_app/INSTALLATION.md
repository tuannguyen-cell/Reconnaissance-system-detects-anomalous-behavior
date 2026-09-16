# Hướng dẫn cài đặt Behavior Monitor Mobile App

## Yêu cầu hệ thống

### Phần mềm bắt buộc
- **Node.js**: Phiên bản 16.x trở lên
- **Java Development Kit (JDK)**: Phiên bản 11 trở lên
- **Android Studio**: Để phát triển và build Android
- **React Native CLI**: Công cụ dòng lệnh của React Native

### Phần mềm tùy chọn (cho iOS)
- **Xcode**: Chỉ cần nếu muốn build cho iOS (macOS only)
- **CocoaPods**: Quản lý dependencies cho iOS

## Cài đặt môi trường

### 1. Cài đặt Node.js
- Tải và cài đặt từ: https://nodejs.org/
- Kiểm tra phiên bản: `node --version` (cần >= 16.x)

### 2. Cài đặt JDK
- Tải JDK 11 hoặc mới hơn từ: https://www.oracle.com/java/technologies/downloads/
- Cài đặt JAVA_HOME environment variable

### 3. Cài đặt Android Studio
- Tải từ: https://developer.android.com/studio
- Cài đặt Android SDK (API Level 33 trở lên)
- Cài đặt Android SDK Build-Tools
- Cài đặt Android SDK Platform-Tools
- Cài đặt Android Emulator hoặc kết nối thiết bị thật

### 4. Cài đặt React Native CLI
```bash
npm install -g react-native-cli
```

## Cài đặt project

### 1. Di chuyển vào thư mục project
```bash
cd mobile_app
```

### 2. Cài đặt dependencies
```bash
npm install
```

### 3. Cài đặt dependencies cho Android
```bash
cd android
./gradlew clean
cd ..
```

## Chạy ứng dụng

### Trên Android Emulator
1. Mở Android Studio và khởi tạo Emulator
2. Chạy ứng dụng:
```bash
npx react-native run-android
```

### Trên thiết bị Android thật
1. Bật Developer Options trên điện thoại
2. Bật USB Debugging
3. Kết nối điện thoại qua USB
4. Chạy:
```bash
npx react-native run-android
```

### Chạy Metro server (nếu cần)
```bash
npx react-native start
```

## Khắc phục sự cố

### Lỗi "SDK location not found"
- Thiết lập ANDROID_HOME environment variable
- Hoặc tạo file `local.properties` trong thư mục `android/` với:
```
sdk.dir=C:\\Users\\[USERNAME]\\AppData\\Local\\Android\\Sdk
```

### Lỗi "Gradle build failed"
```bash
cd android
./gradlew clean
cd ..
npx react-native run-android
```

### Lỗi Metro server
```bash
npx react-native start --reset-cache
```

### Lỗi dependencies
```bash
rm -rf node_modules
npm install
```

### Lỗi kết nối ADB
```bash
adb devices
adb reverse tcp:8081 tcp:8081
```

## Cấu hình nâng cao

### Thay đổi package name
- Sửa trong `android/app/build.gradle`
- Sửa trong `android/app/src/main/AndroidManifest.xml`
- Sửa trong `android/app/src/main/java/com/behaviormonitor/`

### Thay đổi tên ứng dụng
- Sửa trong `app.json`
- Sửa trong `android/app/src/main/res/values/strings.xml`

### Build release APK
```bash
cd android
./gradlew assembleRelease
```
APK sẽ nằm ở: `android/app/build/outputs/apk/release/`

## Tài liệu tham khảo

- [React Native Documentation](https://reactnative.dev/)
- [React Native Android Setup](https://reactnative.dev/docs/environment-setup)
- [Android Studio Documentation](https://developer.android.com/studio)

## Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra log trong terminal
2. Kiểm tra log trong Android Studio Logcat
3. Xem tài liệu React Native chính thức
4. Kiểm tra GitHub issues của project

## Lưu ý quan trọng

- Đây là phiên bản demo với mock data
- Camera hiện được giả lập, cần tích hợp camera thật cho production
- Backend API cần được triển khai theo spec trong MOBILE_APP_GUIDE.md
- App hỗ trợ cả Android và iOS (cross-platform)
- Cần test kỹ trên các thiết bị khác nhau trước khi release
