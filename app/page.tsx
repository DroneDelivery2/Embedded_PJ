'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import styles from './page.module.css'
import { droneApi } from '@/lib/droneApi'

export default function Home() {
  const [droneStatus, setDroneStatus] = useState('확인 중...')
  const [isConnected, setIsConnected] = useState(false)
  const [battery, setBattery] = useState(0)
  const [isConnecting, setIsConnecting] = useState(false)
  const [isChecking, setIsChecking] = useState(true)

  useEffect(() => {
    // 초기 상태 확인
    initializeStatus()
  }, [])

  const initializeStatus = async () => {
    setIsChecking(true)
    
    // 1. 서버 연결 확인
    const isHealthy = await droneApi.healthCheck()
    if (!isHealthy) {
      setDroneStatus('백엔드 서버 연결 실패')
      setIsChecking(false)
      return
    }
    
    // 2. 드론 상태 확인
    try {
      const status = await droneApi.getStatus()
      if (status && status.connected) {
        setIsConnected(true)
        setBattery(status.battery)
        setDroneStatus('드론 연결됨')
      } else {
        setIsConnected(false)
        setDroneStatus('서버 연결됨 - 드론 연결 대기 중')
      }
    } catch (error) {
      console.error('드론 상태 확인 실패:', error)
      setDroneStatus('서버 연결됨 - 드론 연결 대기 중')
    }
    
    setIsChecking(false)
  }

  const connectDrone = async () => {
    setIsConnecting(true)
    setDroneStatus('드론 연결 중...')
    
    try {
      const result = await droneApi.connect()
      console.log('연결 결과:', result)
      
      if (result.success) {
        setIsConnected(true)
        setDroneStatus('드론 연결 성공!')
        
        // 연결 응답에 포함된 상태 정보 사용
        if (result.status && result.status.connected) {
          setBattery(result.status.battery)
          console.log('연결 응답에서 배터리 업데이트:', result.status.battery)
        } else {
          // 상태 정보가 없으면 별도 조회
          await new Promise(resolve => setTimeout(resolve, 1000))
          
          const status = await droneApi.getStatus()
          console.log('별도 상태 조회 결과:', status)
          
          if (status && status.connected) {
            setBattery(status.battery)
            console.log('배터리 업데이트:', status.battery)
          }
        }
      } else {
        setIsConnected(false)
        setDroneStatus(`드론 연결 실패: ${result.message}`)
      }
    } catch (error) {
      console.error('연결 오류:', error)
      setIsConnected(false)
      setDroneStatus('드론 연결 오류')
    } finally {
      setIsConnecting(false)
    }
  }

  const disconnectDrone = async () => {
    try {
      await droneApi.disconnect()
      setIsConnected(false)
      setDroneStatus('드론 연결 해제됨')
      setBattery(0)
    } catch (error) {
      setDroneStatus('연결 해제 오류')
    }
  }

  const testConnection = async () => {
    if (isConnected) {
      const status = await droneApi.getStatus()
      console.log('테스트 상태:', status)
      
      if (status && status.connected) {
        alert(`✅ Parrot Anafi 드론 연결됨!\n배터리: ${status.battery}%\n위치: ${status.gps.latitude.toFixed(6)}, ${status.gps.longitude.toFixed(6)}\n고도: ${status.gps.altitude.toFixed(1)}m`)
        
        // UI 업데이트
        setBattery(status.battery)
      } else {
        alert('❌ 상태 정보를 가져올 수 없습니다.')
      }
    } else {
      alert('❌ 드론을 찾을 수 없습니다.\n드론을 켜고 WiFi에 연결하세요.')
    }
  }

  return (
    <main className={styles.main}>
      <div className={styles.header}>
        <h1>🚁 드론 배송 시스템</h1>
        <p>Parrot Anafi 드론 제어</p>
      </div>

      <div className={styles.statusCard}>
        <h2>드론 상태</h2>
        <p className={styles.status}>{droneStatus}</p>
        {isConnected && <p className={styles.battery}>🔋 배터리: {battery}%</p>}
        
        <div className={styles.btnGroup}>
          {isChecking ? (
            <button className={styles.connectBtn} disabled>
              확인 중...
            </button>
          ) : !isConnected ? (
            <button 
              className={styles.connectBtn}
              onClick={connectDrone}
              disabled={isConnecting}
            >
              {isConnecting ? '연결 중...' : '드론 연결'}
            </button>
          ) : (
            <>
              <button 
                className={styles.testBtn}
                onClick={testConnection}
              >
                상태 확인
              </button>
              <button 
                className={styles.disconnectBtn}
                onClick={disconnectDrone}
              >
                연결 해제
              </button>
            </>
          )}
        </div>
      </div>

      <div className={styles.actions}>
        <Link href="/control" className={styles.actionBtn}>
          <div className={styles.btnContent}>
            <span className={styles.icon}>🎮</span>
            <span>드론 제어</span>
          </div>
        </Link>

        <Link href="/status" className={styles.actionBtn}>
          <div className={styles.btnContent}>
            <span className={styles.icon}>📊</span>
            <span>배송 현황</span>
          </div>
        </Link>

        <Link href="/request" className={styles.actionBtn}>
          <div className={styles.btnContent}>
            <span className={styles.icon}>🚀</span>
            <span>배송 시작</span>
          </div>
        </Link>
      </div>

      <div className={styles.info}>
        <h3>사용 방법</h3>
        <ol>
          <li>Parrot Anafi 드론 전원 ON</li>
          <li>스마트폰을 드론 WiFi에 연결 (ANAFI-XXXXXX)</li>
          <li>앱에서 드론 연결 확인</li>
          <li>배송 시작 버튼으로 미션 수행</li>
        </ol>
      </div>
    </main>
  )
}
