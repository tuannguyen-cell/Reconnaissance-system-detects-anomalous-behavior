import AsyncStorage from '@react-native-async-storage/async-storage';
import { AppSettings, Detection, ServerStatus } from '../types';

const SERVER_URL_KEY = '@behavior_monitor/server_url';
const TOKEN_KEY = '@behavior_monitor/access_token';
const DEFAULT_SERVER_URL = 'http://localhost:8000';

type DetectionFilter = {
  label?: 'normal' | 'abnormal';
  startDate?: string;
  endDate?: string;
};

type Credentials = {
  username: string;
  password: string;
  email?: string;
};

const normalizeBaseUrl = (serverUrl: string) => {
  const trimmed = serverUrl.trim().replace(/\/+$/, '');
  return trimmed.endsWith('/api/v1') ? trimmed : `${trimmed}/api/v1`;
};

const toDetection = (item: any): Detection => ({
  id: item.id ?? item.event_id,
  label: item.label,
  confidence: item.confidence,
  timestamp: item.timestamp,
  source: item.source,
  eventId: item.event_id,
});

const request = async <T>(path: string, options: RequestInit = {}, serverUrl?: string): Promise<T> => {
  const baseUrl = normalizeBaseUrl(serverUrl || await AsyncStorage.getItem(SERVER_URL_KEY) || DEFAULT_SERVER_URL);
  const token = await AsyncStorage.getItem(TOKEN_KEY);
  const headers = new Headers(options.headers);
  headers.set('Accept', 'application/json');
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${baseUrl}${path}`, { ...options, headers });
  const body = await response.text();
  let data: any = null;
  try {
    data = body ? JSON.parse(body) : null;
  } catch {
    data = body;
  }

  if (!response.ok) {
    const detail = typeof data === 'object' && data?.detail ? data.detail : `HTTP ${response.status}`;
    throw new Error(detail);
  }
  return data as T;
};

const authenticate = async (serverUrl: string, credentials: Credentials) => {
  let login = await request<{ access_token: string }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username: credentials.username, password: credentials.password }),
  }, serverUrl).catch(() => null);

  if (!login) {
    await request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        username: credentials.username,
        email: credentials.email || `${credentials.username}@example.com`,
        password: credentials.password,
      }),
    }, serverUrl);
    login = await request<{ access_token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username: credentials.username, password: credentials.password }),
    }, serverUrl);
  }

  await AsyncStorage.setItem(TOKEN_KEY, login.access_token);
};

export const api = {
  async connectToDetectionStream(onAbnormal: (detection: Detection) => void): Promise<() => void> {
    const serverUrl = await AsyncStorage.getItem(SERVER_URL_KEY);
    if (!serverUrl) return () => undefined;

    const websocketUrl = normalizeBaseUrl(serverUrl)
      .replace(/^http:/, 'ws:')
      .replace(/^https:/, 'wss:')
      .replace(/\/api\/v1$/, '/api/v1/ws/detection');
    let socket: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let closed = false;

    const openSocket = () => {
      socket = new WebSocket(websocketUrl);
      socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === 'detection' && message.data?.label === 'abnormal') {
            onAbnormal(toDetection(message.data));
          }
        } catch {
          // Ignore malformed stream messages.
        }
      };
      socket.onclose = () => {
        if (!closed) reconnectTimer = setTimeout(openSocket, 3000);
      };
    };

    openSocket();

    return () => {
      closed = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      socket?.close();
    };
  },

  async connectToServer(serverUrl: string, credentials?: Credentials): Promise<ServerStatus> {
    const normalizedUrl = serverUrl.trim().replace(/\/+$/, '');
    const status = await request<any>('/health/status', {}, normalizedUrl);
    await AsyncStorage.setItem(SERVER_URL_KEY, normalizedUrl);
    if (credentials) {
      await authenticate(normalizedUrl, credentials);
    }
    return {
      status: status.status === 'ok' ? 'ok' : 'error',
      modelLoaded: status.model_loaded,
      modelName: status.model_name,
      modelVersion: status.model_version,
    };
  },

  async getServerStatus(): Promise<ServerStatus> {
    const status = await request<any>('/health/status');
    return {
      status: status.status === 'ok' ? 'ok' : 'error',
      modelLoaded: status.model_loaded,
      modelName: status.model_name,
      modelVersion: status.model_version,
    };
  },

  async getDetections(filter?: DetectionFilter): Promise<Detection[]> {
    const params = new URLSearchParams();
    if (filter?.label) params.set('label', filter.label);
    if (filter?.startDate) params.set('start_date', filter.startDate);
    if (filter?.endDate) params.set('end_date', filter.endDate);
    const query = params.toString();
    const data = await request<{ detections: any[] }>(`/detection/detections${query ? `?${query}` : ''}`);
    return data.detections.map(toDetection);
  },

  async getStatistics(): Promise<{
    total: number;
    normal: number;
    abnormal: number;
    abnormalRate: number;
    dailyData: Array<{ date: string; normal: number; abnormal: number }>;
  }> {
    const data = await request<any>('/statistics/statistics');
    return {
      total: data.total,
      normal: data.normal,
      abnormal: data.abnormal,
      abnormalRate: data.abnormal_rate,
      dailyData: data.daily_data,
    };
  },

  async detectFromFrame(frameData: string, threshold: number): Promise<Detection> {
    const data = await request<any>('/detection/detect', {
      method: 'POST',
      body: JSON.stringify({ frame_data: frameData, threshold, source: 'mobile-camera' }),
    });
    return toDetection(data);
  },

  async deleteDetection(id: string): Promise<void> {
    await request(`/detection/detections/${encodeURIComponent(id)}`, { method: 'DELETE' });
  },

  async saveSettings(settings: AppSettings): Promise<void> {
    await AsyncStorage.setItem(SERVER_URL_KEY, settings.serverUrl.trim().replace(/\/+$/, ''));
  },

  async logout(): Promise<void> {
    await AsyncStorage.removeItem(TOKEN_KEY);
  },
};

export { DEFAULT_SERVER_URL };
