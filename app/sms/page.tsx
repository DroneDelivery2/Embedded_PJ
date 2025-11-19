'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import styles from './sms.module.css'

interface SMSItem {
  phone: string
  message: string
  timestamp: number
  status: 'pending' | 'sent'
  sent_at?: number
}

interface SMSQueueStatus {
  total: number
  pending: number
  sent: number
}

export default function SMSPage() {
  const [smsQueue, setSmsQueue] = useState<SMSItem[]>([])
  const [queueStatus, setQueueStatus] = useState<SMSQueueStatus>({ total: 0, pending: 0, sent: 0 })
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')

  const fetchSMSQueue = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('http://localhost:5000/api/sms/queue')
      const data = await response.json()
      
      if (data.success) {
        setSmsQueue(data.queue || [])
        setQueueStatus(data.status || { total: 0, pending: 0, sent: 0 })
      } else {
        setMessage('SMS 큐 조회 실패')
      }
    } catch (error) {
      console.error('SMS 큐 조회 오류:', error)
      setMessage('서버 연결 실패')
    } finally {
      setIsLoading(false)
    }
  }

  const sendQueuedSMS = async () => {
    setIsLoading(true)
    setMessage('SMS 전송 중...')
    
    try {
      const response = await fetch('http://localhost:5000/api/sms/send', {
        method: 'POST'
      })
      const data = await response.json()
      
      if (data.success) {
        setMessage(`✅ SMS 전송 완료: 성공 ${data.success_count}건, 실패 ${data.fail_count}건`)
        fetchSMSQueue()
      } else {
        setMessage(`❌ SMS 전송 실패: ${data.message}`)
      }
    } catch (error) {
      console.error('SMS 전송 오류:', error)
      setMessage('❌ 서버 연결 실패')
    } finally {
      setIsLoading(false)
    }
  }

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString('ko-KR')
  }

  const formatPhone = (phone: string) => {
    if (phone.length >= 8) {
      return phone.slice(0, 3) + '****' + phone.slice(-4)
    }
    return phone
  }

  useEffect(() => {
    fetchSMSQueue()
  }, [])

  return (
    <main className={styles.main}>
      <div className={styles.header}>
        <Link href="/" className={styles.backBtn}>← 뒤로</Link>
        <h1>📱 SMS 알림 관리</h1>
      </div>

      <div className={styles.statusCard}>
        <h2>큐 상태</h2>
        <div className={styles.statusGrid}>
          <div className={styles.statusItem}>
            <span className={styles.statusLabel}>전체</span>
            <span className={styles.statusValue}>{queueStatus.total}건</span>
          </div>
          <div className={styles.statusItem}>
            <span className={styles.statusLabel}>대기 중</span>
            <span className={`${styles.statusValue} ${styles.pending}`}>{queueStatus.pending}건</span>
          </div>
          <div className={styles.statusItem}>
            <span className={styles.statusLabel}>전송 완료</span>
            <span className={`${styles.statusValue} ${styles.sent}`}>{queueStatus.sent}건</span>
          </div>
        </div>
      </div>

      <div className={styles.controls}>
        <button 
          onClick={fetchSMSQueue}
          disabled={isLoading}
          className={styles.refreshBtn}
        >
          🔄 새로고침
        </button>
        
        {queueStatus.pending > 0 && (
          <button 
            onClick={sendQueuedSMS}
            disabled={isLoading}
            className={styles.sendBtn}
          >
            📤 대기 중인 SMS 전송 ({queueStatus.pending}건)
          </button>
        )}
      </div>

      {message && (
        <div className={styles.message}>
          {message}
        </div>
      )}

      <div className={styles.queueCard}>
        <h2>SMS 큐 목록</h2>
        
        {isLoading ? (
          <div className={styles.loading}>로딩 중...</div>
        ) : smsQueue.length === 0 ? (
          <div className={styles.empty}>
            📭 SMS 큐가 비어있습니다
          </div>
        ) : (
          <div className={styles.queueList}>
            {smsQueue.map((sms, index) => (
              <div key={index} className={`${styles.queueItem} ${styles[sms.status]}`}>
                <div className={styles.queueHeader}>
                  <span className={styles.phone}>{formatPhone(sms.phone)}</span>
                  <span className={`${styles.status} ${styles[sms.status]}`}>
                    {sms.status === 'pending' ? '⏳ 대기 중' : '✅ 전송 완료'}
                  </span>
                </div>
                
                <div className={styles.queueMessage}>
                  {sms.message}
                </div>
                
                <div className={styles.queueFooter}>
                  <span className={styles.timestamp}>
                    📅 생성: {formatDate(sms.timestamp)}
                  </span>
                  {sms.sent_at && (
                    <span className={styles.timestamp}>
                      📤 전송: {formatDate(sms.sent_at)}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className={styles.info}>
        <h3>💡 사용 안내</h3>
        <ul>
          <li><strong>대기 중</strong>: 드론 배송 완료 시 생성된 SMS (아직 전송 안됨)</li>
          <li><strong>전송 완료</strong>: 인터넷 연결 시 NCP SMS로 전송된 메시지</li>
          <li><strong>자동 전송</strong>: 인터넷 연결 시 자동으로 대기 중인 SMS 전송</li>
          <li><strong>수동 전송</strong>: "대기 중인 SMS 전송" 버튼으로 즉시 전송</li>
        </ul>
      </div>
    </main>
  )
}
