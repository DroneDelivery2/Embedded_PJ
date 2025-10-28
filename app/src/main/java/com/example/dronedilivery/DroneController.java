package com.example.dronedilivery;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import java.util.List;

/** 드론 제어를 담당하는 클래스 (시뮬레이션 모드) */
public class DroneController {
  private static final String TAG = "DroneController";

  public enum DroneState {
    IDLE, // 대기 중
    CONNECTING, // 연결 중
    CONNECTED, // 연결됨
    TAKING_OFF, // 이륙 중
    FLYING_TO_DEST, // 목적지로 이동 중
    LANDING, // 착륙 중
    WAITING_PICKUP, // 수령 대기 중
    RETURNING, // 복귀 중
    LANDED, // 착륙 완료
    DISCONNECTED, // 연결 해제
    ERROR // 오류
  }

  public interface DroneStateListener {
    void onStateChanged(DroneState state);

    void onLocationUpdate(double lat, double lng, double altitude);

    void onError(String error);
  }

  private final Context context;
  private DroneStateListener listener;
  private DroneState currentState = DroneState.IDLE;
  private Handler handler = new Handler(Looper.getMainLooper());

  // 시뮬레이션용 좌표
  private double currentLat = 37.5665; // 서울 시청 기준
  private double currentLng = 126.9780;
  private double currentAlt = 0;

  private double originLat, originLng;
  private double destLat, destLng;

  public DroneController(Context context) {
    this.context = context;
    // 시뮬레이션 모드로 즉시 연결됨 상태로 설정
    handler.postDelayed(
        () -> {
          setState(DroneState.CONNECTING);
          handler.postDelayed(() -> setState(DroneState.CONNECTED), 2000);
        },
        1000);
  }

  public void setStateListener(DroneStateListener listener) {
    this.listener = listener;
  }

  /** 배송 미션 시작 */
  public void startDeliveryMission(String origin, String destination, List<String> waypoints) {
    Log.d(TAG, "Starting delivery mission from " + origin + " to " + destination);

    // 좌표 설정 (시뮬레이션용)
    originLat = currentLat;
    originLng = currentLng;
    destLat = currentLat + 0.001; // 약 100m 이동
    destLng = currentLng + 0.001;

    // 연결되어 있으면 이륙 시작
    if (currentState == DroneState.CONNECTED) {
      takeOff();
    } else {
      // 연결 대기 후 이륙
      handler.postDelayed(this::takeOff, 3000);
    }
  }

  /** 이륙 */
  private void takeOff() {
    setState(DroneState.TAKING_OFF);

    // 시뮬레이션: 3초 후 이륙 완료
    handler.postDelayed(
        () -> {
          currentAlt = 50; // 50m 고도
          notifyLocationUpdate();
          flyToDestination();
        },
        3000);
  }

  /** 목적지로 이동 */
  private void flyToDestination() {
    setState(DroneState.FLYING_TO_DEST);

    // 시뮬레이션: 10초에 걸쳐 목적지로 이동
    simulateMovement(destLat, destLng, 10000, this::landAtDestination);
  }

  /** 목적지 착륙 */
  private void landAtDestination() {
    setState(DroneState.LANDING);

    // 시뮬레이션: 3초 후 착륙 완료
    handler.postDelayed(
        () -> {
          currentAlt = 0;
          notifyLocationUpdate();
          setState(DroneState.WAITING_PICKUP);
        },
        3000);
  }

  /** 수령 완료 후 복귀 */
  public void startReturn() {
    Log.d(TAG, "Starting return journey");

    // 이륙
    setState(DroneState.TAKING_OFF);
    handler.postDelayed(
        () -> {
          currentAlt = 50;
          notifyLocationUpdate();

          // 원점으로 복귀
          setState(DroneState.RETURNING);
          simulateMovement(originLat, originLng, 10000, this::landAtOrigin);
        },
        3000);
  }

  /** 원점 착륙 */
  private void landAtOrigin() {
    setState(DroneState.LANDING);

    handler.postDelayed(
        () -> {
          currentAlt = 0;
          currentLat = originLat;
          currentLng = originLng;
          notifyLocationUpdate();
          setState(DroneState.LANDED);
        },
        3000);
  }

  /** 이동 시뮬레이션 */
  private void simulateMovement(
      double targetLat, double targetLng, long durationMs, Runnable onComplete) {
    double startLat = currentLat;
    double startLng = currentLng;
    long startTime = System.currentTimeMillis();

    Runnable updatePosition =
        new Runnable() {
          @Override
          public void run() {
            long elapsed = System.currentTimeMillis() - startTime;
            float progress = Math.min(1.0f, (float) elapsed / durationMs);

            currentLat = startLat + (targetLat - startLat) * progress;
            currentLng = startLng + (targetLng - startLng) * progress;

            notifyLocationUpdate();

            if (progress < 1.0f) {
              handler.postDelayed(this, 500); // 0.5초마다 업데이트
            } else {
              currentLat = targetLat;
              currentLng = targetLng;
              notifyLocationUpdate();
              if (onComplete != null) onComplete.run();
            }
          }
        };

    handler.post(updatePosition);
  }

  private void setState(DroneState state) {
    this.currentState = state;
    Log.d(TAG, "Drone state changed to: " + state);

    if (listener != null) {
      listener.onStateChanged(state);
    }
  }

  private void notifyLocationUpdate() {
    if (listener != null) {
      listener.onLocationUpdate(currentLat, currentLng, currentAlt);
    }
  }

  public DroneState getCurrentState() {
    return currentState;
  }

  public double[] getCurrentLocation() {
    return new double[] {currentLat, currentLng, currentAlt};
  }

  /** 리소스 정리 */
  public void cleanup() {
    if (handler != null) {
      handler.removeCallbacksAndMessages(null);
    }
  }
}
