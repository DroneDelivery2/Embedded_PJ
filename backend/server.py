from flask import Flask, jsonify
from flask_cors import CORS
import logging
from drone_controller import DroneController

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask 애플리케이션 생성
app = Flask(__name__)

# CORS 설정 - Next.js PWA origin 허용
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000"
        ]
    }
})

# 드론 컨트롤러 인스턴스 (전역)
drone_controller = None


# 기본 라우트
@app.route('/')
def index():
    return jsonify({
        "message": "Parrot ANAFI Flask 브리지 서버",
        "status": "running"
    })


# 상태 조회 엔드포인트
@app.route('/api/status', methods=['GET'])
def get_status():
    """드론 연결 상태 조회"""
    logger.info("상태 조회 요청 수신")
    
    if drone_controller is None:
        return jsonify({
            "connected": False,
            "message": "드론 컨트롤러가 초기화되지 않았습니다"
        })
    
    connected = drone_controller.is_connected()
    message = "드론이 연결되었습니다" if connected else "드론이 연결되지 않았습니다"
    
    logger.info(f"상태 응답: connected={connected}")
    
    return jsonify({
        "connected": connected,
        "message": message
    })


# 이륙 명령 엔드포인트
@app.route('/api/takeoff', methods=['POST'])
def takeoff():
    """드론 이륙 명령"""
    logger.info("이륙 명령 요청 수신")
    
    if drone_controller is None:
        logger.error("드론 컨트롤러가 초기화되지 않았습니다")
        return jsonify({
            "success": False,
            "message": "드론 컨트롤러가 초기화되지 않았습니다"
        }), 500
    
    success, message = drone_controller.takeoff()
    
    if success:
        logger.info(f"이륙 성공: {message}")
        return jsonify({
            "success": True,
            "message": message
        }), 200
    else:
        logger.error(f"이륙 실패: {message}")
        return jsonify({
            "success": False,
            "message": message
        }), 500


# 착륙 명령 엔드포인트
@app.route('/api/land', methods=['POST'])
def land():
    """드론 착륙 명령"""
    logger.info("착륙 명령 요청 수신")
    
    if drone_controller is None:
        logger.error("드론 컨트롤러가 초기화되지 않았습니다")
        return jsonify({
            "success": False,
            "message": "드론 컨트롤러가 초기화되지 않았습니다"
        }), 500
    
    success, message = drone_controller.land()
    
    if success:
        logger.info(f"착륙 성공: {message}")
        return jsonify({
            "success": True,
            "message": message
        }), 200
    else:
        logger.error(f"착륙 실패: {message}")
        return jsonify({
            "success": False,
            "message": message
        }), 500


def initialize_drone():
    """드론 컨트롤러 초기화 및 연결"""
    global drone_controller
    
    try:
        logger.info("드론 컨트롤러 초기화 중...")
        drone_controller = DroneController()
        
        logger.info("드론 연결 시도 중...")
        if drone_controller.connect():
            logger.info("드론 연결 성공")
        else:
            logger.warning("드론 연결 실패 - 수동으로 재연결 필요")
            
    except Exception as e:
        logger.error(f"드론 초기화 실패: {str(e)}")
        drone_controller = DroneController()  # 연결 실패해도 컨트롤러는 생성


def cleanup_drone():
    """드론 연결 해제"""
    global drone_controller
    
    if drone_controller is not None:
        logger.info("드론 연결 해제 중...")
        drone_controller.disconnect()
        logger.info("드론 연결 해제 완료")


if __name__ == '__main__':
    import signal
    import sys
    
    # 시그널 핸들러 등록 (Ctrl+C 처리)
    def signal_handler(sig, frame):
        logger.info("\n서버 종료 신호 수신...")
        cleanup_drone()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # 드론 초기화
    initialize_drone()
    
    # Flask 서버 시작
    logger.info("Flask 브리지 서버 시작 중...")
    logger.info("서버 주소: http://0.0.0.0:5000")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    finally:
        cleanup_drone()
