package com.example.dronedilivery;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import androidx.annotation.NonNull;

import com.parrot.drone.groundsdk.GroundSdk;
import com.parrot.drone.groundsdk.ManagedGroundSdk;
import com.parrot.drone.groundsdk.device.Drone;
import com.parrot.drone.groundsdk.device.pilotingitf.ManualCopterPilotingItf;
import com.parrot.drone.groundsdk.device.pilotingitf.ReturnHomePilotingItf;
import com.parrot.drone.groundsdk.device.instrument.Gps;
import com.parrot.drone.groundsdk.device.instrument.Altimeter;
import com.parrot.drone.groundsdk.facility.AutoConnection;

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

  // Parrot Ground SDK 관련
  private ManagedGroundSdk groundSdk;
  private Drone drone;
  private ManualCopterPilotingItf pilotingItf;
  private AutoConnection autoConnection;
  private boolean useSimulation = true; // 시뮬레이션 모드 플래그

  // 좌표 정보
  private double currentLat = 37.5665; // 서울 시청 기준
  private double currentLng = 126.9780;
  private double currentAlt = 0;
  private double originLat, originLng;
  private double destLat, destLng;

  public DroneController(Context context) {
    this.context = context;

    // Parrot Ground SDK 초기화 시도
    try {
      initParrotGroundSdk();
      useSimulation = false;
      Log.d(TAG, "Parrot Ground SDK initialized - Real drone mode");
    } catch (Exception e) {
      Log.w(TAG, "Parrot Ground SDK not available, using simulation mode: " + e.getMessage());
      useSimulation = true;
      startSimulationMode();
    }
  }

  /** Parrot Ground SDK 초기화 */
  private void initParrotGroundSdk() {
    groundSdk = ManagedGroundSdk.obtainSession(context);

    // 자동 연결 설정
    autoConnection = groundSdk.getFacility(AutoConnection.class);
    if (autoConnection != null) {
      autoConnection.start();
    }

    setState(DroneState.CONNECTING);

    // 드론 검색 및 연결
    groundSdk.resume();
    GroundSdk.newSession(context, session -> {
      session.getDevices(Drone.class, droneList -> {
        if (!droneList.isEmpty()) {
          connectToParrotDrone(droneList.get(0));
        } else {
          // 드론을 찾지 못하면 시뮬레이션 모드로 전환
          Log.w(TAG, "No Parrot drone found, switching to simulation");
          useSimulation = true;
          startSimulationMode();
        }
      });
    });
  }

  /** Parrot 드론 연결 */
  private void connectToParrotDrone(Drone discoveredDrone) {
    this.drone = discoveredDrone;

    drone.getState(state -> {
      switch (state.getConnectionState()) {
        case CONNECTED:
          onParrotDroneConnected();
          break;
        case CONNECTING:
          setState(DroneState.CONNECTING);
          break;
        case DISCONNECTED:
          setState(DroneState.DISCONNECTED);
          break;
      }
    });

    if (drone.getState().getConnectionState() != Drone.ConnectionState.CONNECTED) {
      drone.connect();
    }
  }

  /** Parrot 드론 연결 완료 */
  private void onParrotDroneConnected() {
    Log.d(TAG, "Parrot drone connected successfully");
    setState(DroneState.CONNECTED);

    // Piloting Interface 설정
    pilotingItf = drone.getPilotingItf(ManualCopterPilotingItf.class);

    // GPS 위치 모니터링
    drone.getInstrument(Gps.class, gps -> {
      if (gps != null && gps.isFixed()) {
        currentLat = gps.getLastKnownLocation().getLatitude();
        currentLng = gps.getLastKnownLocation().getLongitude();
        currentAlt = gps.getLastKnownLocation().getAltitude();
        notifyLocationUpdate();
      }
    });
  }

  /** 시뮬레이션 모드 시작 */
  private void startSimulationMode() {
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

    if (useSimulation) {
      // 시뮬레이션: 3초 후 이륙 완료
      handler.postDelayed(
          () -> {
            currentAlt = 50; // 50m 고도
            notifyLocationUpdate();
            flyToDestination();
          },
          3000);
    } else {
      // 실제 Parrot 드론 이륙
      if (pilotingItf != null) {
        pilotingItf.takeOff();

        // 고도 모니터링으로 이륙 완료 감지
        drone.getInstrument(Altimeter.class, altimeter -> {
          if (altimeter != null && altimeter.getTakeoffRelativeAltitude() > 10) {
            flyToDestination();
          }
        });
      }
    }
  }

  /** 목적지로 이동 */
  private void flyToDestination() {
    setState(DroneState.FLYING_TO_DEST);

    if (useSimulation) {
      // 시뮬레이션: 10초에 걸쳐 목적지로 이동
      simulateMovement(destLat, destLng, 10000, this::landAtDestination);
    } else {
      // 실제 Parrot 드론 이동 (수동 조종 또는 FlightPlan 사용)
      Log.d(TAG, "Flying to destination with real drone: " + destLat + ", " + destLng);

      // 간단한 예시: 10초 후 착륙 (실제로는 GPS 기반 도착 감지 필요)
      handler.postDelayed(this::landAtDestination, 10000);
    }
  }

  /** 목적지 착륙 */
  private void landAtDestination() {
    setState(DroneState.LANDING);

    if (useSimulation) {
      // 시뮬레이션: 3초 후 착륙 완료
      handler.postDelayed(
          () -> {
            currentAlt = 0;
            notifyLocationUpdate();
            setState(DroneState.WAITING_PICKUP);
          },
          3000);
    } else {
      // 실제 Parrot 드론 착륙
      if (pilotingItf != null) {
        pilotingItf.land();
      }

      handler.postDelayed(() -> setState(DroneState.WAITING_PICKUP), 5000);
    }
  }

  /** 수령 완료 후 복귀 */
  public void startReturn() {
    Log.d(TAG, "Starting return journey");

    setState(DroneState.TAKING_OFF);

    if (useSimulation) {
      handler.postDelayed(
          () -> {
            currentAlt = 50;
            notifyLocationUpdate();
            setState(DroneState.RETURNING);
            simulateMovement(originLat, originLng, 10000, this::landAtOrigin);
          },
          3000);
    } else {
      // 실제 Parrot 드론 복귀
      if (pilotingItf != null) {
        pilotingItf.takeOff();
      }

      handler.postDelayed(() -> {
        setState(DroneState.RETURNING);
        returnToHomeWithParrot();
      }, 5000);
    }
  }

  /** Parrot 드론 RTH (Return To Home) */
  private void returnToHomeWithParrot() {
    ReturnHomePilotingItf rth = drone.getPilotingItf(ReturnHomePilotingItf.class);
    if (rth != null) {
      rth.activate();
    }

    handler.postDelayed(() -> setState(DroneState.LANDED), 15000);
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

    Runnable updatePosition = new Runnable() {
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
          if (onComplete != null)
            onComplete.run();
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
    return new double[] { currentLat, currentLng, currentAlt };
  }

  /** 드론 연결 상태 확인 */
  public boolean isRealDroneConnected() {
    return !useSimulation && drone != null &&
        drone.getState().getConnectionState() == Drone.ConnectionState.CONNECTED;
  }

  /** 시뮬레이션 모드 여부 */
  public boolean isSimulationMode() {
    return useSimulation;
  }

  /** 리소스 정리 */
  public void cleanup() {
    if (handler != null) {
      handler.removeCallbacksAndMessages(null);
    }

    // Parrot Ground SDK 정리
    if (!useSimulation) {
      if (drone != null && drone.getState().getConnectionState() == Drone.ConnectionState.CONNECTED) {
        drone.disconnect();
      }

      if (autoConnection != null) {
        autoConnection.stop();
      }

      if (groundSdk != null) {
        groundSdk.close();
      }
    }
  }
}
