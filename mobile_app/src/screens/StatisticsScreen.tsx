import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { theme } from '../theme';
import { mockApi } from '../services/mockApi';

interface StatisticsData {
  total: number;
  normal: number;
  abnormal: number;
  abnormalRate: number;
  dailyData: Array<{ date: string; normal: number; abnormal: number }>;
}

const StatisticsScreen: React.FC = () => {
  const [statistics, setStatistics] = useState<StatisticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    try {
      const data = await mockApi.getStatistics();
      setStatistics(data);
    } catch (error) {
      console.error('Error loading statistics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderStatCard = (title: string, value: string | number, color: string) => (
    <View style={[styles.statCard, { backgroundColor: color + '20' }]}>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statTitle}>{title}</Text>
    </View>
  );

  const renderDailyBar = (item: { date: string; normal: number; abnormal: number }) => {
    const maxCount = Math.max(item.normal, item.abnormal, 1);
    const normalHeight = (item.normal / maxCount) * 100;
    const abnormalHeight = (item.abnormal / maxCount) * 100;
    
    const dateStr = new Date(item.date).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });

    return (
      <View key={item.date} style={styles.barContainer}>
        <View style={styles.barGroup}>
          <View style={[styles.bar, styles.normalBar, { height: `${normalHeight}%` }]} />
          <View style={[styles.bar, styles.abnormalBar, { height: `${abnormalHeight}%` }]} />
        </View>
        <Text style={styles.barLabel}>{dateStr}</Text>
      </View>
    );
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
        <Text style={styles.loadingText}>Đang tải thống kê...</Text>
      </View>
    );
  }

  if (!statistics || statistics.total === 0) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyIcon}>📊</Text>
        <Text style={styles.emptyTitle}>Chưa có dữ liệu thống kê</Text>
        <Text style={styles.emptyText}>
          Bắt đầu giám sát để thu thập dữ liệu
        </Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Overview Cards */}
        <View style={styles.statsRow}>
          {renderStatCard('Tổng số', statistics.total, theme.colors.primary)}
          {renderStatCard('Bình thường', statistics.normal, theme.colors.normal)}
          {renderStatCard('Bất thường', statistics.abnormal, theme.colors.abnormal)}
        </View>

        {/* Abnormal Rate Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Tỷ lệ bất thường</Text>
          <View style={styles.rateContainer}>
            <Text style={styles.rateValue}>
              {statistics.abnormalRate.toFixed(1)}%
            </Text>
            <View style={styles.rateBar}>
              <View 
                style={[
                  styles.rateFill, 
                  { width: `${statistics.abnormalRate}%` }
                ]} 
              />
            </View>
          </View>
        </View>

        {/* Daily Chart */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Biểu đồ theo ngày (7 ngày gần nhất)</Text>
          
          <View style={styles.chartLegend}>
            <View style={styles.legendItem}>
              <View style={[styles.legendDot, { backgroundColor: theme.colors.normal }]} />
              <Text style={styles.legendText}>Bình thường</Text>
            </View>
            <View style={styles.legendItem}>
              <View style={[styles.legendDot, { backgroundColor: theme.colors.abnormal }]} />
              <Text style={styles.legendText}>Bất thường</Text>
            </View>
          </View>

          <View style={styles.chartContainer}>
            {statistics.dailyData.map(renderDailyBar)}
          </View>
        </View>

        {/* Summary */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Tóm tắt</Text>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Tổng số phát hiện:</Text>
            <Text style={styles.summaryValue}>{statistics.total}</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Số bình thường:</Text>
            <Text style={styles.summaryValue}>{statistics.normal}</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Số bất thường:</Text>
            <Text style={styles.summaryValue}>{statistics.abnormal}</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Tỷ lệ bất thường:</Text>
            <Text style={styles.summaryValue}>{statistics.abnormalRate.toFixed(1)}%</Text>
          </View>
        </View>

        {/* Info */}
        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>ℹ️ Thông tin</Text>
          <Text style={styles.infoText}>
            Dữ liệu được cập nhật theo thời gian thực
          </Text>
          <Text style={styles.infoText}>
            Thống kê dựa trên tất cả các phát hiện đã lưu
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
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing.xxl,
    backgroundColor: theme.colors.background,
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
  statValue: {
    fontSize: theme.typography.fontSize.xxxl,
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text,
    marginBottom: theme.spacing.xs,
  },
  statTitle: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.textSecondary,
    textAlign: 'center',
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
  rateContainer: {
    alignItems: 'center',
  },
  rateValue: {
    fontSize: theme.typography.fontSize.xxxl,
    fontWeight: theme.typography.fontWeight.bold,
    color: theme.colors.text,
    marginBottom: theme.spacing.md,
  },
  rateBar: {
    width: '100%',
    height: 12,
    backgroundColor: theme.colors.background,
    borderRadius: 6,
    overflow: 'hidden',
  },
  rateFill: {
    height: '100%',
    backgroundColor: theme.colors.abnormal,
    borderRadius: 6,
  },
  chartLegend: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: theme.spacing.lg,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: theme.spacing.md,
  },
  legendDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: theme.spacing.sm,
  },
  legendText: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.textSecondary,
  },
  chartContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'flex-end',
    height: 150,
    paddingTop: theme.spacing.md,
  },
  barContainer: {
    alignItems: 'center',
    flex: 1,
  },
  barGroup: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    height: 100,
    width: 30,
    justifyContent: 'center',
  },
  bar: {
    width: 12,
    borderRadius: 4,
    marginHorizontal: 2,
  },
  normalBar: {
    backgroundColor: theme.colors.normal,
  },
  abnormalBar: {
    backgroundColor: theme.colors.abnormal,
  },
  barLabel: {
    fontSize: theme.typography.fontSize.xs,
    color: theme.colors.textSecondary,
    marginTop: theme.spacing.sm,
    textAlign: 'center',
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: theme.spacing.sm,
  },
  summaryLabel: {
    fontSize: theme.typography.fontSize.md,
    color: theme.colors.textSecondary,
  },
  summaryValue: {
    fontSize: theme.typography.fontSize.md,
    color: theme.colors.text,
    fontWeight: theme.typography.fontWeight.medium,
  },
  infoCard: {
    backgroundColor: theme.colors.primary + '10',
    borderRadius: 12,
    padding: theme.spacing.lg,
    borderLeftWidth: 4,
    borderLeftColor: theme.colors.primary,
  },
  infoTitle: {
    fontSize: theme.typography.fontSize.md,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.primary,
    marginBottom: theme.spacing.sm,
  },
  infoText: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.textSecondary,
    marginBottom: theme.spacing.xs,
  },
});

export default StatisticsScreen;
