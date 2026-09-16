# Behavior Monitor Mobile App

Ứng dụng mobile giám sát hành vi thông minh bằng AI - Demo Version

## 🎯 Tính năng

### MVP Features
- ✅ Kết nối backend (mock data)
- ✅ Camera realtime (simulated)
- ✅ Hiển thị normal/abnormal và confidence
- ✅ Cảnh báo âm thanh/rung tùy chọn
- ✅ Lịch sử phát hiện
- ✅ Thống kê cơ bản
- ✅ Cài đặt threshold và các tùy chọn khác

### Các màn hình chính
1. **ConnectScreen**: Màn hình kết nối server
2. **HomeScreen**: Trang chủ với tóm tắt trạng thái
3. **MonitorScreen**: Màn hình giám sát realtime
4. **HistoryScreen**: Lịch sử các phát hiện
5. **DetectionDetailScreen**: Chi tiết từng phát hiện
6. **StatisticsScreen**: Thống kê và biểu đồ
7. **SettingsScreen**: Cài đặt ứng dụng

## 🚀 Cài đặt

### Yêu cầu
- Node.js >= 16
- React Native CLI
- Android Studio (cho Android) hoặc Xcode (cho iOS)
- JDK 11+

### Các bước cài đặt

1. Cài đặt dependencies:
```bash
cd mobile_app
npm install
```

2. Cài đặt React Native CLI:
```bash
npm install -g react-native-cli
```

3. Cài đặt dependencies cho Android:
```bash
cd android
./gradlew clean
cd ..
```

4. Chạy ứng dụng:

**Cho Android:**
```bash
npx react-native run-android
```

**Cho iOS:**
```bash
npx react-native run-ios
```

**Hoặc start Metro server:**
```bash
npx react-native start
```

## 📱 Cấu trúc project

```
mobile_app/
├── src/
│   ├── screens/          # Các màn hình chính
│   │   ├── ConnectScreen.tsx
│   │   ├── HomeScreen.tsx
│   │   ├── MonitorScreen.tsx
│   │   ├── HistoryScreen.tsx
│   │   ├── DetectionDetailScreen.tsx
│   │   ├── StatisticsScreen.tsx
│   │   └── SettingsScreen.tsx
│   ├── components/       # Các component dùng lại
│   ├── navigation/       # Cấu hình navigation
│   ├── services/         # API services (mock)
│   │   └── mockApi.ts
│   ├── theme/           # Theme và styles
│   │   ├── colors.ts
│   │   ├── typography.ts
│   │   ├── spacing.ts
│   │   └── index.ts
│   ├── types/           # TypeScript types
│   │   └── index.ts
│   └── utils/           # Utility functions
├── App.tsx              # Entry point
├── package.json
├── tsconfig.json
├── babel.config.js
├── metro.config.js
└── README.md
```

## 🔧 Cấu hình

### Mock API
App hiện tại sử dụng mock API service (`src/services/mockApi.ts`) để giả lập backend. Khi backend thật sẵn sàng, thay thế mockApi bằng API calls thật.

### Theme
Theme được định nghĩa trong `src/theme/` với:
- Colors: các màu sắc UI
- Typography: font sizes và weights
- Spacing: khoảng cách padding/margin

## 📊 Luồng sử dụng chính

1. Mở app → Màn hình Connect
2. Nhập địa chỉ server → Kết nối
3. Màn hình Home → Xem trạng thái server
4. Bắt đầu giám sát → MonitorScreen
5. Camera gửi dữ liệu → Nhận kết quả
6. Hiển thị cảnh báo nếu abnormal
7. Xem lịch sử/thống kê → History/Statistics
8. Cài đặt → SettingsScreen

## 🎨 Giao diện

### Màu sắc trạng thái
- **Normal**: Xanh lá (#4CAF50)
- **Abnormal**: Đỏ (#F44336)
- **Connecting**: Vàng (#FF9800)
- **Error**: Đỏ đậm (#D32F2F)

### Nguyên tắc thiết kế
- Ưu tiên thao tác nhanh, dễ đọc
- Màn hình giám sát là trọng tâm
- Hỗ trợ tiếng Việt đầy đủ
- Touch target tối thiểu 44x44 dp
- Hỗ trợ màn hình nhỏ và xoay dọc

## 🔜 Tính năng mở rộng (sau MVP)

- Tài khoản và phân quyền
- Nhiều camera hoặc nhiều khu vực
- Đồng bộ cloud
- Push notification khi app chạy nền
- Dashboard quản trị
- On-device inference bằng TFLite
- Xuất báo cáo CSV/PDF

## 🐛 Troubleshooting

### Android build fails
```bash
cd android
./gradlew clean
cd ..
npx react-native run-android
```

### Metro server không start
```bash
npx react-native start --reset-cache
```

### Dependencies issues
```bash
rm -rf node_modules
npm install
```

## 📝 Ghi chú

- Đây là phiên bản demo với mock data
- Camera hiện được giả lập, cần tích hợp camera thật
- Backend API cần được triển khai theo spec trong MOBILE_APP_GUIDE.md
- App hỗ trợ cả Android và iOS (cross-platform)

## 🤝 Đóng góp

Đây là project demo, phát triển theo spec trong MOBILE_APP_GUIDE.md

## 📄 License

Demo project cho mục đích học tập và phát triển
