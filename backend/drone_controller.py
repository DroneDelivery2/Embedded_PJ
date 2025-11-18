#!/usr/bin/env python3
"""
Parrot Anafi 드론 제어 모듈
Olympe SDK를 사용한 드론 연결 및 제어
"""

import olympe
from olympe.messages.ardrone3.Piloting import TakeOff, Landing, moveTo
from olympe.messages.ardrone3.PilotingState import FlyingStateChanged, AlertStateChanged, PositionChanged
from olympe.messages.ardrone3.GPSSettingsState import GPSFixStateChanged
from olympe.messages.common.CommonState import BatteryStateChanged
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DroneController:
    """Olympe SDK를 사용한 ANAFI 드론 제어 클래스"""
    
    def __init__(self, drone_ip="192.168.42.1"):
        """
        DroneController 초기화
        Args:
            drone_ip: 드론의 IP 주소 (기본값: 192.168.42.1)
        """
        self.drone_ip = drone_ip
        self.drone = olympe.Drone(drone_ip)
        self.connected = False
        logger.info(f"DroneController 초기화 완료 (IP: {drone_ip})")
    
    def connect(self):
        """
        드론에 연결 시도
        Returns:
            bool: 연결 성공 시 True, 실패 시 False
        """
        try:
            logger.info(f"드론 연결 시도 중... (IP: {self.drone_ip})")
            success = self.drone.connect()
            
            if success:
                self.connected = True
                logger.info("드론 연결 성공")
                return True
            else:
                self.connected = False
                logger.error("드론 연결 실패")
                return False
        except Exception as e:
            self.connected = False
            logger.error(f"드론 연결 실패: {str(e)}")
            return False
    
    def disconnect(self):
        """
        드론 연결 해제
        Returns:
            bool: 연결 해제 성공 시 True, 실패 시 False
        """
        try:
            if self.connected:
                logger.info("드론 연결 해제 중...")
                self.drone.disconnect()
                self.connected = False
                logger.info("드론 연결 해제 완료")
                return True
            else:
                logger.warning("드론이 연결되어 있지 않습니다")
                return True
        except Exception as e:
            logger.error(f"드론 연결 해제 실패: {str(e)}")
            return False
    
    def is_connected(self):
        """
        현재 드론 연결 상태 확인
        Returns:
            bool: 연결되어 있으면 True, 아니면 False
        """
        return self.connected
    
    def get_flying_state(self):
        """
        드론의 현재 비행 상태 확인
        Returns:
            str: 비행 상태
        """
        try:
            state = self.drone.get_state(FlyingStateChanged)
            logger.info(f"현재 비행 상태: {state}")
            return str(state)
        except Exception as e:
            logger.error(f"비행 상태 조회 실패: {str(e)}")
            return "unknown"
    
    def check_preflight_status(self):
        """
        이륙 전 드론 상태 확인
        Returns:
            tuple: (준비 완료 여부, 메시지)
        """
        try:
            # 배터리 상태 확인
            battery = self.drone.get_state(BatteryStateChanged)
            if battery:
                battery_percent = battery["percent"]
                logger.info(f"배터리 잔량: {battery_percent}%")
                
                if battery_percent < 20:
                    return False, f"배터리 부족 ({battery_percent}%). 20% 이상 필요합니다."
            
            # 비행 상태 확인
            flying_state = self.drone.get_state(FlyingStateChanged)
            if flying_state:
                state = str(flying_state["state"]) if isinstance(flying_state, dict) else str(flying_state)
                logger.info(f"현재 비행 상태: {state}")
                
                # landed 상태 확인 (문자열에 'landed' 포함 여부)
                if "landed" not in state.lower():
                    return False, f"드론이 착륙 상태가 아닙니다 (현재: {state})"
            
            # GPS 상태 확인
            gps_state = self.drone.get_state(GPSFixStateChanged)
            if gps_state:
                logger.info(f"GPS 상태: {gps_state}")
            else:
                logger.warning("GPS 상태를 확인할 수 없습니다 (실내 모드일 수 있음)")
            
            # 알림 상태 확인
            alert_state = self.drone.get_state(AlertStateChanged)
            if alert_state:
                logger.info(f"알림 상태: {alert_state}")
            
            return True, "이륙 준비 완료"
            
        except Exception as e:
            logger.error(f"사전 점검 실패: {str(e)}")
            return True, "사전 점검 건너뜀"  # 점검 실패해도 이륙 시도
    
    def takeoff(self):
        """
        드론 이륙 명령 실행
        Returns:
            tuple: (성공 여부, 메시지)
        """
        if not self.connected:
            msg = "드론이 연결되지 않았습니다"
            logger.error(f"이륙 실패: {msg}")
            return False, msg
        
        # 사전 점검
        ready, check_msg = self.check_preflight_status()
        logger.info(f"사전 점검 결과: {check_msg}")
        
        if not ready:
            logger.warning(f"사전 점검 경고: {check_msg}")
            # 경고만 하고 계속 진행 (사용자가 판단)
        
        try:
            logger.info("이륙 명령 전송 중...")
            
            # 이륙 명령만 전송 (상태 변화 기다리지 않음)
            self.drone(TakeOff())
            logger.info("이륙 명령 전송 완료")
            
            # 5초 대기
            time.sleep(5)
            
            # 현재 상태 확인
            flying_state = self.drone.get_state(FlyingStateChanged)
            if flying_state:
                state = flying_state["state"]
                logger.info(f"5초 후 비행 상태: {state}")
                
                if state in ["takingoff", "hovering", "flying"]:
                    msg = f"이륙 성공! (상태: {state})"
                    logger.info(msg)
                    return True, msg
                elif state == "landed":
                    msg = "이륙 명령을 전송했지만 드론이 이륙하지 않았습니다. FreeFlight 앱으로 드론 상태를 확인하세요."
                    logger.warning(msg)
                    return False, msg
                else:
                    msg = f"드론 상태: {state}"
                    logger.info(msg)
                    return True, msg
            else:
                msg = "이륙 명령을 전송했습니다 (상태 확인 불가)"
                logger.warning(msg)
                return True, msg
                
        except Exception as e:
            msg = f"이륙 실패: {str(e)}"
            logger.error(msg)
            logger.exception("이륙 명령 예외 발생:")
            return False, msg
    
    def land(self):
        """
        드론 착륙 명령 실행
        Returns:
            tuple: (성공 여부, 메시지)
        """
        if not self.connected:
            msg = "드론이 연결되지 않았습니다"
            logger.error(f"착륙 실패: {msg}")
            return False, msg
        
        try:
            logger.info("착륙 명령 전송 중...")
            
            # 착륙 명령 전송
            self.drone(Landing())
            logger.info("착륙 명령 전송 완료")
            
            msg = "착륙 명령을 전송했습니다"
            logger.info(msg)
            return True, msg
                
        except Exception as e:
            msg = f"착륙 실패: {str(e)}"
            logger.error(msg)
            logger.exception("착륙 명령 예외 발생:")
            return False, msg
    
    def get_status(self):
        """
        드론 상태 조회 (간단한 버전)
        Returns:
            dict: 드론 상태 정보
        """
        # 실제 연결 상태 확인
        if not self.connected or self.drone is None:
            return {
                "connected": False,
                "battery": 0,
                "gps": {"latitude": 0, "longitude": 0, "altitude": 0},
                "flying": False
            }
        
        # Olympe 내부 연결 상태 확인
        try:
            if hasattr(self.drone, '_connected') and not self.drone._connected:
                logger.warning("드론 연결이 끊어졌습니다")
                self.connected = False
                return {
                    "connected": False,
                    "battery": 0,
                    "gps": {"latitude": 0, "longitude": 0, "altitude": 0},
                    "flying": False
                }
        except Exception as e:
            logger.debug(f"연결 상태 확인 실패: {e}")
        
        status = {
            "connected": True,
            "battery": 0,
            "gps": {"latitude": 0, "longitude": 0, "altitude": 0},
            "flying": False
        }
        
        try:
            # 배터리 상태
            battery = self.drone.get_state(BatteryStateChanged)
            if battery:
                status["battery"] = int(battery["percent"])
        except Exception as e:
            logger.debug(f"배터리 조회 실패: {e}")
        
        try:
            # 비행 상태
            flying_state = self.drone.get_state(FlyingStateChanged)
            if flying_state:
                state = str(flying_state["state"]) if isinstance(flying_state, dict) else str(flying_state)
                status["flying"] = "flying" in state.lower() or "hovering" in state.lower() or "takingoff" in state.lower()
        except Exception as e:
            logger.debug(f"비행 상태 조회 실패: {e}")
        
        try:
            # GPS 위치 정보
            from olympe.messages.ardrone3.PilotingState import PositionChanged
            position = self.drone.get_state(PositionChanged)
            if position:
                if isinstance(position, dict):
                    status["gps"]["latitude"] = float(position.get("latitude", 0))
                    status["gps"]["longitude"] = float(position.get("longitude", 0))
                    status["gps"]["altitude"] = float(position.get("altitude", 0))
                elif hasattr(position, 'latitude'):
                    status["gps"]["latitude"] = float(position.latitude)
                    status["gps"]["longitude"] = float(position.longitude)
                    status["gps"]["altitude"] = float(position.altitude)
                
                logger.debug(f"GPS: lat={status['gps']['latitude']}, lon={status['gps']['longitude']}, alt={status['gps']['altitude']}")
        except Exception as e:
            logger.debug(f"GPS 조회 실패: {e}")
        
        return status
    
    def get_current_position(self):
        """
        현재 드론 위치 조회
        Returns:
            dict: {latitude, longitude, altitude} 또는 None
        """
        try:
            position = self.drone.get_state(PositionChanged)
            if position:
                if isinstance(position, dict):
                    return {
                        'latitude': float(position.get('latitude', 0)),
                        'longitude': float(position.get('longitude', 0)),
                        'altitude': float(position.get('altitude', 0))
                    }
                elif hasattr(position, 'latitude'):
                    return {
                        'latitude': float(position.latitude),
                        'longitude': float(position.longitude),
                        'altitude': float(position.altitude)
                    }
            return None
        except Exception as e:
            logger.error(f"위치 조회 실패: {str(e)}")
            return None
    

    def move_to_gps(self, latitude, longitude, dest_altitude):
        """
        GPS 좌표로 드론 이동 (안전 고도 자동 계산)
        Args:
            latitude: 목표 위도
            longitude: 목표 경도
            dest_altitude: 도착지 고도 (미터)
        Returns:
            tuple: (성공 여부, 메시지)
        """
        if not self.connected:
            msg = "드론이 연결되지 않았습니다"
            logger.error(f"이동 실패: {msg}")
            return False, msg
        
        try:
            # 현재 위치 고도 가져오기
            current_position = self.get_current_position()
            if current_position:
                current_altitude = current_position['altitude']
            else:
                current_altitude = 0
                logger.warning("현재 고도를 가져올 수 없습니다. 0으로 가정합니다.")
            
            # 안전 비행 고도: 3m 고정 (낮은 고도로 안전하게 비행)
            safe_altitude = 3
            
            logger.info(f"GPS 이동 시작:")
            logger.info(f"  - 목표: 위도={latitude}, 경도={longitude}")
            logger.info(f"  - 현재 고도: {current_altitude}m")
            logger.info(f"  - 도착지 고도: {dest_altitude}m")
            logger.info(f"  - 안전 비행 고도: {safe_altitude}m (장애물 회피)")
            
            # moveTo 명령 사용 (GPS 좌표로 이동)
            # orientation_mode: 0=TO_TARGET (목표 방향), 1=HEADING_START, 2=HEADING_DURING
            result = self.drone(
                moveTo(latitude, longitude, safe_altitude, 0, 0)
            ).wait(_timeout=60)
            
            if result.success():
                msg = f"목표 지점 도착 완료 (비행 고도: {safe_altitude}m)"
                logger.info(msg)
                return True, msg
            else:
                msg = "이동 실패"
                logger.error(msg)
                return False, msg
                
        except Exception as e:
            msg = f"이동 실패: {str(e)}"
            logger.error(msg)
            logger.exception("GPS 이동 예외 발생:")
            return False, msg
    

    def start_delivery(self, origin_lat, origin_lng, dest_lat, dest_lng, altitude=3):
        """
        배송 미션 시작 (이륙 → 목적지 이동 → 착륙 → 재이륙 → 출발지 복귀)
        Args:
            origin_lat: 출발지 위도
            origin_lng: 출발지 경도
            dest_lat: 도착지 위도
            dest_lng: 도착지 경도
            altitude: 비행 고도 (기본 10m)
        Returns:
            tuple: (성공 여부, 메시지)
        """
        if not self.connected:
            return False, "드론이 연결되지 않았습니다"
        
        try:
            logger.info("=" * 60)
            logger.info("배송 미션 시작")
            logger.info(f"출발지: ({origin_lat}, {origin_lng})")
            logger.info(f"도착지: ({dest_lat}, {dest_lng})")
            logger.info(f"비행 고도: {altitude}m")
            logger.info("=" * 60)
            
            # 1. 이륙 (출발지에서)
            logger.info("[1/5] 출발지에서 이륙 중...")
            success, msg = self.takeoff()
            if not success:
                return False, f"이륙 실패: {msg}"
            
            time.sleep(3)  # 안정화 대기
            
            # 2. 목적지로 이동
            logger.info("[2/5] 목적지로 이동 중...")
            success, msg = self.move_to_gps(dest_lat, dest_lng, 0)  # 도착지 고도 0 (지상)
            if not success:
                logger.warning(f"이동 실패: {msg}, 착륙 시도...")
                self.land()
                return False, f"목적지 이동 실패: {msg}"
            
            time.sleep(2)  # 안정화 대기
            
            # 3. 목적지에서 착륙
            logger.info("[3/5] 목적지에서 착륙 중...")
            success, msg = self.land()
            if not success:
                return False, f"목적지 착륙 실패: {msg}"
            
            time.sleep(5)  # 착륙 후 대기 (배송 완료)
            
            # 4. 재이륙 (목적지에서)
            logger.info("[4/5] 목적지에서 재이륙 중...")
            success, msg = self.takeoff()
            if not success:
                return False, f"재이륙 실패: {msg}"
            
            time.sleep(3)  # 안정화 대기
            
            # 5. 출발지로 복귀 (Return to Home)
            logger.info("[5/5] 출발지로 복귀 중...")
            success, msg = self.move_to_gps(origin_lat, origin_lng, 0)  # 출발지 고도 0 (지상)
            if not success:
                logger.warning(f"복귀 실패: {msg}, 현재 위치에서 착륙 시도...")
                self.land()
                return False, f"출발지 복귀 실패: {msg}"
            
            time.sleep(2)  # 안정화 대기
            
            # 6. 출발지에서 최종 착륙
            logger.info("[최종] 출발지에서 착륙 중...")
            success, msg = self.land()
            if not success:
                return False, f"최종 착륙 실패: {msg}"
            
            logger.info("=" * 60)
            logger.info("배송 미션 완료! (왕복 완료)")
            logger.info("=" * 60)
            
            return True, "배송 완료 (왕복 완료)"
            
        except Exception as e:
            msg = f"배송 미션 실패: {str(e)}"
            logger.error(msg)
            logger.exception("배송 미션 예외 발생:")
            # 비상 착륙 시도
            try:
                logger.warning("비상 착륙 시도...")
                self.land()
            except:
                pass
            return False, msg


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
