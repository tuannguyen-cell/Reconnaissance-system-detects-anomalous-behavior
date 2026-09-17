import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { theme } from '../theme';
import { useNavigation, useRoute } from '@react-navigation/native';
import { Detection } from '../types';

const DetectionDetailScreen: React.FC = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const { detection } = route.params as { detection: Detection };

  const isAbnormal = detection.label === 'abnormal';
  const statusColor = isAbnormal ? theme.colors.abnormal : theme.colors.normal;
  const statusText = isAbnormal ? 'Bất thường' : 'Bình thường';

  const handleDelete = async () => {
    // In a real app, this would call the API to delete
    console.log('Delete detection:', detection.id);
    navigation.goBack();
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Status Card */}
        <View style={[styles.statusCard, { borderLeftColor: statusColor }]}>
          <View style={[styles.statusBadge, { backgroundColor: statusColor }]}>
            <Text style={styles.statusBadgeText}>{statusText}</Text>
          </View>
          <Text style={styles.confidenceText}>
            Confidence: {(detection.confidence * 100).toFixed(1)}%
          </Text>
        </View>

        {/* Detection Details */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Thông tin phát hiện</Text>
          
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Event ID:</Text>
            <Text style={styles.detailValue}>{detection.eventId}</Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Thời gian:</Text>
            <Text style={styles.detailValue}>
              {new Date(detection.timestamp).toLocaleString('vi-VN')}
            </Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Nguồn:</Text>
            <Text style={styles.detailValue}>{detection.source}</Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Confidence:</Text>
            <Text style={styles.detailValue}>
              {(detection.confidence * 100).toFixed(1)}%
            </Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Kết quả:</Text>
            <Text style={[styles.detailValue, { color: statusColor }]}>
              {statusText}
            </Text>
          </View>
        </View>

        {/* Technical Details */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Chi tiết kỹ thuật</Text>
          
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Detection ID:</Text>
            <Text style={styles.detailValue}>{detection.id}</Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Timestamp ISO:</Text>
            <Text style={[styles.detailValue, styles.detailValueSmall]}>
              {detection.timestamp}
            </Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Raw Confidence:</Text>
            <Text style={styles.detailValue}>
              {detection.confidence.toFixed(4)}
            </Text>
          </View>
        </View>

        {/* Placeholder for image/video */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Hình ảnh</Text>
          <View style={styles.imagePlaceholder}>
            <Text style={styles.imagePlaceholderText}>
              📷 Ảnh snapshot sẽ hiển thị ở đây
            </Text>
            <Text style={styles.imagePlaceholderSubtext}>
              (Backend cần lưu trữ ảnh để hiển thị)
            </Text>
          </View>
        </View>

        {/* Actions */}
        <View style={styles.actionsContainer}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.actionButtonText}>Quay lại</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.deleteButton]}
            onPress={handleDelete}
          >
            <Text style={styles.deleteButtonText}>Xóa bản ghi</Text>
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
  statusCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: theme.spacing.xl,
    marginBottom: theme.spacing.lg,
    borderLeftWidth: 4,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  statusBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.sm,
    borderRadius: 8,
    marginBottom: theme.spacing.md,
  },
  statusBadgeText: {
    color: theme.colors.surface,
    fontSize: theme.typography.fontSize.md,
    fontWeight: theme.typography.fontWeight.bold,
  },
  confidenceText: {
    fontSize: theme.typography.fontSize.xl,
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text,
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
  cardTitle: {
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.text,
    marginBottom: theme.spacing.md,
  },
  detailRow: {
    flexDirection: 'row',
    marginBottom: theme.spacing.md,
    alignItems: 'flex-start',
  },
  detailLabel: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.textSecondary,
    width: 120,
    flexShrink: 0,
  },
  detailValue: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text,
    fontWeight: theme.typography.fontWeight.medium,
    flex: 1,
  },
  detailValueSmall: {
    fontSize: theme.typography.fontSize.xs,
  },
  imagePlaceholder: {
    backgroundColor: theme.colors.background,
    borderRadius: 8,
    padding: theme.spacing.xxl,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 200,
  },
  imagePlaceholderText: {
    fontSize: theme.typography.fontSize.md,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: theme.spacing.sm,
  },
  imagePlaceholderSubtext: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
  actionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: theme.spacing.lg,
  },
  actionButton: {
    flex: 1,
    backgroundColor: theme.colors.primary,
    borderRadius: 8,
    padding: theme.spacing.md,
    alignItems: 'center',
    marginHorizontal: theme.spacing.xs,
    minHeight: theme.spacing.touchTarget,
    justifyContent: 'center',
  },
  actionButtonText: {
    color: theme.colors.surface,
    fontSize: theme.typography.fontSize.md,
    fontWeight: theme.typography.fontWeight.semibold,
  },
  deleteButton: {
    backgroundColor: theme.colors.error,
  },
  deleteButtonText: {
    color: theme.colors.surface,
    fontSize: theme.typography.fontSize.md,
    fontWeight: theme.typography.fontWeight.semibold,
  },
});

export default DetectionDetailScreen;
