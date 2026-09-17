import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { theme } from '../theme';
import { mockApi } from '../services/mockApi';
import { useNavigation } from '@react-navigation/native';
import { Detection, DetectionResult } from '../types';

const HistoryScreen: React.FC = () => {
  const navigation = useNavigation();
  const [detections, setDetections] = useState<Detection[]>([]);
  const [filteredDetections, setFilteredDetections] = useState<Detection[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [filter, setFilter] = useState<'all' | 'normal' | 'abnormal'>('all');

  useEffect(() => {
    loadDetections();
  }, []);

  useEffect(() => {
    applyFilter();
  }, [filter, detections]);

  const loadDetections = async () => {
    try {
      const data = await mockApi.getDetections();
      setDetections(data);
    } catch (error) {
      console.error('Error loading detections:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const applyFilter = () => {
    if (filter === 'all') {
      setFilteredDetections(detections);
    } else {
      setFilteredDetections(detections.filter(d => d.label === filter));
    }
  };

  const onRefresh = async () => {
    setIsRefreshing(true);
    await loadDetections();
    setIsRefreshing(false);
  };

  const renderDetectionItem = ({ item }: { item: Detection }) => {
    const isAbnormal = item.label === 'abnormal';
    const statusColor = isAbnormal ? theme.colors.abnormal : theme.colors.normal;
    const statusText = isAbnormal ? 'Bất thường' : 'Bình thường';

    return (
      <TouchableOpacity
        style={styles.detectionItem}
        onPress={() => (navigation as any).navigate('DetectionDetail', { detection: item })}
      >
        <View style={styles.detectionHeader}>
          <View style={[styles.statusBadge, { backgroundColor: statusColor }]}>
            <Text style={styles.statusBadgeText}>{statusText}</Text>
          </View>
          <Text style={styles.timestamp}>
            {new Date(item.timestamp).toLocaleString('vi-VN')}
          </Text>
        </View>

        <View style={styles.detectionDetails}>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Confidence:</Text>
            <Text style={styles.detailValue}>
              {(item.confidence * 100).toFixed(1)}%
            </Text>
          </View>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Nguồn:</Text>
            <Text style={styles.detailValue}>{item.source}</Text>
          </View>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Event ID:</Text>
            <Text style={styles.detailValue}>{item.eventId}</Text>
          </View>
        </View>

        <View style={styles.detectionFooter}>
          <Text style={styles.tapText}>Nhấn để xem chi tiết →</Text>
        </View>
      </TouchableOpacity>
    );
  };

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <Text style={styles.emptyIcon}>📋</Text>
      <Text style={styles.emptyTitle}>Chưa có dữ liệu</Text>
      <Text style={styles.emptyText}>
        Bắt đầu giám sát để ghi lại các phát hiện
      </Text>
    </View>
  );

  const renderFilterButton = (filterType: 'all' | 'normal' | 'abnormal', label: string) => (
    <TouchableOpacity
      style={[
        styles.filterButton,
        filter === filterType && styles.activeFilterButton,
      ]}
      onPress={() => setFilter(filterType)}
    >
      <Text
        style={[
          styles.filterButtonText,
          filter === filterType && styles.activeFilterButtonText,
        ]}
      >
        {label}
      </Text>
    </TouchableOpacity>
  );

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
        <Text style={styles.loadingText}>Đang tải lịch sử...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Filter Bar */}
      <View style={styles.filterContainer}>
        {renderFilterButton('all', 'Tất cả')}
        {renderFilterButton('normal', 'Bình thường')}
        {renderFilterButton('abnormal', 'Bất thường')}
      </View>

      {/* Detection List */}
      <FlatList
        data={filteredDetections}
        renderItem={renderDetectionItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={onRefresh}
            colors={[theme.colors.primary]}
          />
        }
        ListEmptyComponent={renderEmptyState}
      />

      {/* Summary Footer */}
      {detections.length > 0 && (
        <View style={styles.summaryFooter}>
          <Text style={styles.summaryText}>
            Tổng: {detections.length} | Bất thường: {detections.filter(d => d.label === 'abnormal').length}
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
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
  filterContainer: {
    flexDirection: 'row',
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  filterButton: {
    flex: 1,
    marginHorizontal: theme.spacing.xs,
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.md,
    borderRadius: 20,
    backgroundColor: theme.colors.background,
    borderWidth: 1,
    borderColor: theme.colors.border,
    alignItems: 'center',
  },
  activeFilterButton: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  filterButtonText: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text,
    fontWeight: theme.typography.fontWeight.medium,
  },
  activeFilterButtonText: {
    color: theme.colors.surface,
  },
  listContent: {
    padding: theme.spacing.md,
    flexGrow: 1,
  },
  detectionItem: {
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: theme.spacing.lg,
    marginBottom: theme.spacing.md,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  detectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.md,
  },
  statusBadge: {
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.xs,
    borderRadius: 12,
  },
  statusBadgeText: {
    color: theme.colors.surface,
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.semibold,
  },
  timestamp: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.textSecondary,
  },
  detectionDetails: {
    marginBottom: theme.spacing.md,
  },
  detailRow: {
    flexDirection: 'row',
    marginBottom: theme.spacing.xs,
  },
  detailLabel: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.textSecondary,
    width: 80,
  },
  detailValue: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text,
    fontWeight: theme.typography.fontWeight.medium,
  },
  detectionFooter: {
    alignItems: 'flex-end',
  },
  tapText: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.primary,
    fontWeight: theme.typography.fontWeight.medium,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing.xxl,
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: theme.spacing.md,
  },
  emptyTitle: {
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
  },
  emptyText: {
    fontSize: theme.typography.fontSize.md,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
  summaryFooter: {
    backgroundColor: theme.colors.surface,
    padding: theme.spacing.md,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
    alignItems: 'center',
  },
  summaryText: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.textSecondary,
  },
});

export default HistoryScreen;
