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
            
            # 상태 안정화 대기
            time.sleep(1)
            
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
    
    def get_status(self):
        """드론 상태 조회 (Olympe 공식 방식)"""
        if not self.is_connected or self.drone is None:
            return {
                "connected": False,
                "battery": 0,
                "gps": {"latitude": 0, "longitude": 0, "altitude": 0},
                "flying": False
            }
        
        try:
            status = {
                "connected": True,
                "battery": 0,
                "gps": {"latitude": 0, "longitude": 0, "altitude": 0},
                "flying": False
            }
            
            # 배터리 상태 (Olympe 공식 방식)
            battery_state = self.drone.get_state(BatteryStateChanged)
            if battery_state is not None:
                status["battery"] = int(battery_state["percent"])
            
            # GPS 위치 (Olympe 공식 방식)
            position_state = self.drone.get_state(PositionChanged)
            if position_state is not None:
                status["gps"]["latitude"] = float(position_state["latitude"])
                status["gps"]["longitude"] = float(position_state["longitude"])
                status["gps"]["altitude"] = float(position_state["altitude"])
            
            # 비행 상태 (Olympe 공식 방식)
            flying_state = self.drone.get_state(FlyingStateChanged)
            if flying_state is not None:
                # FlyingStateChanged의 state 값: landed, takingoff, hovering, flying, landing, emergency
                state_value = flying_state["state"]
                status["flying"] = state_value in ["flying", "hovering", "takingoff"]
            
            return status
            
        except Exception as e:
            logger.error(f"상태 조회 실패: {e}")
            return {
                "connected": True,
                "battery": 0,
                "gps": {"latitude": 0, "longitude": 0, "altitude": 0},
                "flying": False
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
