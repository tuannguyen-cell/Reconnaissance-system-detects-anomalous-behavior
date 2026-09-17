import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { StatusBar } from 'react-native';
import { theme } from './src/theme';

// Screens
import ConnectScreen from './src/screens/ConnectScreen';
import HomeScreen from './src/screens/HomeScreen';
import MonitorScreen from './src/screens/MonitorScreen';
import HistoryScreen from './src/screens/HistoryScreen';
import StatisticsScreen from './src/screens/StatisticsScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import DetectionDetailScreen from './src/screens/DetectionDetailScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar barStyle="dark-content" backgroundColor={theme.colors.background} />
      <Stack.Navigator
        initialRouteName="Connect"
        screenOptions={{
          headerStyle: {
            backgroundColor: theme.colors.primary,
          },
          headerTintColor: theme.colors.surface,
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        <Stack.Screen 
          name="Connect" 
          component={ConnectScreen}
          options={{ title: 'Kết nối' }}
        />
        <Stack.Screen 
          name="Home" 
          component={HomeScreen}
          options={{ title: 'Trang chủ' }}
        />
        <Stack.Screen 
          name="Monitor" 
          component={MonitorScreen}
          options={{ title: 'Giám sát' }}
        />
        <Stack.Screen 
          name="History" 
          component={HistoryScreen}
          options={{ title: 'Lịch sử' }}
        />
        <Stack.Screen 
          name="DetectionDetail" 
          component={DetectionDetailScreen}
          options={{ title: 'Chi tiết phát hiện' }}
        />
        <Stack.Screen 
          name="Statistics" 
          component={StatisticsScreen}
          options={{ title: 'Thống kê' }}
        />
        <Stack.Screen 
          name="Settings" 
          component={SettingsScreen}
          options={{ title: 'Cài đặt' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
