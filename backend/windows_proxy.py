#!/usr/bin/env python3
"""
Windows 프록시 서버
Windows에서 실행되어 드론과 직접 통신
WSL2의 백엔드 서버와 HTTP로 통신
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import olympe
from olympe.messages.ardrone3.Piloting import TakeOff, Landing, moveBy
from olympe.messages.ardrone3.PilotingState import FlyingStateChanged, PositionChanged
from olympe.messages.common.CommonState import BatteryStateChanged
import logging
import time

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 드론 인스턴스
drone = None
is_connected = False
drone_ip = "192.168.42.1"


@app.route('/health', methods=['GET'])
def health():
    """헬스 체크"""
    return jsonify({'status': 'ok', 'connected': is_connected})


@app.route('/connect', methods=['POST'])
def connect():
    """드론 연결"""
    global drone, is_connected, drone_ip
    
    try:
        data = request.json or {}
        drone_ip = data.get('ip', '192.168.42.1')
        
        logger.info(f"드론 연결 시도: {drone_ip}")
        
        # 기존 연결 정리
        if drone is not None:
            try:
                if is_connected:
                    drone.disconnect()
            except:
                pass
            drone = None
        
        # 새 드론 인스턴스
        drone = olympe.Drone(drone_ip)
        
        # 연결
        assert drone.connect(retry=3)
        
        is_connected = True
        logger.info("✅ 드론 연결 성공!")
        
        return jsonify({
            'success': True,
            'message': '드론 연결 성공'
        })
        
    except AssertionError:
        logger.error("❌ 드론 연결 실패: 타임아웃")
        is_connected = False
        return jsonify({
            'success': False,
            'message': '드론 연결 실패: 타임아웃'
        }), 500
        
    except Exception as e:
        logger.error(f"❌ 드론 연결 실패: {e}")
        is_connected = False
        return jsonify({
            'success': False,
            'message': f'드론 연결 실패: {str(e)}'
        }), 500


@app.route('/disconnect', methods=['POST'])
def disconnect():
    """드론 연결 해제"""
    global drone, is_connected
    
    try:
        if drone is not None:
            drone.disconnect()
            logger.info("드론 연결 해제")
        
        is_connected = False
        drone = None
        
        return jsonify({
            'success': True,
            'message': '드론 연결 해제'
        })
        
    except Exception as e:
        logger.error(f"연결 해제 오류: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/status', methods=['GET'])
def get_status():
    """드론 상태 조회"""
    global drone, is_connected
    
    if not is_connected or drone is None:
        return jsonify({
            'connected': False,
            'battery': 0,
            'gps': {'latitude': 0, 'longitude': 0, 'altitude': 0},
            'flying': False
        })
    
    try:
        status = {
            'connected': True,
            'battery': 0,
            'gps': {'latitude': 0, 'longitude': 0, 'altitude': 0},
            'flying': False
        }
        
        # 배터리
        battery_state = drone.get_state(BatteryStateChanged)
        if battery_state is not None:
            status['battery'] = int(battery_state['percent'])
        
        # GPS
        position_state = drone.get_state(PositionChanged)
        if position_state is not None:
            status['gps']['latitude'] = float(position_state['latitude'])
            status['gps']['longitude'] = float(position_state['longitude'])
            status['gps']['altitude'] = float(position_state['altitude'])
        
        # 비행 상태
        flying_state = drone.get_state(FlyingStateChanged)
        if flying_state is not None:
            state_value = flying_state['state']
            status['flying'] = state_value in ['flying', 'hovering', 'takingoff']
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"상태 조회 실패: {e}")
        return jsonify({
            'connected': True,
            'battery': 0,
            'gps': {'latitude': 0, 'longitude': 0, 'altitude': 0},
            'flying': False
        })


@app.route('/takeoff', methods=['POST'])
def takeoff():
    """이륙"""
    global drone, is_connected
    
    if not is_connected or drone is None:
        return jsonify({
            'success': False,
            'message': '드론이 연결되지 않음'
        }), 400
    
    try:
        logger.info("🚁 이륙 시작...")
        
        assert drone(
            TakeOff()
            >> FlyingStateChanged(state="hovering", _timeout=10)
        ).wait().success()
        
        logger.info("✅ 이륙 완료!")
        
        return jsonify({
            'success': True,
            'message': '이륙 성공'
        })
        
    except AssertionError:
        logger.error("❌ 이륙 실패: 타임아웃")
        return jsonify({
            'success': False,
            'message': '이륙 실패: 타임아웃'
        }), 500
        
    except Exception as e:
        logger.error(f"❌ 이륙 실패: {e}")
        return jsonify({
            'success': False,
            'message': f'이륙 실패: {str(e)}'
        }), 500


@app.route('/land', methods=['POST'])
def land():
    """착륙"""
    global drone, is_connected
    
    if not is_connected or drone is None:
        return jsonify({
            'success': False,
            'message': '드론이 연결되지 않음'
        }), 400
    
    try:
        logger.info("🛬 착륙 시작...")
        
        assert drone(
            Landing()
            >> FlyingStateChanged(state="landed", _timeout=10)
        ).wait().success()
        
        logger.info("✅ 착륙 완료!")
        
        return jsonify({
            'success': True,
            'message': '착륙 성공'
        })
        
    except AssertionError:
        logger.error("❌ 착륙 실패: 타임아웃")
        return jsonify({
            'success': False,
            'message': '착륙 실패: 타임아웃'
        }), 500
        
    except Exception as e:
        logger.error(f"❌ 착륙 실패: {e}")
        return jsonify({
            'success': False,
            'message': f'착륙 실패: {str(e)}'
        }), 500


@app.route('/move', methods=['POST'])
def move():
    """상대 이동"""
    global drone, is_connected
    
    if not is_connected or drone is None:
        return jsonify({
            'success': False,
            'message': '드론이 연결되지 않음'
        }), 400
    
    try:
        data = request.json
        dx = data.get('dx', 0)
        dy = data.get('dy', 0)
        dz = data.get('dz', 0)
        dyaw = data.get('dyaw', 0)
        
        logger.info(f"📍 이동: dx={dx}, dy={dy}, dz={dz}, dyaw={dyaw}")
        
        assert drone(
            moveBy(dx, dy, dz, dyaw)
            >> FlyingStateChanged(state="hovering", _timeout=10)
        ).wait().success()
        
        logger.info("✅ 이동 완료!")
        
        return jsonify({
            'success': True,
            'message': '이동 성공'
        })
        
    except AssertionError:
        logger.error("❌ 이동 실패: 타임아웃")
        return jsonify({
            'success': False,
            'message': '이동 실패: 타임아웃'
        }), 500
        
    except Exception as e:
        logger.error(f"❌ 이동 실패: {e}")
        return jsonify({
            'success': False,
            'message': f'이동 실패: {str(e)}'
        }), 500


if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("Windows 프록시 서버 시작")
    logger.info("포트: 5001")
    logger.info("드론 IP: 192.168.42.1")
    logger.info("=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=False)
