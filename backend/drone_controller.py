#!/usr/bin/env python3
"""
Parrot Anafi 드론 제어 모듈
Olympe SDK를 사용한 드론 연결 및 제어
공식 문서: https://developer.parrot.com/docs/olympe/
"""

import olympe
from olympe.messages.ardrone3.Piloting import TakeOff, Landing, moveBy
from olympe.messages.ardrone3.PilotingState import FlyingStateChanged, PositionChanged, AttitudeChanged
from olympe.messages.common.CommonState import BatteryStateChanged
from olympe.messages.common.Common import AllStates
from olympe.messages.ardrone3.GPSSettingsState import GPSFixStateChanged
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
        # 상태 캐시
        self.cached_status = {
            "connected": False,
            "battery": 0,
            "gps": {"latitude": 0, "longitude": 0, "altitude": 0},
            "flying": False
        }
        self.last_status_update = 0
        
    def connect(self):
        """드론 연결 (Olympe 공식 방식)"""
        try:
            logger.info(f"드론 연결 시도: {self.drone_ip}")
            
            # 기존 연결 정리
            if self.drone is not None:
                try:
                    if self.is_connected:
                        self.drone.disconnect()
                except Exception as e:
                    logger.debug(f"기존 연결 정리 중 에러 (무시): {e}")
                self.drone = None
            
            # 드론 인스턴스 생성
            self.drone = olympe.Drone(self.drone_ip)
            
            # 연결 시도 (공식 문서 방식)
            assert self.drone.connect(retry=3)
            
            self.is_connected = True
            logger.info("✅ 드론 연결 성공!")
            
            # 상태 초기화 대기
            logger.info("⏳ 드론 상태 초기화 대기 중...")
            time.sleep(3)
            
            # 모든 상태 요청 (중요!)
            try:
                logger.info("📡 드론에 상태 정보 요청 중...")
                self.drone(AllStates()).wait(_timeout=10)
                logger.info("✅ AllStates 명령 전송 완료")
                time.sleep(3)  # 상태 수신 대기 (증가)
            except Exception as e:
                logger.error(f"❌ AllStates 실패: {e}")
            
            # 초기 상태 캐시 업데이트
            logger.info("🔍 초기 상태 캐시 업데이트 중...")
            self._update_cached_status()
            
            if self.cached_status["battery"] > 0:
                logger.info(f"✅ 초기 배터리: {self.cached_status['battery']}%")
            else:
                logger.warning("⚠️ 배터리 정보를 가져오지 못했습니다")
            
            return True
            
        except AssertionError:
            logger.error("❌ 드론 연결 실패: 연결 타임아웃")
            self.is_connected = False
            return False
        except Exception as e:
            logger.error(f"❌ 드론 연결 실패: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """드론 연결 해제 (Olympe 공식 방식)"""
        if self.drone is not None:
            try:
                self.drone.disconnect()
                logger.info("드론 연결 해제")
            except Exception as e:
                logger.error(f"연결 해제 중 에러: {e}")
            finally:
                self.is_connected = False
                self.drone = None
    
    def _update_cached_status(self):
        """내부 메서드: 캐시된 상태 업데이트"""
        if not self.is_connected or self.drone is None:
            return
        
        # 배터리 상태
        try:
            battery_state = self.drone.get_state(BatteryStateChanged)
            if battery_state is not None:
                if isinstance(battery_state, dict) and "percent" in battery_state:
                    self.cached_status["battery"] = int(battery_state["percent"])
                elif hasattr(battery_state, 'percent'):
                    self.cached_status["battery"] = int(battery_state.percent)
        except Exception as e:
            logger.debug(f"배터리 캐시 업데이트 실패: {e}")
        
        # GPS 위치
        try:
            position_state = self.drone.get_state(PositionChanged)
            if position_state is not None:
                if isinstance(position_state, dict):
                    self.cached_status["gps"]["latitude"] = float(position_state.get("latitude", 0))
                    self.cached_status["gps"]["longitude"] = float(position_state.get("longitude", 0))
                    self.cached_status["gps"]["altitude"] = float(position_state.get("altitude", 0))
                elif hasattr(position_state, 'latitude'):
                    self.cached_status["gps"]["latitude"] = float(position_state.latitude)
                    self.cached_status["gps"]["longitude"] = float(position_state.longitude)
                    self.cached_status["gps"]["altitude"] = float(position_state.altitude)
        except Exception as e:
            logger.debug(f"GPS 캐시 업데이트 실패: {e}")
        
        # 비행 상태
        try:
            flying_state = self.drone.get_state(FlyingStateChanged)
            if flying_state is not None:
                state_value = None
                if isinstance(flying_state, dict) and "state" in flying_state:
                    state_value = flying_state["state"]
                elif hasattr(flying_state, 'state'):
                    state_value = flying_state.state
                
                if state_value:
                    self.cached_status["flying"] = state_value in ["flying", "hovering", "takingoff"]
        except Exception as e:
            logger.debug(f"비행 상태 캐시 업데이트 실패: {e}")
        
        self.cached_status["connected"] = True
        self.last_status_update = time.time()
    
    def get_status(self):
        """드론 상태 조회 (캐시 사용)"""
        if not self.is_connected or self.drone is None:
            logger.debug("드론 연결 안됨")
            return {
                "connected": False,
                "battery": 0,
                "gps": {"latitude": 0, "longitude": 0, "altitude": 0},
                "flying": False
            }
        
        # 캐시가 너무 오래되었거나 (2초 이상) 처음 조회인 경우 갱신
        current_time = time.time()
        if current_time - self.last_status_update > 2:
            logger.debug("📡 상태 갱신 중...")
            
            # AllStates 요청 (선택적)
            try:
                self.drone(AllStates()).wait(_timeout=3)
                time.sleep(0.3)
            except Exception as e:
                logger.debug(f"AllStates 실패 (무시): {e}")
            
            # 캐시 업데이트
            self._update_cached_status()
        
        logger.info(f"📊 상태 반환: 배터리={self.cached_status['battery']}%, GPS=({self.cached_status['gps']['latitude']:.6f}, {self.cached_status['gps']['longitude']:.6f}), 비행={self.cached_status['flying']}")
        
        # 캐시 복사본 반환
        return {
            "connected": self.cached_status["connected"],
            "battery": self.cached_status["battery"],
            "gps": {
                "latitude": self.cached_status["gps"]["latitude"],
                "longitude": self.cached_status["gps"]["longitude"],
                "altitude": self.cached_status["gps"]["altitude"]
            },
            "flying": self.cached_status["flying"]
        }
    
    def takeoff(self):
        """이륙 (Olympe 공식 방식)"""
        if not self.is_connected or self.drone is None:
            logger.error("드론이 연결되지 않음")
            return False
        
        try:
            logger.info("🚁 이륙 시작...")
            
            # Olympe 공식 방식: assert를 사용한 명령 전송 및 대기
            assert self.drone(
                TakeOff()
                >> FlyingStateChanged(state="hovering", _timeout=10)
            ).wait().success()
            
            logger.info("✅ 이륙 완료!")
            return True
            
        except AssertionError:
            logger.error("❌ 이륙 실패: 타임아웃 또는 명령 실패")
            return False
        except Exception as e:
            logger.error(f"❌ 이륙 실패: {e}")
            return False
    
    def land(self):
        """착륙 (Olympe 공식 방식)"""
        if not self.is_connected or self.drone is None:
            logger.error("드론이 연결되지 않음")
            return False
        
        try:
            logger.info("🛬 착륙 시작...")
            
            # Olympe 공식 방식: assert를 사용한 명령 전송 및 대기
            assert self.drone(
                Landing()
                >> FlyingStateChanged(state="landed", _timeout=10)
            ).wait().success()
            
            logger.info("✅ 착륙 완료!")
            return True
            
        except AssertionError:
            logger.error("❌ 착륙 실패: 타임아웃 또는 명령 실패")
            return False
        except Exception as e:
            logger.error(f"❌ 착륙 실패: {e}")
            return False
    
    def move_by(self, dx, dy, dz, dyaw):
        """
        상대 위치로 이동 (Olympe 공식 방식)
        :param dx: 전진/후진 (미터, 양수=전진)
        :param dy: 좌/우 (미터, 양수=오른쪽)
        :param dz: 상승/하강 (미터, 양수=상승)
        :param dyaw: 회전 (라디안, 양수=시계방향)
        """
        if not self.is_connected or self.drone is None:
            logger.error("드론이 연결되지 않음")
            return False
        
        try:
            logger.info(f"📍 상대 이동: dx={dx}m, dy={dy}m, dz={dz}m, dyaw={dyaw}rad")
            
            # Olympe 공식 방식: moveBy 사용
            assert self.drone(
                moveBy(dx, dy, dz, dyaw)
                >> FlyingStateChanged(state="hovering", _timeout=10)
            ).wait().success()
            
            logger.info("✅ 이동 완료!")
            return True
            
        except AssertionError:
            logger.error("❌ 이동 실패: 타임아웃 또는 명령 실패")
            return False
        except Exception as e:
            logger.error(f"❌ 이동 실패: {e}")
            return False
    
    def start_mission(self, waypoints):
        """
        미션 시작 (간단한 데모)
        :param waypoints: [{"lat": float, "lng": float, "alt": float}, ...]
        """
        if not self.is_connected or self.drone is None:
            logger.error("드론이 연결되지 않음")
            return False
        
        try:
            logger.info("🚀 미션 시작!")
            
            # 이륙
            if not self.takeoff():
                return False
            
            time.sleep(2)  # 안정화 대기
            
            # 간단한 이동 데모 (상대 좌표)
            logger.info("📍 전진 5m")
            self.move_by(5, 0, 0, 0)
            time.sleep(2)
            
            logger.info("📍 우측 3m")
            self.move_by(0, 3, 0, 0)
            time.sleep(2)
            
            logger.info("📍 상승 2m")
            self.move_by(0, 0, 2, 0)
            time.sleep(2)
            
            # 착륙
            self.land()
            
            logger.info("✅ 미션 완료!")
            return True
            
        except Exception as e:
            logger.error(f"❌ 미션 실패: {e}")
            # 비상 착륙 시도
            try:
                self.land()
            except:
                pass
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
