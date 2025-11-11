#!/usr/bin/env python3
"""
Parrot Anafi 드론 제어 모듈
Olympe SDK를 사용한 드론 연결 및 제어
"""

import olympe
from olympe.messages.ardrone3.Piloting import TakeOff, Landing, moveTo
from olympe.messages.ardrone3.PilotingState import FlyingStateChanged
from olympe.enums.ardrone3.Piloting import MoveTo_Orientation_mode
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DroneController:
    def __init__(self, drone_ip="192.168.42.1"):
        """
        드론 컨트롤러 초기화
        :param drone_ip: Parrot Anafi 드론 IP (기본값: 192.168.42.1)
        """
        self.drone_ip = drone_ip
        self.drone = None
        self.is_connected = False
        
    def connect(self):
        """드론 연결"""
        try:
            logger.info(f"드론 연결 시도: {self.drone_ip}")
            self.drone = olympe.Drone(self.drone_ip)
            self.drone.connect()
            self.is_connected = True
            logger.info("드론 연결 성공!")
            return True
        except Exception as e:
            logger.error(f"드론 연결 실패: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """드론 연결 해제"""
        if self.drone and self.is_connected:
            self.drone.disconnect()
            self.is_connected = False
            logger.info("드론 연결 해제")
    
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
            # 배터리 상태
            battery = self.drone.get_state(olympe.messages.common.CommonState.BatteryStateChanged)
            
            # GPS 위치
            gps = self.drone.get_state(olympe.messages.ardrone3.PilotingState.PositionChanged)
            
            # 비행 상태
            flying_state = self.drone.get_state(FlyingStateChanged)
            
            return {
                "connected": True,
                "battery": battery["percent"] if battery else 0,
                "gps": {
                    "latitude": gps["latitude"] if gps else 0,
                    "longitude": gps["longitude"] if gps else 0,
                    "altitude": gps["altitude"] if gps else 0
                },
                "flying": flying_state["state"] == "flying" if flying_state else False
            }
        except Exception as e:
            logger.error(f"상태 조회 실패: {e}")
            return None
    
    def takeoff(self):
        """이륙"""
        if not self.is_connected:
            return False
        
        try:
            logger.info("이륙 시작")
            self.drone(TakeOff()).wait()
            logger.info("이륙 완료")
            return True
        except Exception as e:
            logger.error(f"이륙 실패: {e}")
            return False
    
    def land(self):
        """착륙"""
        if not self.is_connected:
            return False
        
        try:
            logger.info("착륙 시작")
            self.drone(Landing()).wait()
            logger.info("착륙 완료")
            return True
        except Exception as e:
            logger.error(f"착륙 실패: {e}")
            return False
    
    def move_to(self, latitude, longitude, altitude, orientation=0):
        """
        지정된 GPS 좌표로 이동
        :param latitude: 위도
        :param longitude: 경도
        :param altitude: 고도 (미터)
        :param orientation: 방향 (도)
        """
        if not self.is_connected:
            return False
        
        try:
            logger.info(f"이동 시작: ({latitude}, {longitude}, {altitude}m)")
            self.drone(
                moveTo(latitude, longitude, altitude, 
                       MoveTo_Orientation_mode.TO_TARGET, orientation)
            ).wait()
            logger.info("이동 완료")
            return True
        except Exception as e:
            logger.error(f"이동 실패: {e}")
            return False
    
    def start_mission(self, waypoints):
        """
        미션 시작 (여러 웨이포인트 순회)
        :param waypoints: [{"lat": float, "lng": float, "alt": float}, ...]
        """
        if not self.is_connected:
            return False
        
        try:
            # 이륙
            if not self.takeoff():
                return False
            
            time.sleep(3)  # 안정화 대기
            
            # 각 웨이포인트 순회
            for i, wp in enumerate(waypoints):
                logger.info(f"웨이포인트 {i+1}/{len(waypoints)} 이동 중...")
                self.move_to(wp["lat"], wp["lng"], wp["alt"])
                time.sleep(2)  # 각 지점에서 대기
            
            # 착륙
            self.land()
            return True
            
        except Exception as e:
            logger.error(f"미션 실패: {e}")
            # 비상 착륙
            self.land()
            return False


if __name__ == "__main__":
    # 테스트 코드
    controller = DroneController()
    
    if controller.connect():
        print("드론 연결 성공!")
        status = controller.get_status()
        print(f"드론 상태: {status}")
        controller.disconnect()
    else:
        print("드론 연결 실패")
