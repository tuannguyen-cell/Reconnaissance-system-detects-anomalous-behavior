import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Switch,
  Slider,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { theme } from '../theme';
import { mockApi } from '../services/mockApi';
import { AppSettings } from '../types';
import { useNavigation } from '@react-navigation/native';

const SettingsScreen: React.FC = () => {
  const navigation = useNavigation();
  const [settings, setSettings] = useState<AppSettings>({
    serverUrl: 'http://localhost:8000',
    threshold: 0.5,
    soundEnabled: true,
    vibrationEnabled: true,
    alertCooldown: 5,
    imageQuality: 'medium',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [serverStatus, setServerStatus] = useState<'ok' | 'error' | 'connecting'>('ok');

  const handleSaveSettings = async () => {
    setIsLoading(true);
    try {
      await mockApi.saveSettings(settings);
      Alert.alert('Thành công', 'Cài đặt đã được lưu');
    } catch (error) {
      Alert.alert('Lỗi', 'Không thể lưu cài đặt');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTestConnection = async () => {
    setServerStatus('connecting');
    try {
      await mockApi.connectToServer(settings.serverUrl);
      setServerStatus('ok');
      Alert.alert('Thành công', 'Đã kết nối đến server');
    } catch (error) {
      setServerStatus('error');
      Alert.alert('Lỗi', 'Không thể kết nối đến server');
    }
  };

  const handleLogout = () => {
    Alert.alert(
      'Đăng xuất',
      'Bạn có chắc chắn muốn đăng xuất?',
      [
        { text: 'Hủy', style: 'cancel' },
        { 
          text: 'Đăng xuất', 
          style: 'destructive',
          onPress: () => navigation.reset({
            index: 0,
            routes: [{ name: 'Connect' as never }],
          })
        },
      ]
    );
  };

  const getStatusColor = () => {
    switch (serverStatus) {
      case 'ok':
        return theme.colors.normal;
      case 'error':
        return theme.colors.error;
      default:
        return theme.colors.connecting;
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Server Settings */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Cài đặt Server</Text>
          
          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>Địa chỉ Server</Text>
            <TextInput
              style={styles.settingInput}
              value={settings.serverUrl}
              onChangeText={(text) => setSettings({ ...settings, serverUrl: text })}
              placeholder="http://localhost:8000"
              autoCapitalize="none"
              keyboardType="url"
            />
          </View>

          <TouchableOpacity
            style={styles.testButton}
            onPress={handleTestConnection}
            disabled={serverStatus === 'connecting'}
          >
            {serverStatus === 'connecting' ? (
              <ActivityIndicator color={theme.colors.surface} />
            ) : (
              <>
                <View style={[styles.statusDot, { backgroundColor: getStatusColor() }]} />
                <Text style={styles.testButtonText}>Kiểm tra kết nối</Text>
              </>
            )}
          </TouchableOpacity>
        </View>

        {/* Detection Settings */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Cài đặt Phát hiện</Text>
          
          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>Threshold ({(settings.threshold * 100).toFixed(0)}%)</Text>
            <Slider
              style={styles.slider}
              minimumValue={0}
              maximumValue={1}
              step={0.05}
              value={settings.threshold}
              onValueChange={(value) => setSettings({ ...settings, threshold: value })}
              minimumTrackTintColor={theme.colors.primary}
              maximumTrackTintColor={theme.colors.border}
            />
            <Text style={styles.settingHelper}>
              Ngưỡng phát hiện hành vi bất thường
            </Text>
          </View>

          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>Chất lượng ảnh</Text>
            <View style={styles.qualityOptions}>
              {(['low', 'medium', 'high'] as const).map((quality) => (
                <TouchableOpacity
                  key={quality}
                  style={[
                    styles.qualityButton,
                    settings.imageQuality === quality && styles.qualityButtonActive,
                  ]}
                  onPress={() => setSettings({ ...settings, imageQuality: quality })}
                >
                  <Text
                    style={[
                      styles.qualityButtonText,
                      settings.imageQuality === quality && styles.qualityButtonTextActive,
                    ]}
                  >
                    {quality === 'low' ? 'Thấp' : quality === 'medium' ? 'Trung bình' : 'Cao'}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>

        {/* Alert Settings */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Cài đặt Cảnh báo</Text>
          
          <View style={styles.settingItem}>
            <View style={styles.switchRow}>
              <Text style={styles.settingLabel}>Âm thanh cảnh báo</Text>
              <Switch
                value={settings.soundEnabled}
                onValueChange={(value) => setSettings({ ...settings, soundEnabled: value })}
                trackColor={{ false: theme.colors.border, true: theme.colors.primary }}
                thumbColor={settings.soundEnabled ? theme.colors.primary : theme.colors.textSecondary}
              />
            </View>
            <Text style={styles.settingHelper}>
              Phát âm thanh khi phát hiện hành vi bất thường
            </Text>
          </View>

          <View style={styles.settingItem}>
            <View style={styles.switchRow}>
              <Text style={styles.settingLabel}>Rung cảnh báo</Text>
              <Switch
                value={settings.vibrationEnabled}
                onValueChange={(value) => setSettings({ ...settings, vibrationEnabled: value })}
                trackColor={{ false: theme.colors.border, true: theme.colors.primary }}
                thumbColor={settings.vibrationEnabled ? theme.colors.primary : theme.colors.textSecondary}
              />
            </View>
            <Text style={styles.settingHelper}>
              Rung thiết bị khi phát hiện hành vi bất thường
            </Text>
          </View>

          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>
              Thời gian chống lặp ({settings.alertCooldown}s)
            </Text>
            <Slider
              style={styles.slider}
              minimumValue={1}
              maximumValue={30}
              step={1}
              value={settings.alertCooldown}
              onValueChange={(value) => setSettings({ ...settings, alertCooldown: value })}
              minimumTrackTintColor={theme.colors.primary}
              maximumTrackTintColor={theme.colors.border}
            />
            <Text style={styles.settingHelper}>
              Khoảng thời gian giữa các cảnh báo liên tiếp
            </Text>
          </View>
        </View>

        {/* App Info */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Thông tin ứng dụng</Text>
          
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>Phiên bản:</Text>
            <Text style={styles.infoValue}>0.1.0 (Demo)</Text>
          </View>
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>Platform:</Text>
            <Text style={styles.infoValue}>React Native</Text>
          </View>
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>Model:</Text>
            <Text style={styles.infoValue}>YOLOv8-Pose + LSTM</Text>
          </View>
        </View>

        {/* Actions */}
        <View style={styles.actionsContainer}>
          <TouchableOpacity
            style={[styles.actionButton, styles.saveButton]}
            onPress={handleSaveSettings}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color={theme.colors.surface} />
            ) : (
              <Text style={styles.actionButtonText}>Lưu cài đặt</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.logoutButton]}
            onPress={handleLogout}
          >
            <Text style={styles.logoutButtonText}>Đăng xuất</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  content: {
    padding: theme.spacing.lg,
  },
  section: {
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: theme.spacing.lg,
    marginBottom: theme.spacing.lg,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  sectionTitle: {
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.text,
    marginBottom: theme.spacing.md,
  },
  settingItem: {
    marginBottom: theme.spacing.lg,
  },
  settingLabel: {
    fontSize: theme.typography.fontSize.md,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
  },
  settingInput: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: 8,
    padding: theme.spacing.md,
    fontSize: theme.typography.fontSize.md,
    backgroundColor: theme.colors.background,
  },
  settingHelper: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.textSecondary,
    marginTop: theme.spacing.xs,
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  slider: {
    width: '100%',
    height: 40,
  },
  qualityOptions: {
    flexDirection: 'row',
    marginTop: theme.spacing.sm,
  },
  qualityButton: {
    flex: 1,
    padding: theme.spacing.sm,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: theme.colors.border,
    alignItems: 'center',
    marginHorizontal: theme.spacing.xs,
  },
  qualityButtonActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  qualityButtonText: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text,
  },
  qualityButtonTextActive: {
    color: theme.colors.surface,
    fontWeight: theme.typography.fontWeight.semibold,
  },
  testButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: theme.colors.primary,
    borderRadius: 8,
    padding: theme.spacing.md,
    marginTop: theme.spacing.md,
  },
  testButtonText: {
    color: theme.colors.surface,
    fontSize: theme.typography.fontSize.md,
    fontWeight: theme.typography.fontWeight.semibold,
    marginLeft: theme.spacing.sm,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  infoItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: theme.spacing.sm,
  },
  infoLabel: {
    fontSize: theme.typography.fontSize.md,
    color: theme.colors.textSecondary,
  },
  infoValue: {
    fontSize: theme.typography.fontSize.md,
    color: theme.colors.text,
    fontWeight: theme.typography.fontWeight.medium,
  },
  actionsContainer: {
    marginTop: theme.spacing.lg,
  },
  actionButton: {
    borderRadius: 8,
    padding: theme.spacing.md,
    alignItems: 'center',
    marginBottom: theme.spacing.md,
    minHeight: theme.spacing.touchTarget,
    justifyContent: 'center',
  },
  saveButton: {
    backgroundColor: theme.colors.primary,
  },
  actionButtonText: {
    color: theme.colors.surface,
    fontSize: theme.typography.fontSize.md,
    fontWeight: theme.typography.fontWeight.semibold,
  },
  logoutButton: {
    backgroundColor: theme.colors.error,
  },
  logoutButtonText: {
    color: theme.colors.surface,
    fontSize: theme.typography.fontSize.md,
    fontWeight: theme.typography.fontWeight.semibold,
  },
});

export default SettingsScreen;
