'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import styles from './request.module.css'
import { droneApi, Waypoint } from '@/lib/droneApi'

interface Site {
  name: string
  lat: number
  lng: number
  alt: number
}

export default function RequestPage() {
  const router = useRouter()
  const [origin, setOrigin] = useState<Site | null>(null)
  const [destination, setDestination] = useState<Site | null>(null)
  const [isStarting, setIsStarting] = useState(false)

  // 실제 GPS 좌표로 변경 필요
  const sites: Site[] = [
    { name: 'site 1', lat: 37.5665, lng: 126.9780, alt: 10 },
    { name: 'site 2', lat: 37.5675, lng: 126.9790, alt: 10 },
    { name: 'site 3', lat: 37.5685, lng: 126.9800, alt: 10 },
    { name: 'site 4', lat: 37.5695, lng: 126.9810, alt: 10 },
    { name: 'N4동 5층 옥상', lat: 36.352590, lng: 127.301334, alt: 126.1 },
    { name: 'N4동 6층 옥상', lat: 36.352093, lng: 127.301639, alt: 118.0 }
  ]

  const handleStartDelivery = async () => {
    if (!origin || !destination) {
      alert('출발지와 도착지를 모두 선택해주세요.')
      return
    }

    setIsStarting(true)

    // site 1, 2 선택 시 실내 모드
    const isIndoorMode = (origin.name === 'site 1' && destination.name === 'site 2') ||
                         (origin.name === 'site 2' && destination.name === 'site 1')

    try {
      let response

      if (isIndoorMode) {
        // 실내 모드: 상대 좌표 이동 (2m 왕복)
        alert('실내 모드: 2m 왕복 테스트를 시작합니다')
        response = await fetch('http://localhost:5000/api/delivery/indoor', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ distance: 2.0 })
        })
      } else {
        // 실외 모드: GPS 좌표 이동
        alert('실외 모드: GPS 배송을 시작합니다')
        response = await fetch('http://localhost:5000/api/delivery/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            origin_lat: origin.lat,
            origin_lng: origin.lng,
            dest_lat: destination.lat,
            dest_lng: destination.lng,
            altitude: destination.alt
          })
        })
      }

      const data = await response.json()

      if (data.success) {
        alert('배송이 시작되었습니다!')
        router.push('/status')
      } else {
        alert(`배송 시작 실패: ${data.message}`)
      }
    } catch (error) {
      alert('배송 시작 중 오류가 발생했습니다.')
    } finally {
      setIsStarting(false)
    }
  }

  return (
    <main className={styles.main}>
      <div className={styles.header}>
        <Link href="/" className={styles.backBtn}>← 뒤로</Link>
        <h1>배송 요청</h1>
      </div>

      <div className={styles.card}>
        <h2>출발지</h2>
        <input
          type="text"
          placeholder="출발지를 선택하세요"
          value={origin?.name || ''}
          readOnly
          className={styles.input}
        />
      </div>

      <div className={styles.card}>
        <h2>도착지</h2>
        <input
          type="text"
          placeholder="도착지를 선택하세요"
          value={destination?.name || ''}
          readOnly
          className={styles.input}
        />
      </div>

      <div className={styles.card}>
        <h2>장소 선택</h2>
        <div className={styles.siteList}>
          {sites.map((site, index) => (
            <div key={index} className={styles.siteItem}>
              <div>
                <div className={styles.siteName}>{site.name}</div>
                <div className={styles.siteCoords}>
                  {site.lat.toFixed(4)}, {site.lng.toFixed(4)}
                </div>
              </div>
              <button
                className={styles.selectBtn}
                onClick={() => {
                  if (!origin) {
                    setOrigin(site)
                  } else if (!destination) {
                    setDestination(site)
                  }
                }}
              >
                선택
              </button>
            </div>
          ))}
        </div>
      </div>

      <button
        className={styles.startBtn}
        onClick={handleStartDelivery}
        disabled={isStarting || !origin || !destination}
      >
        {isStarting ? '배송 시작 중...' : '배송 시작'}
      </button>
    </main>
  )
}
