import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { theme } from '../theme';
import { api } from '../services/api';
import { useNavigation } from '@react-navigation/native';
import { ServerStatus } from '../types';

const HomeScreen: React.FC = () => {
  const navigation = useNavigation();
  const [serverStatus, setServerStatus] = useState<ServerStatus | null>(null);
  const [recentAlerts, setRecentAlerts] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [status, detections] = await Promise.all([
        api.getServerStatus(),
        api.getDetections({ label: 'abnormal' }),
      ]);
      
      setServerStatus(status);
      setRecentAlerts(detections.length);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = () => {
    if (!serverStatus) return theme.colors.connecting;
    switch (serverStatus.status) {
      case 'ok':
        return theme.colors.normal;
      case 'error':
        return theme.colors.error;
      default:
        return theme.colors.connecting;
    }
  };

  const getStatusText = () => {
    if (!serverStatus) return 'Đang kết nối...';
    switch (serverStatus.status) {
      case 'ok':
        return 'Server đang hoạt động';
      case 'error':
        return 'Lỗi server';
      default:
        return 'Đang kết nối...';
    }
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
        <Text style={styles.loadingText}>Đang tải...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Server Status Card */}
        <View style={[styles.card, styles.statusCard]}>
          <View style={styles.statusHeader}>
            <Text style={styles.cardTitle}>Trạng thái Server</Text>
            <View style={[styles.statusIndicator, { backgroundColor: getStatusColor() }]} />
          </View>
          <Text style={styles.statusText}>{getStatusText()}</Text>
          {serverStatus && serverStatus.modelLoaded && (
            <View style={styles.modelInfo}>
              <Text style={styles.modelText}>
                Model: {serverStatus.modelName} (v{serverStatus.modelVersion})
              </Text>
            </View>
          )}
        </View>

        {/* Quick Stats */}
        <View style={styles.statsRow}>
          <View style={[styles.statCard, { backgroundColor: theme.colors.error + '20' }]}>
            <Text style={styles.statNumber}>{recentAlerts}</Text>
            <Text style={styles.statLabel}>Cảnh báo gần đây</Text>
          </View>
          <View style={[styles.statCard, { backgroundColor: theme.colors.normal + '20' }]}>
            <Text style={styles.statNumber}>●</Text>
            <Text style={styles.statLabel}>Hoạt động</Text>
          </View>
        </View>

        {/* Main Actions */}
        <View style={styles.actionsContainer}>
          <TouchableOpacity
            style={[styles.actionButton, styles.primaryButton]}
            onPress={() => navigation.navigate('Monitor' as never)}
          >
            <Text style={styles.actionButtonIcon}>📹</Text>
            <Text style={styles.actionButtonText}>Bắt đầu giám sát</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.secondaryButton]}
            onPress={() => navigation.navigate('History' as never)}
          >
            <Text style={styles.actionButtonIcon}>📋</Text>
            <Text style={styles.actionButtonText}>Xem lịch sử</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.secondaryButton]}
            onPress={() => navigation.navigate('Statistics' as never)}
          >
            <Text style={styles.actionButtonIcon}>📊</Text>
            <Text style={styles.actionButtonText}>Thống kê</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.secondaryButton]}
            onPress={() => navigation.navigate('Settings' as never)}
          >
            <Text style={styles.actionButtonIcon}>⚙️</Text>
            <Text style={styles.actionButtonText}>Cài đặt</Text>
          </TouchableOpacity>
        </View>

        {/* Quick Info */}
        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>Thông tin nhanh</Text>
          <Text style={styles.infoText}>
            👁️ Hệ thống giám sát hành vi bằng AI
          </Text>
          <Text style={styles.infoText}>
            🤖 Sử dụng YOLOv8-Pose + LSTM
          </Text>
          <Text style={styles.infoText}>
            📱 Real-time detection & alerting
          </Text>
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
  },
  loadingText: {
    marginTop: theme.spacing.md,
    fontSize: theme.typography.fontSize.md,
    color: theme.colors.textSecondary,
  },
  card: {
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
  statusCard: {
    borderLeftWidth: 4,
    borderLeftColor: theme.colors.primary,
  },
  statusHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
  },
  cardTitle: {
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.text,
  },
  statusIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  statusText: {
    fontSize: theme.typography.fontSize.md,
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
  },
  modelInfo: {
    backgroundColor: theme.colors.background,
    borderRadius: 8,
    padding: theme.spacing.sm,
  },
  modelText: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.textSecondary,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: theme.spacing.lg,
  },
  statCard: {
    flex: 1,
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: theme.spacing.lg,
    alignItems: 'center',
    marginHorizontal: theme.spacing.xs,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  statNumber: {
    fontSize: theme.typography.fontSize.xxxl,
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text,
    marginBottom: theme.spacing.xs,
  },
  statLabel: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
  actionsContainer: {
    marginBottom: theme.spacing.lg,
  },
  actionButton: {
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: theme.spacing.lg,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: theme.spacing.md,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  primaryButton: {
    backgroundColor: theme.colors.primary,
  },
  secondaryButton: {
    backgroundColor: theme.colors.surface,
  },
  actionButtonIcon: {
    fontSize: 24,
    marginRight: theme.spacing.md,
  },
  actionButtonText: {
    fontSize: theme.typography.fontSize.md,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.text,
  },
  infoCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: theme.spacing.lg,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  infoTitle: {
    fontSize: theme.typography.fontSize.md,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
  },
  infoText: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.textSecondary,
    marginBottom: theme.spacing.xs,
  },
});

export default HomeScreen;
