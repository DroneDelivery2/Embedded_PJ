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
    { name: 'N4동 5층 옥상', lat: 37.5705, lng: 126.9820, alt: 15 },
    { name: 'XXX 우체국', lat: 37.5715, lng: 126.9830, alt: 10 }
  ]

  const handleStartDelivery = async () => {
    if (!origin || !destination) {
      alert('출발지와 도착지를 모두 선택해주세요.')
      return
    }

    setIsStarting(true)

    try {
      // 웨이포인트 생성
      const waypoints: Waypoint[] = [
        { lat: origin.lat, lng: origin.lng, alt: origin.alt },
        { lat: destination.lat, lng: destination.lng, alt: destination.alt }
      ]

      // 미션 시작
      const result = await droneApi.startMission(waypoints)

      if (result.success) {
        alert('배송이 시작되었습니다!')
        router.push('/status')
      } else {
        alert(`배송 시작 실패: ${result.message}`)
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
