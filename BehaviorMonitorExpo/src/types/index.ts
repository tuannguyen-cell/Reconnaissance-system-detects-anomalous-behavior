export type DetectionResult = 'normal' | 'abnormal';

export interface Detection {
  id: string;
  label: DetectionResult;
  confidence: number;
  timestamp: string;
  source: string;
  eventId: string;
}

export interface ServerStatus {
  status: 'ok' | 'error' | 'connecting';
  modelLoaded: boolean;
  modelName: string;
  modelVersion: string;
}

export interface AppSettings {
  serverUrl: string;
  threshold: number;
  soundEnabled: boolean;
  vibrationEnabled: boolean;
  alertCooldown: number; // in seconds
  imageQuality: 'low' | 'medium' | 'high';
}

export interface MonitoringState {
  isActive: boolean;
  isPaused: boolean;
  currentResult: DetectionResult | null;
  currentConfidence: number | null;
  lastDetectionTime: string | null;
}
