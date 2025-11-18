/**
 * 드론 API 클라이언트
 * 백엔드 서버와 통신
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export interface DroneStatus {
  connected: boolean;
  battery: number;
  gps: {
    latitude: number;
    longitude: number;
    altitude: number;
  };
  flying: boolean;
}

export interface Waypoint {
  lat: number;
  lng: number;
  alt: number;
}

class DroneAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * 드론 연결
   */
  async connect(ip: string = '192.168.42.1'): Promise<{ success: boolean; message: string; status?: DroneStatus }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/drone/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip })
      });
      const data = await response.json();
      console.log('API 연결 응답:', data);
      return data;
    } catch (error) {
      console.error('드론 연결 오류:', error);
      return { success: false, message: '서버 연결 실패' };
    }
  }

  /**
   * 드론 연결 해제
   */
  async disconnect(): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/drone/disconnect`, {
        method: 'POST'
      });
      return await response.json();
    } catch (error) {
      console.error('드론 연결 해제 오류:', error);
      return { success: false, message: '서버 연결 실패' };
    }
  }

  /**
   * 드론 상태 조회
   */
  async getStatus(): Promise<DroneStatus | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/drone/status`);
      return await response.json();
    } catch (error) {
      console.error('드론 상태 조회 오류:', error);
      return null;
    }
  }

  /**
   * 이륙
   */
  async takeoff(): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/drone/takeoff`, {
        method: 'POST'
      });
      return await response.json();
    } catch (error) {
      console.error('이륙 오류:', error);
      return { success: false, message: '서버 연결 실패' };
    }
  }

  /**
   * 착륙
   */
  async land(): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/drone/land`, {
        method: 'POST'
      });
      return await response.json();
    } catch (error) {
      console.error('착륙 오류:', error);
      return { success: false, message: '서버 연결 실패' };
    }
  }

  /**
   * GPS 좌표로 이동 (안전 고도 자동 계산: max(출발지, 도착지) + 3m)
   */
  async moveToGPS(latitude: number, longitude: number, destAltitude: number = 0): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/drone/move-gps`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude, longitude, altitude: destAltitude })
      });
      return await response.json();
    } catch (error) {
      console.error('GPS 이동 오류:', error);
      return { success: false, message: '서버 연결 실패' };
    }
  }

  /**
   * 미션 시작
   */
  async startMission(waypoints: Waypoint[]): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/drone/mission`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ waypoints })
      });
      return await response.json();
    } catch (error) {
      console.error('미션 오류:', error);
      return { success: false, message: '서버 연결 실패' };
    }
  }

  /**
   * 서버 헬스 체크
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      const data = await response.json();
      return data.status === 'ok';
    } catch (error) {
      console.error('헬스 체크 오류:', error);
      return false;
    }
  }
}

export const droneApi = new DroneAPI();
