import { Detection, ServerStatus, AppSettings } from '../types';

// Mock data storage
let mockDetections: Detection[] = [];
let mockServerStatus: ServerStatus = {
  status: 'ok',
  modelLoaded: true,
  modelName: 'lstm_best.pt',
  modelVersion: '1.0.0',
};

// Generate mock detection
const generateMockDetection = (): Detection => {
  const isAbnormal = Math.random() > 0.7; // 30% chance of abnormal
  const now = new Date();
  
  return {
    id: `detection_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    label: isAbnormal ? 'abnormal' : 'normal',
    confidence: isAbnormal ? 0.7 + Math.random() * 0.3 : 0.5 + Math.random() * 0.4,
    timestamp: now.toISOString(),
    source: 'camera-01',
    eventId: `evt_${Date.now()}`,
  };
};

// Initialize with some historical data
const initializeMockData = () => {
  const now = new Date();
  for (let i = 0; i < 20; i++) {
    const timestamp = new Date(now.getTime() - i * 3600000); // Each hour
    const isAbnormal = i % 4 === 0; // Every 4th detection is abnormal
    
    mockDetections.push({
      id: `detection_${i}`,
      label: isAbnormal ? 'abnormal' : 'normal',
      confidence: isAbnormal ? 0.75 + Math.random() * 0.2 : 0.6 + Math.random() * 0.3,
      timestamp: timestamp.toISOString(),
      source: 'camera-01',
      eventId: `evt_${i}`,
    });
  }
  
  // Sort by timestamp descending
  mockDetections.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
};

initializeMockData();

// Mock API service
export const mockApi = {
  // Connect to server
  async connectToServer(serverUrl: string): Promise<ServerStatus> {
    return new Promise((resolve) => {
      setTimeout(() => {
        mockServerStatus = {
          ...mockServerStatus,
          status: 'ok',
        };
        resolve(mockServerStatus);
      }, 1000);
    });
  },

  // Get server status
  async getServerStatus(): Promise<ServerStatus> {
    return new Promise((resolve) => {
      setTimeout(() => resolve(mockServerStatus), 500);
    });
  },

  // Get detections history
  async getDetections(filter?: {
    label?: 'normal' | 'abnormal';
    startDate?: string;
    endDate?: string;
  }): Promise<Detection[]> {
    return new Promise((resolve) => {
      setTimeout(() => {
        let filtered = [...mockDetections];
        
        if (filter?.label) {
          filtered = filtered.filter(d => d.label === filter.label);
        }
        
        if (filter?.startDate) {
          const startDate = filter.startDate;
          filtered = filtered.filter(d => new Date(d.timestamp) >= new Date(startDate));
        }
        
        if (filter?.endDate) {
          const endDate = filter.endDate;
          filtered = filtered.filter(d => new Date(d.timestamp) <= new Date(endDate));
        }
        
        resolve(filtered);
      }, 500);
    });
  },

  // Get statistics
  async getStatistics(): Promise<{
    total: number;
    normal: number;
    abnormal: number;
    abnormalRate: number;
    dailyData: Array<{ date: string; normal: number; abnormal: number }>;
  }> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const total = mockDetections.length;
        const normal = mockDetections.filter(d => d.label === 'normal').length;
        const abnormal = mockDetections.filter(d => d.label === 'abnormal').length;
        
        // Generate daily data for last 7 days
        const dailyData = [];
        for (let i = 6; i >= 0; i--) {
          const date = new Date();
          date.setDate(date.getDate() - i);
          const dateStr = date.toISOString().split('T')[0];
          
          const dayDetections = mockDetections.filter(d => 
            d.timestamp.startsWith(dateStr)
          );
          
          dailyData.push({
            date: dateStr,
            normal: dayDetections.filter(d => d.label === 'normal').length,
            abnormal: dayDetections.filter(d => d.label === 'abnormal').length,
          });
        }
        
        resolve({
          total,
          normal,
          abnormal,
          abnormalRate: total > 0 ? (abnormal / total) * 100 : 0,
          dailyData,
        });
      }, 500);
    });
  },

  // Send frame for detection (mock)
  async detectFromFrame(frameData: any, threshold: number): Promise<Detection> {
    return new Promise((resolve) => {
      setTimeout(() => {
        const detection = generateMockDetection();
        mockDetections.unshift(detection);
        
        // Keep only last 100 detections
        if (mockDetections.length > 100) {
          mockDetections = mockDetections.slice(0, 100);
        }
        
        resolve(detection);
      }, 200); // Simulate processing time
    });
  },

  // Delete detection
  async deleteDetection(id: string): Promise<void> {
    return new Promise((resolve) => {
      setTimeout(() => {
        mockDetections = mockDetections.filter(d => d.id !== id);
        resolve();
      }, 300);
    });
  },

  // Save settings
  async saveSettings(settings: AppSettings): Promise<void> {
    return new Promise((resolve) => {
      setTimeout(() => {
        // In a real app, this would save to AsyncStorage or backend
        console.log('Settings saved:', settings);
        resolve();
      }, 300);
    });
  },
};
