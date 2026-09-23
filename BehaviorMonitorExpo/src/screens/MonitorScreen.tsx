import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { theme } from '../theme';
import { api } from '../services/api';
import { useNavigation } from '@react-navigation/native';
import { Detection, DetectionResult } from '../types';

const MonitorScreen: React.FC = () => {
  const navigation = useNavigation();
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [currentResult, setCurrentResult] = useState<DetectionResult | null>(null);
  const [currentConfidence, setCurrentConfidence] = useState<number | null>(null);
  const [lastDetectionTime, setLastDetectionTime] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [serverConnected, setServerConnected] = useState(true);
  const [permission, requestPermission] = useCameraPermissions();
  
  const detectionInterval = useRef<ReturnType<typeof setInterval> | null>(null);
  const cameraRef = useRef<CameraView>(null);
  const monitoringRef = useRef(false);
  const pausedRef = useRef(false);

  useEffect(() => {
    return () => {
      if (detectionInterval.current) {
        clearInterval(detectionInterval.current);
      }
    };
  }, []);

  const startMonitoring = async () => {
    if (!permission?.granted) {
      const result = await requestPermission();
      if (!result.granted) {
        Alert.alert('Cần quyền camera', 'Hãy cấp quyền camera để bắt đầu giám sát.');
        return;
      }
    }

    setIsConnecting(true);
    
    // Simulate camera permission check
    setTimeout(() => {
      setIsConnecting(false);
      setIsMonitoring(true);
      setIsPaused(false);
      monitoringRef.current = true;
      pausedRef.current = false;
      startDetectionLoop();
    }, 1500);
  };

  const stopMonitoring = () => {
    setIsMonitoring(false);
    setIsPaused(false);
    monitoringRef.current = false;
    pausedRef.current = false;
    setCurrentResult(null);
    setCurrentConfidence(null);
    
    if (detectionInterval.current) {
      clearInterval(detectionInterval.current);
      detectionInterval.current = null;
    }
  };

  const pauseMonitoring = () => {
    setIsPaused(!isPaused);
    pausedRef.current = !isPaused;
    if (!isPaused && detectionInterval.current) {
      clearInterval(detectionInterval.current);
      detectionInterval.current = null;
    } else if (isPaused) {
      startDetectionLoop();
    }
  };

  const startDetectionLoop = () => {
    if (detectionInterval.current) {
      clearInterval(detectionInterval.current);
    }

    detectionInterval.current = setInterval(async () => {
      if (!monitoringRef.current || pausedRef.current || !cameraRef.current) return;

      try {
        const photo = await cameraRef.current.takePictureAsync({
          base64: true,
          quality: 0.5,
          skipProcessing: true,
          shutterSound: false,
        });
        if (!photo.base64) return;
        const detection = await api.detectFromFrame(photo.base64, 0.5);
        
        setCurrentResult(detection.label);
        setCurrentConfidence(detection.confidence);
        setLastDetectionTime(detection.timestamp);

      } catch (error) {
        console.error('Detection error:', error);
        setServerConnected(false);
      }
    }, 2000); // Detect every 2 seconds
  };

  const getStatusColor = () => {
    if (!isMonitoring) return theme.colors.connecting;
    if (isPaused) return theme.colors.connecting;
    if (!serverConnected) return theme.colors.error;
    
    switch (currentResult) {
      case 'normal':
        return theme.colors.normal;
      case 'abnormal':
        return theme.colors.abnormal;
      default:
        return theme.colors.connecting;
    }
  };

  const getStatusText = () => {
    if (!isMonitoring) return 'ĐANG CHỜ';
    if (isPaused) return 'ĐÃ TẠM DỪNG';
    if (!serverConnected) return 'MẤT KẾT NỐI';
    
    switch (currentResult) {
      case 'normal':
        return 'BÌNH THƯỜNG';
      case 'abnormal':
        return 'BẤT THƯỜNG';
      default:
        return 'ĐANG PHÁT HIỆN...';
    }
  };

  return (
    <View style={styles.container}>
      {/* Simulated Camera View */}
      <View style={styles.cameraContainer}>
        {isConnecting ? (
          <View style={styles.cameraPlaceholder}>
            <ActivityIndicator size="large" color={theme.colors.primary} />
            <Text style={styles.cameraPlaceholderText}>Đang khởi tạo camera...</Text>
          </View>
        ) : isMonitoring ? (
          <View style={styles.cameraActive}>
            <CameraView
              ref={cameraRef}
              style={styles.cameraPreview}
              facing="back"
            />
            <View style={styles.cameraFrame}>
              <Text style={styles.cameraText}>CAMERA FEED</Text>
              <Text style={styles.cameraSubtext}>
                {isPaused ? 'Đã tạm dừng' : 'Đang giám sát'}
              </Text>
            </View>
            
            {/* Detection Overlay */}
            {currentResult && (
              <View style={[
                styles.detectionOverlay,
                { backgroundColor: currentResult === 'abnormal' ? 'rgba(244, 67, 54, 0.3)' : 'rgba(76, 175, 80, 0.3)' }
              ]}>
                <View style={[
                  styles.detectionBadge,
                  { backgroundColor: getStatusColor() }
                ]}>
                  <Text style={styles.detectionBadgeText}>
                    {getStatusText()}
                  </Text>
                </View>
                
                {currentConfidence && (
                  <View style={styles.confidenceContainer}>
                    <Text style={styles.confidenceText}>
                      Confidence: {(currentConfidence * 100).toFixed(1)}%
                    </Text>
                  </View>
                )}
              </View>
            )}
          </View>
        ) : (
          <View style={styles.cameraPlaceholder}>
            <Text style={styles.cameraPlaceholderIcon}>📷</Text>
            <Text style={styles.cameraPlaceholderText}>
              Nhấn "Bắt đầu giám sát" để kích hoạt camera
            </Text>
          </View>
        )}
      </View>

      {/* Status Bar */}
      <View style={[styles.statusBar, { backgroundColor: getStatusColor() }]}>
        <Text style={styles.statusText}>{getStatusText()}</Text>
        {currentConfidence && isMonitoring && !isPaused && (
          <Text style={styles.confidenceBadge}>
            {(currentConfidence * 100).toFixed(1)}%
          </Text>
        )}
      </View>

      {/* Control Buttons */}
      <View style={styles.controlsContainer}>
        {!isMonitoring ? (
          <TouchableOpacity
            style={[styles.controlButton, styles.startButton]}
            onPress={startMonitoring}
            disabled={isConnecting}
          >
            {isConnecting ? (
              <ActivityIndicator color={theme.colors.surface} />
            ) : (
              <>
                <Text style={styles.controlButtonIcon}>▶️</Text>
                <Text style={styles.controlButtonText}>Bắt đầu giám sát</Text>
              </>
            )}
          </TouchableOpacity>
        ) : (
          <>
            <TouchableOpacity
              style={[styles.controlButton, styles.pauseButton]}
              onPress={pauseMonitoring}
            >
              <Text style={styles.controlButtonIcon}>
                {isPaused ? '▶️' : '⏸️'}
              </Text>
              <Text style={styles.controlButtonText}>
                {isPaused ? 'Tiếp tục' : 'Tạm dừng'}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.controlButton, styles.stopButton]}
              onPress={stopMonitoring}
            >
              <Text style={styles.controlButtonIcon}>⏹️</Text>
              <Text style={styles.controlButtonText}>Kết thúc</Text>
            </TouchableOpacity>
          </>
        )}
      </View>

      {/* Server Connection Status */}
      <View style={styles.serverStatusContainer}>
        <View style={[
          styles.serverStatusIndicator,
          { backgroundColor: serverConnected ? theme.colors.normal : theme.colors.error }
        ]} />
        <Text style={styles.serverStatusText}>
          {serverConnected ? 'Đã kết nối server' : 'Mất kết nối server'}
        </Text>
      </View>

      {/* Last Detection Info */}
      {lastDetectionTime && (
        <View style={styles.lastDetectionContainer}>
          <Text style={styles.lastDetectionText}>
            Phát hiện gần nhất: {new Date(lastDetectionTime).toLocaleString('vi-VN')}
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
  cameraContainer: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center',
  },
  cameraPlaceholder: {
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing.xl,
  },
  cameraPlaceholderIcon: {
    fontSize: 64,
    marginBottom: theme.spacing.md,
  },
  cameraPlaceholderText: {
    color: theme.colors.surface,
    fontSize: theme.typography.fontSize.md,
    textAlign: 'center',
  },
  cameraActive: {
    flex: 1,
    width: '100%',
    justifyContent: 'center',
    alignItems: 'center',
  },
  cameraPreview: {
    ...StyleSheet.absoluteFill,
  },
  cameraFrame: {
    borderWidth: 2,
    borderColor: theme.colors.surface,
    borderRadius: 8,
    padding: theme.spacing.xl,
    alignItems: 'center',
  },
  cameraText: {
    color: theme.colors.surface,
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.bold,
    marginBottom: theme.spacing.sm,
  },
  cameraSubtext: {
    color: theme.colors.surface,
    fontSize: theme.typography.fontSize.sm,
  },
  detectionOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  detectionBadge: {
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.md,
    borderRadius: 8,
    marginBottom: theme.spacing.md,
  },
  detectionBadgeText: {
    color: theme.colors.surface,
    fontSize: theme.typography.fontSize.xl,
    fontWeight: theme.typography.fontWeight.bold,
  },
  confidenceContainer: {
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
    borderRadius: 4,
  },
  confidenceText: {
    color: theme.colors.surface,
    fontSize: theme.typography.fontSize.md,
    fontWeight: theme.typography.fontWeight.semibold,
  },
  statusBar: {
    padding: theme.spacing.md,
    alignItems: 'center',
  },
  statusText: {
    color: theme.colors.surface,
    fontSize: theme.typography.fontSize.lg,
    fontWeight: theme.typography.fontWeight.bold,
  },
  confidenceBadge: {
    color: theme.colors.surface,
    fontSize: theme.typography.fontSize.md,
    fontWeight: theme.typography.fontWeight.semibold,
    marginTop: theme.spacing.xs,
  },
  controlsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: theme.spacing.lg,
    backgroundColor: theme.colors.surface,
  },
  controlButton: {
    flex: 1,
    marginHorizontal: theme.spacing.sm,
    padding: theme.spacing.md,
    borderRadius: 8,
    alignItems: 'center',
    minHeight: theme.spacing.touchTarget,
    justifyContent: 'center',
  },
  startButton: {
    backgroundColor: theme.colors.primary,
  },
  pauseButton: {
    backgroundColor: theme.colors.warning,
  },
  stopButton: {
    backgroundColor: theme.colors.error,
  },
  controlButtonIcon: {
    fontSize: 24,
    marginBottom: theme.spacing.xs,
  },
  controlButtonText: {
    color: theme.colors.surface,
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.semibold,
  },
  serverStatusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },
  serverStatusIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: theme.spacing.sm,
  },
  serverStatusText: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.textSecondary,
  },
  lastDetectionContainer: {
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },
  lastDetectionText: {
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
});

export default MonitorScreen;
