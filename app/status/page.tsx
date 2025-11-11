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
    // 초기 상태 조회
    refreshStatus()

    // 5초마다 자동 갱신
    const interval = setInterval(refreshStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  const refreshStatus = async () => {
    setIsRefreshing(true)
    try {
      const data = await droneApi.getStatus()
      if (data) {
        setStatus(data)
        if (data.connected) {
          if (data.flying) {
            setDroneState('비행 중')
          } else {
            setDroneState('연결됨 - 대기 중')
          }
        } else {
          setDroneState('드론 연결 안됨')
        }
      }
    } catch (error) {
      setDroneState('상태 조회 실패')
    } finally {
      setIsRefreshing(false)
    }
  }

  const handleTakeoff = async () => {
    const result = await droneApi.takeoff()
    if (result.success) {
      alert('이륙 성공!')
      refreshStatus()
    } else {
      alert(`이륙 실패: ${result.message}`)
    }
  }

  const handleLand = async () => {
    const result = await droneApi.land()
    if (result.success) {
      alert('착륙 성공!')
      refreshStatus()
    } else {
      alert(`착륙 실패: ${result.message}`)
    }
  }

  return (
    <main className={styles.main}>
      <div className={styles.header}>
        <Link href="/" className={styles.backBtn}>← 뒤로</Link>
        <h1>배송 현황</h1>
      </div>

      <div className={styles.banner}>
        <p>{droneState}</p>
        {status && status.connected && (
          <p className={styles.battery}>🔋 {status.battery}%</p>
        )}
      </div>

      <div className={styles.card}>
        <h2>드론 위치</h2>
        <div className={styles.location}>
          <p>위도: {status?.gps.latitude.toFixed(6) || '0.000000'}</p>
          <p>경도: {status?.gps.longitude.toFixed(6) || '0.000000'}</p>
          <p>고도: {status?.gps.altitude.toFixed(1) || '0.0'}m</p>
        </div>
        <button 
          className={styles.refreshBtn}
          onClick={refreshStatus}
          disabled={isRefreshing}
        >
          {isRefreshing ? '갱신 중...' : '위치 갱신'}
        </button>
      </div>

      {status?.connected && (
        <div className={styles.card}>
          <h2>드론 제어</h2>
          <div className={styles.controls}>
            <button 
              className={styles.controlBtn}
              onClick={handleTakeoff}
              disabled={status.flying}
            >
              🚁 이륙
            </button>
            <button 
              className={styles.controlBtn}
              onClick={handleLand}
              disabled={!status.flying}
            >
              🛬 착륙
            </button>
          </div>
        </div>
      )}

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
