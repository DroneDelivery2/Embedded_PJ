#!/usr/bin/env python3
"""
SMS 큐 관리 모듈
드론 WiFi 연결 시 인터넷이 안되므로 SMS를 큐에 저장하고 나중에 전송
"""

import json
import os
import time
import logging

logger = logging.getLogger(__name__)

SMS_QUEUE_FILE = 'sms_queue.json'


def queue_sms(phone, message):
    """
    SMS를 큐에 저장
    Args:
        phone: 수신자 전화번호
        message: 메시지 내용
    """
    try:
        # 기존 큐 읽기
        if os.path.exists(SMS_QUEUE_FILE):
            with open(SMS_QUEUE_FILE, 'r', encoding='utf-8') as f:
                queue = json.load(f)
        else:
            queue = []
        
        # 새 SMS 추가
        sms_data = {
            'phone': phone,
            'message': message,
            'timestamp': time.time(),
            'status': 'pending'
        }
        queue.append(sms_data)
        
        # 큐 저장
        with open(SMS_QUEUE_FILE, 'w', encoding='utf-8') as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📱 SMS 큐에 저장: {phone} - {message}")
        return True
        
    except Exception as e:
        logger.error(f"❌ SMS 큐 저장 실패: {e}")
        return False


def send_ncp_sms(phone, message):
    """
    NCP SENS를 사용한 SMS 전송 (실제 구현은 주석 처리)
    Args:
        phone: 수신자 전화번호
        message: 메시지 내용
    Returns:
        bool: 전송 성공 여부
    """
    # TODO: NCP SENS API 실제 구현
    # import hashlib
    # import hmac
    # import base64
    # import requests
    # 
    # service_id = 'your_service_id'
    # access_key = 'your_access_key'
    # secret_key = 'your_secret_key'
    # 
    # timestamp = str(int(time.time() * 1000))
    # 
    # # 서명 생성
    # message_to_sign = f"POST /sms/v2/services/{service_id}/messages\n{timestamp}\n{access_key}"
    # signature = base64.b64encode(
    #     hmac.new(secret_key.encode(), message_to_sign.encode(), hashlib.sha256).digest()
    # ).decode()
    # 
    # # API 호출
    # url = f"https://sens.apigw.ntruss.com/sms/v2/services/{service_id}/messages"
    # headers = {
    #     'Content-Type': 'application/json',
    #     'x-ncp-apigw-timestamp': timestamp,
    #     'x-ncp-iam-access-key': access_key,
    #     'x-ncp-apigw-signature-v2': signature
    # }
    # 
    # data = {
    #     'type': 'SMS',
    #     'from': '01012345678',  # 발신번호
    #     'content': message,
    #     'messages': [{'to': phone}]
    # }
    # 
    # response = requests.post(url, headers=headers, json=data)
    # return response.status_code == 202
    
    logger.info(f"📱 [주석처리] NCP SMS 전송: {phone} - {message}")
    return True


def send_queued_sms():
    """
    큐에 있는 SMS 전송 (인터넷 연결 시 호출)
    Returns:
        tuple: (전송 성공 개수, 전송 실패 개수)
    """
    if not os.path.exists(SMS_QUEUE_FILE):
        logger.info("전송할 SMS가 없습니다")
        return 0, 0
    
    try:
        with open(SMS_QUEUE_FILE, 'r', encoding='utf-8') as f:
            queue = json.load(f)
        
        if not queue:
            logger.info("전송할 SMS가 없습니다")
            return 0, 0
        
        success_count = 0
        fail_count = 0
        remaining_queue = []
        
        for sms in queue:
            if sms['status'] == 'pending':
                try:
                    # NCP SMS 전송 시도
                    if send_ncp_sms(sms['phone'], sms['message']):
                        sms['status'] = 'sent'
                        sms['sent_at'] = time.time()
                        success_count += 1
                        logger.info(f"✅ SMS 전송 성공: {sms['phone']}")
                    else:
                        fail_count += 1
                        remaining_queue.append(sms)
                        logger.error(f"❌ SMS 전송 실패: {sms['phone']}")
                except Exception as e:
                    fail_count += 1
                    remaining_queue.append(sms)
                    logger.error(f"❌ SMS 전송 예외: {e}")
            else:
                # 이미 전송된 SMS는 유지 (로그용)
                remaining_queue.append(sms)
        
        # 큐 업데이트 (전송 완료된 것도 로그로 유지)
        with open(SMS_QUEUE_FILE, 'w', encoding='utf-8') as f:
            json.dump(remaining_queue, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 SMS 전송 결과: 성공 {success_count}건, 실패 {fail_count}건")
        return success_count, fail_count
        
    except Exception as e:
        logger.error(f"❌ SMS 큐 처리 실패: {e}")
        return 0, 0


def get_queue_status():
    """
    SMS 큐 상태 조회
    Returns:
        dict: 큐 상태 정보
    """
    if not os.path.exists(SMS_QUEUE_FILE):
        return {'total': 0, 'pending': 0, 'sent': 0}
    
    try:
        with open(SMS_QUEUE_FILE, 'r', encoding='utf-8') as f:
            queue = json.load(f)
        
        pending = sum(1 for sms in queue if sms['status'] == 'pending')
        sent = sum(1 for sms in queue if sms['status'] == 'sent')
        
        return {
            'total': len(queue),
            'pending': pending,
            'sent': sent
        }
    except Exception as e:
        logger.error(f"큐 상태 조회 실패: {e}")
        return {'total': 0, 'pending': 0, 'sent': 0}
