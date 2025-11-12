'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import styles from './status.module.css';

interface DeliveryStatus {
  isActive: boolean;
  origin: string;
  destination: string;
  currentPhase: string;
  latitude: number;
  longitude: number;
  altitude: number;
}

export default function StatusPage() {
  const [connected, setConnected] = useState(false);
  const [statusMessage, setStatusMessage] = useState('드론 연결 안됨');
  const [notification, setNotification] = useState({ message: '', type: '' });
  const [loading, setLoading] = useState(false);
  const [deliveryStatus, setDeliveryStatus] = useState<DeliveryStatus>({
    isActive: false,
    origin: 'XXX 우체국',
    destination: 'N4동 5층 옥상',
    currentPhase: '드론 연결 안됨',
    latitude: 0.0,
    longitude: 0.0,
    altitude: 0.0
  });

  const API_BASE = 'http://localhost:5000';

  // 드론 상태 조회
  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/status`);
      const data = await response.json();
      setConnected(data.connected);
      setStatusMessage(data.connected ? '드론 연결됨' : '드론 연결 안됨');
      
      setDeliveryStatus(prev => ({
        ...prev,
        currentPhase: data.connected ? '드론 연결됨' : '드론 연결 안됨'
      }));
    } catch (error) {
      setConnected(false);
      setStatusMessage('드론 연결 안됨');
      setDeliveryStatus(prev => ({
        ...prev,
        currentPhase: '드론 연결 안됨'
      }));
    }
  };

  // 이륙 명령 (배송 시작)
  const handleTakeoff = async () => {
    setLoading(true);
    showNotification('이륙 명령 전송 중...', 'info');

    try {
      const response = await fetch(`${API_BASE}/api/takeoff`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();

      if (data.success) {
        showNotification('이륙 성공!', 'success');
        setDeliveryStatus({
          isActive: true,
          origin: 'XXX 우체국',
          destination: 'N4동 5층 옥상',
          currentPhase: '이륙 완료 - 목적지로 이동 중',
          latitude: 37.5665,
          longitude: 126.9780,
          altitude: 10.5
        });
      } else {
        showNotification(data.message, 'error');
      }
    } catch (error) {
      showNotification('이륙 명령 실패', 'error');
    } finally {
      setLoading(false);
      fetchStatus();
    }
  };

  // 착륙 명령 (배송 완료)
  const handleLand = async () => {
    setLoading(true);
    showNotification('착륙 명령 전송 중...', 'info');

    try {
      const response = await fetch(`${API_BASE}/api/land`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();

      if (data.success) {
        showNotification('착륙 성공!', 'success');
        setDeliveryStatus({
          isActive: false,
          origin: 'XXX 우체국',
          destination: 'N4동 5층 옥상',
          currentPhase: '배송 완료',
          latitude: 0.0,
          longitude: 0.0,
          altitude: 0.0
        });
      } else {
        showNotification(data.message, 'error');
      }
    } catch (error) {
      showNotification('착륙 명령 실패', 'error');
    } finally {
      setLoading(false);
      fetchStatus();
    }
  };

  // 새로고침
  const handleRefresh = () => {
    fetchStatus();
    showNotification('상태 새로고침', 'info');
  };

  // 알림 표시
  const showNotification = (message: string, type: string) => {
    setNotification({ message, type });
    setTimeout(() => {
      setNotification({ message: '', type: '' });
    }, 3000);
  };

  // 초기 로드 및 주기적 상태 업데이트
  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className={styles.container}>
      {/* 헤더 */}
      <header className={styles.header}>
        <Link href="/" className={styles.backBtn}>
          ← 뒤로
        </Link>
        <h1 className={styles.title}>배송 현황</h1>
      </header>

      <main className={styles.main}>
        {/* 드론 연결 상태 카드 */}
        <div className={styles.statusCard}>
          <div className={styles.statusBadge}>
            <span className={`${styles.statusDot} ${connected ? styles.connected : styles.disconnected}`}></span>
            <span className={styles.statusText}>{statusMessage}</span>
          </div>
        </div>

        {/* 드론 위치 카드 */}
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <h2 className={styles.cardTitle}>드론 위치</h2>
            <button onClick={handleRefresh} className={styles.refreshBtn}>
              🔄 새로고침
            </button>
          </div>

          <div className={styles.locationInfo}>
            <div className={styles.locationItem}>
              <span className={styles.locationLabel}>위도:</span>
              <span className={styles.locationValue}>
                {deliveryStatus.latitude.toFixed(6)}
              </span>
            </div>
            <div className={styles.locationItem}>
              <span className={styles.locationLabel}>경도:</span>
              <span className={styles.locationValue}>
                {deliveryStatus.longitude.toFixed(6)}
              </span>
            </div>
            <div className={styles.locationItem}>
              <span className={styles.locationLabel}>고도:</span>
              <span className={styles.locationValue}>
                {deliveryStatus.altitude.toFixed(1)}m
              </span>
            </div>
          </div>
        </div>

        {/* 배송 정보 카드 */}
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>배송 정보</h2>
          
          <div className={styles.deliveryInfo}>
            <div className={styles.infoRow}>
              <span className={styles.infoLabel}>출발지:</span>
              <span className={styles.infoValue}>{deliveryStatus.origin}</span>
            </div>
            <div className={styles.infoRow}>
              <span className={styles.infoLabel}>도착지:</span>
              <span className={styles.infoValue}>{deliveryStatus.destination}</span>
            </div>
            <div className={styles.infoRow}>
              <span className={styles.infoLabel}>상태:</span>
              <span className={styles.infoValue}>{deliveryStatus.currentPhase}</span>
            </div>
          </div>
        </div>

        {/* 제어 버튼 */}
        <div className={styles.controlButtons}>
          <button
            onClick={handleTakeoff}
            disabled={!connected || loading || deliveryStatus.isActive}
            className={`${styles.controlBtn} ${styles.takeoffBtn}`}
          >
            ✈️ 이륙
          </button>
          <button
            onClick={handleLand}
            disabled={!connected || loading}
            className={`${styles.controlBtn} ${styles.landBtn}`}
          >
            🛬 착륙
          </button>
        </div>

        {/* 알림 메시지 */}
        {notification.message && (
          <div className={`${styles.notification} ${styles[notification.type]}`}>
            {notification.message}
          </div>
        )}
      </main>
    </div>
  );
}
