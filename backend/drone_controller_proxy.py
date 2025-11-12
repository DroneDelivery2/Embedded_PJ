#!/usr/bin/env python3
"""
드론 컨트롤러 (프록시 버전)
Windows 프록시 서버를 통해 드론 제어
WSL2에서 실행
"""

import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DroneController:
    def __init__(self, proxy_url="http://172.19.240.1:5001"):
        """
        드론 컨트롤러 초기화 (프록시 버전)
        :param proxy_url: Windows 프록시 서버 URL
        """
        self.proxy_url = proxy_url
        self.is_connected = False
        self.session = requests.Session()
        self.session.timeout = 10
        
    def connect(self):
        """드론 연결 (프록시 통해)"""
        try:
            logger.info(f"프록시를 통해 드론 연결 시도: {self.proxy_url}")
            
            response = self.session.post(
                f"{self.proxy_url}/connect",
                json={'ip': '192.168.42.1'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.is_connected = True
                    logger.info("✅ 드론 연결 성공!")
                    return True
            
            logger.error("❌ 드론 연결 실패")
            self.is_connected = False
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 프록시 연결 실패: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """드론 연결 해제"""
        try:
            response = self.session.post(
                f"{self.proxy_url}/disconnect",
                timeout=5
            )
            self.is_connected = False
            logger.info("드론 연결 해제")
        except Exception as e:
            logger.error(f"연결 해제 오류: {e}")
            self.is_connected = False
    
    def get_status(self):
        """드론 상태 조회"""
        if not self.is_connected:
            return {
                "connected": False,
                "battery": 0,
                "gps": {"latitude": 0, "longitude": 0, "altitude": 0},
                "flying": False
            }
        
        try:
            response = self.session.get(
                f"{self.proxy_url}/status",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            
            return {
                "connected": True,
                "battery": 0,
                "gps": {"latitude": 0, "longitude": 0, "altitude": 0},
                "flying": False
            }
            
        except Exception as e:
            logger.error(f"상태 조회 실패: {e}")
            return {
                "connected": True,
                "battery": 0,
                "gps": {"latitude": 0, "longitude": 0, "altitude": 0},
                "flying": False
            }
    
    def takeoff(self):
        """이륙"""
        if not self.is_connected:
            return False
        
        try:
            logger.info("🚁 이륙 명령 전송...")
            
            response = self.session.post(
                f"{self.proxy_url}/takeoff",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    logger.info("✅ 이륙 성공!")
                    return True
            
            logger.error("❌ 이륙 실패")
            return False
            
        except Exception as e:
            logger.error(f"❌ 이륙 실패: {e}")
            return False
    
    def land(self):
        """착륙"""
        if not self.is_connected:
            return False
        
        try:
            logger.info("🛬 착륙 명령 전송...")
            
            response = self.session.post(
                f"{self.proxy_url}/land",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    logger.info("✅ 착륙 성공!")
                    return True
            
            logger.error("❌ 착륙 실패")
            return False
            
        except Exception as e:
            logger.error(f"❌ 착륙 실패: {e}")
            return False
    
    def move_by(self, dx, dy, dz, dyaw):
        """상대 이동"""
        if not self.is_connected:
            return False
        
        try:
            logger.info(f"📍 이동 명령 전송: dx={dx}, dy={dy}, dz={dz}")
            
            response = self.session.post(
                f"{self.proxy_url}/move",
                json={'dx': dx, 'dy': dy, 'dz': dz, 'dyaw': dyaw},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    logger.info("✅ 이동 성공!")
                    return True
            
            logger.error("❌ 이동 실패")
            return False
            
        except Exception as e:
            logger.error(f"❌ 이동 실패: {e}")
            return False
    
    def start_mission(self, waypoints):
        """간단한 미션"""
        if not self.is_connected:
            return False
        
        try:
            logger.info("🚀 미션 시작!")
            
            # 이륙
            if not self.takeoff():
                return False
            
            import time
            time.sleep(2)
            
            # 간단한 이동
            self.move_by(5, 0, 0, 0)  # 전진 5m
            time.sleep(2)
            
            self.move_by(0, 3, 0, 0)  # 우측 3m
            time.sleep(2)
            
            # 착륙
            self.land()
            
            logger.info("✅ 미션 완료!")
            return True
            
        except Exception as e:
            logger.error(f"❌ 미션 실패: {e}")
            try:
                self.land()
            except:
                pass
            return False


if __name__ == "__main__":
    # 테스트
    controller = DroneController()
    
    if controller.connect():
        print("드론 연결 성공!")
        status = controller.get_status()
        print(f"드론 상태: {status}")
        controller.disconnect()
    else:
        print("드론 연결 실패")
