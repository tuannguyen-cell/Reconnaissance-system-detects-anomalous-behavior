import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { theme } from '../theme';
import { mockApi } from '../services/mockApi';
import { useNavigation } from '@react-navigation/native';

const ConnectScreen: React.FC = () => {
  const navigation = useNavigation();
  const [serverUrl, setServerUrl] = useState(Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://localhost:8000');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleConnect = async () => {
    if (!serverUrl.trim()) {
      setError('Vui lòng nhập địa chỉ server');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const status = await mockApi.connectToServer(serverUrl);
      
      if (status.status === 'ok') {
        // Navigate to Home screen
        navigation.navigate('Home' as never);
      } else {
        setError('Không thể kết nối đến server');
      }
    } catch (err) {
      setError('Lỗi kết nối. Vui lòng kiểm tra lại địa chỉ server.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.content}>
          <View style={styles.logoContainer}>
            <Text style={styles.logoText}>👁️</Text>
            <Text style={styles.appName}>Behavior Monitor</Text>
            <Text style={styles.appDescription}>
              Hệ thống giám sát hành vi thông minh
            </Text>
          </View>

          <View style={styles.formContainer}>
            <Text style={styles.label}>Địa chỉ Server</Text>
            <TextInput
              style={styles.input}
              placeholder="http://localhost:8000"
              value={serverUrl}
              onChangeText={setServerUrl}
              autoCapitalize="none"
              keyboardType="url"
              editable={!isLoading}
            />

            {error && (
              <View style={styles.errorContainer}>
                <Text style={styles.errorText}>{error}</Text>
              </View>
            )}

            <TouchableOpacity
              style={[styles.connectButton, isLoading && styles.disabledButton]}
              onPress={handleConnect}
              disabled={isLoading}
            >
              {isLoading ? (
                <ActivityIndicator color={theme.colors.surface} />
              ) : (
                <Text style={styles.connectButtonText}>Kết nối</Text>
              )}
            </TouchableOpacity>

            <View style={styles.infoContainer}>
              <Text style={styles.infoText}>
                💡 Đây là phiên bản demo với dữ liệu giả lập
              </Text>
              <Text style={styles.infoText}>
                📱 Hỗ trợ cả Android và iOS
              </Text>
            </View>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  scrollContent: {
    flexGrow: 1,
  },
  content: {
    flex: 1,
    padding: theme.spacing.xl,
    justifyContent: 'center',
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: theme.spacing.xxl,
  },
  logoText: {
    fontSize: 64,
    marginBottom: theme.spacing.md,
  },
  appName: {
    fontSize: theme.typography.fontSize.xxl,
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
  },
  appDescription: {
    fontSize: theme.typography.fontSize.md,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
  formContainer: {
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: theme.spacing.xl,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  label: {
    fontSize: theme.typography.fontSize.md,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
  },
  input: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: 8,
    padding: theme.spacing.md,
    fontSize: theme.typography.fontSize.md,
    marginBottom: theme.spacing.md,
    backgroundColor: theme.colors.background,
  },
  errorContainer: {
    backgroundColor: theme.colors.error + '20',
    borderRadius: 8,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.md,
  },
  errorText: {
    color: theme.colors.error,
    fontSize: theme.typography.fontSize.sm,
  },
  connectButton: {
    backgroundColor: theme.colors.primary,
    borderRadius: 8,
    padding: theme.spacing.md,
    alignItems: 'center',
    minHeight: theme.spacing.touchTarget,
    justifyContent: 'center',
  },
  disabledButton: {
    opacity: 0.6,
  },
  connectButtonText: {
    color: theme.colors.surface,
    fontSize: theme.typography.fontSize.md,
    fontWeight: theme.typography.fontWeight.semibold,
  },
  infoContainer: {
    marginTop: theme.spacing.xl,
    alignItems: 'center',
  },
  infoText: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: theme.spacing.sm,
  },
});

export default ConnectScreen;
