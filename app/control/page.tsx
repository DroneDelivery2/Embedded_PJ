'use client'

import { useState } from 'react'
import Link from 'next/link'
import styles from './control.module.css'

export default function ControlPage() {
  const [message, setMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleTakeoff = async () => {
    setIsLoading(true)
    setMessage('이륙 명령 전송 중...')
    
    try {
      const response = await fetch('http://localhost:5000/api/drone/takeoff', {
        method: 'POST'
      })
      const data = await response.json()
      
      if (data.success) {
        setMessage(`✅ ${data.message}`)
      } else {
        setMessage(`❌ ${data.message}`)
      }
    } catch (error) {
      setMessage('❌ 서버 연결 실패')
    } finally {
      setIsLoading(false)
    }
  }

  const handleLand = async () => {
    setIsLoading(true)
    setMessage('착륙 명령 전송 중...')
    
    try {
      const response = await fetch('http://localhost:5000/api/drone/land', {
        method: 'POST'
      })
      const data = await response.json()
      
      if (data.success) {
        setMessage(`✅ ${data.message}`)
      } else {
        setMessage(`❌ ${data.message}`)
      }
    } catch (error) {
      setMessage('❌ 서버 연결 실패')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className={styles.main}>
      <div className={styles.header}>
        <Link href="/" className={styles.backBtn}>← 뒤로</Link>
        <h1>드론 제어</h1>
      </div>

      <div className={styles.card}>
        <h2>수동 제어</h2>
        <p className={styles.warning}>
          ⚠️ 주의: 드론이 연결되어 있고 안전한 환경에서만 사용하세요
        </p>
        
        {message && (
          <div className={styles.message}>
            {message}
          </div>
        )}

        <div className={styles.controls}>
          <button 
            className={`${styles.controlBtn} ${styles.takeoffBtn}`}
            onClick={handleTakeoff}
            disabled={isLoading}
          >
            <span className={styles.icon}>🚁</span>
            <span>이륙</span>
          </button>

          <button 
            className={`${styles.controlBtn} ${styles.landBtn}`}
            onClick={handleLand}
            disabled={isLoading}
          >
            <span className={styles.icon}>🛬</span>
            <span>착륙</span>
          </button>
        </div>
      </div>

      <div className={styles.info}>
        <h3>사용 방법</h3>
        <ol>
          <li>드론이 평평한 바닥에 놓여 있는지 확인</li>
          <li>주변에 장애물이 없는지 확인</li>
          <li>이륙 버튼을 눌러 드론 이륙</li>
          <li>착륙 버튼을 눌러 드론 착륙</li>
        </ol>
        
        <h3>실내 비행 시</h3>
        <ul>
          <li>FreeFlight 앱에서 "실내 비행" 모드 활성화 필요</li>
          <li>GPS 신호가 없어도 이륙 가능</li>
          <li>충분한 공간 확보 (최소 3m x 3m)</li>
        </ul>
      </div>
    </main>
  )
}
