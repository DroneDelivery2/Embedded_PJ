#!/usr/bin/env python3
"""
드론 제어 REST API 서버
Flask를 사용한 백엔드 서버
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os

# 프록시 모드 확인
USE_PROXY = os.getenv('USE_PROXY', 'false').lower() == 'true'

if USE_PROXY:
    from drone_controller_proxy import DroneController
    logger = logging.getLogger(__name__)
    logger.info("🔄 프록시 모드로 실행 (Windows 프록시 사용)")
else:
    from drone_controller import DroneController
    logger = logging.getLogger(__name__)
    logger.info("🚁 직접 모드로 실행 (Olympe SDK)")

app = Flask(__name__)
CORS(app)  # CORS 허용

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
        
        logger.info(f"드론 연결 요청: {drone_ip}")
        
        # 드론 IP 설정
        drone.drone_ip = drone_ip
        
        # 연결 시도
        success = drone.connect()
        
        if success:
            logger.info("드론 연결 성공!")
            return jsonify({
                'success': True,
                'message': '드론 연결 성공'
            })
        else:
            logger.error("드론 연결 실패")
            return jsonify({
                'success': False,
                'message': '드론 연결 실패 - 드론 WiFi 연결을 확인하세요'
            })
            
    except Exception as e:
        logger.error(f"연결 오류: {e}")
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
    """드론 상태 조회"""
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


@app.route('/api/drone/takeoff', methods=['POST'])
def takeoff():
    """이륙"""
    try:
        success = drone.takeoff()
        return jsonify({
            'success': success,
            'message': '이륙 성공' if success else '이륙 실패'
        })
    except Exception as e:
        logger.error(f"이륙 오류: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/drone/land', methods=['POST'])
def land():
    """착륙"""
    try:
        success = drone.land()
        return jsonify({
            'success': success,
            'message': '착륙 성공' if success else '착륙 실패'
        })
    except Exception as e:
        logger.error(f"착륙 오류: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/drone/move', methods=['POST'])
def move_to():
    """지정 위치로 이동"""
    try:
        data = request.json
        lat = data.get('latitude')
        lng = data.get('longitude')
        alt = data.get('altitude', 10)
        
        if lat is None or lng is None:
            return jsonify({'success': False, 'message': '위도/경도 필요'}), 400
        
        success = drone.move_to(lat, lng, alt)
        return jsonify({
            'success': success,
            'message': '이동 성공' if success else '이동 실패'
        })
    except Exception as e:
        logger.error(f"이동 오류: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/drone/mission', methods=['POST'])
def start_mission():
    """미션 시작"""
    try:
        data = request.json
        waypoints = data.get('waypoints', [])
        
        if not waypoints:
            return jsonify({'success': False, 'message': '웨이포인트 필요'}), 400
        
        success = drone.start_mission(waypoints)
        return jsonify({
            'success': success,
            'message': '미션 완료' if success else '미션 실패'
        })
    except Exception as e:
        logger.error(f"미션 오류: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    logger.info("드론 제어 서버 시작...")
    app.run(host='0.0.0.0', port=5000, debug=True)
