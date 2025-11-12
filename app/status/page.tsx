'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import styles from './status.module.css'
import { droneApi, DroneStatus } from '@/lib/droneApi'

export default function StatusPage() {
  const [droneState, setDroneState] = useState('대기 중')
  const [status, setStatus] = useState<DroneStatus | null>(null)
  const [isRefreshing, setIsRefreshing] = useState(false)

  useEffect(() => {
    // 초기 상태 조회만 (자동 갱신 제거)
    refreshStatus()
  }, [])

  const refreshStatus = async () => {
    setIsRefreshing(true)
    try {
      // 수동 갱신 API 호출
      const response = await fetch('http://localhost:5000/api/drone/status/refresh', {
        method: 'POST'
      })
      const data = await response.json()
      console.log('상태 페이지 - 상태 갱신:', data)
      
      if (data) {
        setStatus(data)
        console.log('상태 업데이트:', data)
        
        if (data.connected) {
          if (data.flying) {
            setDroneState('비행 중')
          } else {
            setDroneState('연결됨 - 대기 중')
          }
        } else {
          setDroneState('드론 연결 안됨')
        }
      } else {
        console.warn('상태 데이터 없음')
        setDroneState('상태 조회 실패')
      }
    } catch (error) {
      console.error('상태 조회 오류:', error)
      setDroneState('상태 조회 실패')
    } finally {
      setIsRefreshing(false)
    }
  }



  return (
    <main className={styles.main}>
      <div className={styles.header}>
        <Link href="/" className={styles.backBtn}>← 뒤로</Link>
        <h1>배송 현황</h1>
      </div>

      <div className={styles.banner}>
        <div className={styles.statusMain}>
          <span className={styles.statusIcon}>
            {status?.flying ? '✈️' : status?.connected ? '🟢' : '🔴'}
          </span>
          <span className={styles.statusText}>{droneState}</span>
        </div>
        {status && status.connected && (
          <div className={styles.batteryInfo}>
            <span className={styles.batteryIcon}>🔋</span>
            <span className={styles.batteryPercent}>{status.battery}%</span>
            <div className={styles.batteryBar}>
              <div 
                className={styles.batteryFill}
                style={{ 
                  width: `${status.battery}%`,
                  backgroundColor: status.battery > 50 ? '#4CAF50' : status.battery > 20 ? '#FF9800' : '#F44336'
                }}
              />
            </div>
          </div>
        )}
      </div>

      {status?.connected && (
        <div className={styles.statsGrid}>
          <div className={styles.statCard}>
            <div className={styles.statIcon}>📍</div>
            <div className={styles.statLabel}>위도</div>
            <div className={styles.statValue}>
              {status.gps.latitude.toFixed(6)}
            </div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statIcon}>📍</div>
            <div className={styles.statLabel}>경도</div>
            <div className={styles.statValue}>
              {status.gps.longitude.toFixed(6)}
            </div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statIcon}>📏</div>
            <div className={styles.statLabel}>고도</div>
            <div className={styles.statValue}>
              {status.gps.altitude.toFixed(1)}m
            </div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statIcon}>🔋</div>
            <div className={styles.statLabel}>배터리</div>
            <div className={styles.statValue}>
              {status.battery}%
            </div>
          </div>
        </div>
      )}

      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <h2>드론 위치</h2>
          <button 
            className={styles.refreshBtn}
            onClick={refreshStatus}
            disabled={isRefreshing}
          >
            {isRefreshing ? '🔄 갱신 중...' : '🔄 새로고침'}
          </button>
        </div>
        <div className={styles.location}>
          <div className={styles.locationItem}>
            <span className={styles.locationLabel}>위도:</span>
            <span className={styles.locationValue}>
              {status?.gps.latitude.toFixed(6) || '0.000000'}
            </span>
          </div>
          <div className={styles.locationItem}>
            <span className={styles.locationLabel}>경도:</span>
            <span className={styles.locationValue}>
              {status?.gps.longitude.toFixed(6) || '0.000000'}
            </span>
          </div>
          <div className={styles.locationItem}>
            <span className={styles.locationLabel}>고도:</span>
            <span className={styles.locationValue}>
              {status?.gps.altitude.toFixed(1) || '0.0'}m
            </span>
          </div>
        </div>
      </div>



      <div className={styles.card}>
        <h2>배송 정보</h2>
        <div className={styles.info}>
          <p><strong>출발지:</strong> XXX 우체국</p>
          <p><strong>도착지:</strong> N4동 5층 옥상</p>
          <p><strong>상태:</strong> {droneState}</p>
        </div>
      </div>
    </main>
  )
}
