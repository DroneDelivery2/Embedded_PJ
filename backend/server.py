#!/usr/bin/env python3
"""
드론 제어 REST API 서버
Flask를 사용한 백엔드 서버
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from drone_controller import DroneController
import logging

app = Flask(__name__)

# CORS 설정 - 모든 origin 허용
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 드론 컨트롤러 인스턴스
drone = DroneController()


@app.route('/api/drone/connect', methods=['POST'])
def connect_drone():
    """드론 연결"""
    try:
        data = request.json or {}
        drone_ip = data.get('ip', '192.168.42.1')
        
        logger.info(f"🔌 드론 연결 요청: {drone_ip}")
        
        # 드론 IP 설정
        drone.drone_ip = drone_ip
        
        # 연결 시도
        success = drone.connect()
        
        if success:
            # 연결 성공 후 상태 정보 가져오기
            status = drone.get_status()
            logger.info(f"✅ 드론 연결 성공! 배터리: {status.get('battery', 0)}%")
            
            return jsonify({
                'success': True,
                'message': '드론 연결 성공',
                'status': status  # 초기 상태 정보 포함
            })
        else:
            logger.error("❌ 드론 연결 실패")
            return jsonify({
                'success': False,
                'message': '드론 연결 실패 - 드론 WiFi 연결을 확인하세요'
            })
            
    except Exception as e:
        logger.error(f"❌ 연결 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'연결 오류: {str(e)}'
        }), 500


@app.route('/api/drone/disconnect', methods=['POST'])
def disconnect_drone():
    """드론 연결 해제"""
    try:
        drone.disconnect()
        return jsonify({'success': True, 'message': '드론 연결 해제'})
    except Exception as e:
        logger.error(f"연결 해제 오류: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/drone/status', methods=['GET'])
def get_status():
    """드론 상태 조회 (캐시된 값 반환)"""
    try:
        status = drone.get_status()
        if status:
            return jsonify(status)
        else:
            return jsonify({
                'connected': False,
                'battery': 0,
                'gps': {'latitude': 0, 'longitude': 0, 'altitude': 0},
                'flying': False
            })
    except Exception as e:
        logger.error(f"상태 조회 오류: {e}")
        return jsonify({
            'connected': False,
            'battery': 0,
            'gps': {'latitude': 0, 'longitude': 0, 'altitude': 0},
            'flying': False,
            'error': str(e)
        }), 500


@app.route('/api/drone/status/refresh', methods=['POST'])
def refresh_status():
    """드론 상태 수동 갱신"""
    try:
        logger.info("🔄 수동 상태 갱신 요청")
        
        # 상태 조회 (get_status가 최신 상태를 가져옴)
        status = drone.get_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"상태 갱신 오류: {e}")
        return jsonify({
            'connected': False,
            'battery': 0,
            'gps': {'latitude': 0, 'longitude': 0, 'altitude': 0},
            'flying': False,
            'error': str(e)
        }), 500


@app.route('/api/drone/takeoff', methods=['POST'])
def takeoff():
    """이륙"""
    try:
        logger.info("🚁 이륙 명령 실행...")
        success, message = drone.takeoff()
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        logger.error(f"❌ 이륙 오류: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/drone/land', methods=['POST'])
def land():
    """착륙"""
    try:
        logger.info("🛬 착륙 명령 실행...")
        success, message = drone.land()
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        logger.error(f"❌ 착륙 오류: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500





@app.route('/api/drone/move-gps', methods=['POST'])
def move_to_gps():
    """GPS 좌표로 이동 (안전 고도 자동 계산)"""
    try:
        data = request.json or {}
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        dest_altitude = data.get('altitude', 0)  # 도착지 고도 (기본값 0)
        
        if latitude is None or longitude is None:
            return jsonify({
                'success': False,
                'message': '위도와 경도를 입력하세요'
            }), 400
        
        logger.info(f"📍 GPS 이동 명령: 위도={latitude}, 경도={longitude}, 도착지 고도={dest_altitude}m")
        
        success, message = drone.move_to_gps(latitude, longitude, dest_altitude)
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        logger.error(f"❌ GPS 이동 오류: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/drone/mission', methods=['POST'])
def start_mission():
    """미션 시작"""
    try:
        data = request.json or {}
        waypoints = data.get('waypoints', [])
        
        # 현재 상태 확인
        current_status = drone.get_status()
        if not current_status.get('connected'):
            return jsonify({
                'success': False,
                'message': '드론이 연결되지 않았습니다'
            }), 400
        
        if current_status.get('flying'):
            return jsonify({
                'success': False,
                'message': '드론이 이미 비행 중입니다. 먼저 착륙하세요.'
            }), 400
        
        if not waypoints:
            logger.info("🚀 간단한 데모 미션 시작...")
        else:
            logger.info(f"🚀 미션 시작: {len(waypoints)}개 웨이포인트")
        
        success = drone.start_mission(waypoints)
        
        return jsonify({
            'success': success,
            'message': '미션 완료' if success else '미션 실패',
            'status': drone.get_status()  # 최신 상태 반환
        })
    except Exception as e:
        logger.error(f"❌ 미션 오류: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크 (드론 연결 상태 포함)"""
    drone_status = drone.get_status()
    return jsonify({
        'status': 'ok',
        'drone_connected': drone_status.get('connected', False),
        'drone_battery': drone_status.get('battery', 0)
    })


# 실내 배송 테스트 엔드포인트
# 실외 배송 시작 엔드포인트 (GPS)
@app.route('/api/delivery/start', methods=['POST', 'OPTIONS'])
def start_delivery():
    """실외 배송 미션 시작 (GPS 좌표)"""
    # OPTIONS 요청 처리 (CORS preflight)
    if request.method == 'OPTIONS':
        return '', 200
    
    logger.info("실외 배송 시작 요청 수신")
    
    try:
        data = request.json or {}
        origin_lat = data.get('origin_lat')
        origin_lng = data.get('origin_lng')
        dest_lat = data.get('dest_lat')
        dest_lng = data.get('dest_lng')
        altitude = data.get('altitude', 3)  # 기본 고도 3m
        
        if not all([origin_lat, origin_lng, dest_lat, dest_lng]):
            return jsonify({
                'success': False,
                'message': '출발지와 도착지 좌표가 필요합니다'
            }), 400
        
        logger.info(f"실외 배송 시작: ({origin_lat}, {origin_lng}) → ({dest_lat}, {dest_lng})")
        
        success, message = drone.start_delivery(
            origin_lat, origin_lng, dest_lat, dest_lng, altitude
        )
        
        return jsonify({
            'success': success,
            'message': message
        })
            
    except Exception as e:
        logger.error(f"실외 배송 시작 오류: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


if __name__ == '__main__':
    logger.info("드론 제어 서버 시작...")
    app.run(host='0.0.0.0', port=5000, debug=True)
