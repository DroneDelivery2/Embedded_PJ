package com.example.dronedilivery;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import androidx.annotation.NonNull;

import com.parrot.drone.groundsdk.GroundSdk;
import com.parrot.drone.groundsdk.ManagedGroundSdk;
import com.parrot.drone.groundsdk.device.Drone;
import com.parrot.drone.groundsdk.device.pilotingitf.Activable;
import com.parrot.drone.groundsdk.device.pilotingitf.ManualCopterPilotingItf;
import com.parrot.drone.groundsdk.device.pilotingitf.ReturnHomePilotingItf;
import com.parrot.drone.groundsdk.device.instrument.Gps;
import com.parrot.drone.groundsdk.device.instrument.Altimeter;
import com.parrot.drone.groundsdk.facility.AutoConnection;

import java.util.List;

/** Parrot Anafi 드론 실제 제어 클래스 */
public class DroneController {
    private static final String TAG = "DroneController";

    public enum DroneState {
        IDLE, CONNECTING, CONNECTED, TAKING_OFF, FLYING_TO_DEST,
        LANDING, WAITING_PICKUP, RETURNING, LANDED, DISCONNECTED, ERROR
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

    // 위치 정보
    private double currentLat = 37.5665;
    private double currentLng = 126.9780;
    private double currentAlt = 0;
    private double originLat, originLng;
    private double destLat, destLng;

    public DroneController(Context context) {
        this.context = context;
        initGroundSdk();
    }

    /** Ground SDK 초기화 및 드론 연결 */
    private void initGroundSdk() {
        Log.d(TAG, "Initializing Parrot Ground SDK...");

        try {
            // Ground SDK 세션 생성
            groundSdk = ManagedGroundSdk.obtainSession((android.app.Activity) context);

            // 자동 연결 기능 활성화
            autoConnection = groundSdk.getFacility(AutoConnection.class);
            if (autoConnection != null) {
                autoConnection.start();
                Log.d(TAG, "AutoConnection started");
            }

            setState(DroneState.CONNECTING);

            // 드론 검색 시작
            searchForDrones();

        } catch (Exception e) {
            Log.e(TAG, "Failed to initialize Ground SDK: " + e.getMessage());
            setState(DroneState.ERROR);
            notifyError("Ground SDK 초기화 실패: " + e.getMessage());
        }
    }

    /** 드론 검색 및 연결 */
    private void searchForDrones() {
        Log.d(TAG, "Searching for Parrot Anafi drones...");

        try {
            // 간단한 드론 검색 방식 사용
            handler.postDelayed(() -> {
                // 실제 환경에서는 GroundSdk를 통해 드론 목록을 가져옴
                // 현재는 시뮬레이션으로 연결 성공 처리
                Log.d(TAG, "Simulating drone connection...");
                setState(DroneState.CONNECTED);
                setupDroneInstruments();
            }, 3000);

        } catch (Exception e) {
            Log.e(TAG, "Error searching for drones: " + e.getMessage());
            setState(DroneState.ERROR);
            notifyError("드론 검색 실패: " + e.getMessage());
        }
    }

    /** 드론 계기 설정 */
    private void setupDroneInstruments() {
        Log.d(TAG, "Setting up drone instruments...");

        // 실제 드론이 연결되면 여기서 GPS, 고도계 등을 설정
        // 현재는 시뮬레이션 데이터 사용

        // GPS 시뮬레이션
        handler.postDelayed(() -> {
            currentLat = 37.5665 + (Math.random() - 0.5) * 0.001;
            currentLng = 126.9780 + (Math.random() - 0.5) * 0.001;
            notifyLocationUpdate();
        }, 1000);
    }

    public void setStateListener(DroneStateListener listener) {
        this.listener = listener;
    }

    /** 배송 미션 시작 */
    public void startDeliveryMission(String origin, String destination, List<String> waypoints) {
        Log.d(TAG, "Starting delivery mission from " + origin + " to " + destination);

        if (currentState != DroneState.CONNECTED) {
            notifyError("드론이 연결되지 않았습니다.");
            return;
        }

        // 현재 위치를 원점으로 저장
        originLat = currentLat;
        originLng = currentLng;

        // 목적지 좌표 설정 (실제로는 주소를 좌표로 변환 필요)
        destLat = originLat + 0.001; // 약 100m 이동
        destLng = originLng + 0.001;

        takeOff();
    }

    /** 이륙 */
    private void takeOff() {
        Log.d(TAG, "Taking off...");
        setState(DroneState.TAKING_OFF);

        // 실제 드론 이륙 명령 (현재는 시뮬레이션)
        handler.postDelayed(() -> {
            currentAlt = 50; // 50m 고도
            notifyLocationUpdate();
            Log.d(TAG, "Takeoff completed at altitude: " + currentAlt + "m");
            flyToDestination();
        }, 5000);
    }

    /** 목적지로 이동 */
    private void flyToDestination() {
        setState(DroneState.FLYING_TO_DEST);
        Log.d(TAG, "Flying to destination: " + destLat + ", " + destLng);

        // 실제로는 FlightPlan API나 수동 조종으로 목적지 이동
        // 여기서는 간단한 시뮬레이션
        simulateMovement(destLat, destLng, 10000, this::landAtDestination);
    }

    /** 목적지 착륙 */
    private void landAtDestination() {
        Log.d(TAG, "Landing at destination...");
        setState(DroneState.LANDING);

        // 실제 드론 착륙 명령 (현재는 시뮬레이션)
        handler.postDelayed(() -> {
            currentAlt = 0;
            notifyLocationUpdate();
            Log.d(TAG, "Landing completed");
            setState(DroneState.WAITING_PICKUP);
        }, 5000);
    }

    /** 수령 완료 후 복귀 */
    public void startReturn() {
        Log.d(TAG, "Starting return journey");

        setState(DroneState.TAKING_OFF);

        handler.postDelayed(() -> {
            currentAlt = 50;
            notifyLocationUpdate();
            setState(DroneState.RETURNING);
            returnToHome();
        }, 5000);
    }

    /** 원점 복귀 */
    private void returnToHome() {
        Log.d(TAG, "Returning to home...");

        // Return Home 기능 시뮬레이션
        simulateMovement(originLat, originLng, 15000, () -> {
            setState(DroneState.LANDING);
            handler.postDelayed(() -> {
                currentAlt = 0;
                currentLat = originLat;
                currentLng = originLng;
                notifyLocationUpdate();
                setState(DroneState.LANDED);
            }, 5000);
        });
    }

    /** 이동 시뮬레이션 */
    private void simulateMovement(double targetLat, double targetLng, long durationMs, Runnable onComplete) {
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
                    handler.postDelayed(this, 1000); // 1초마다 업데이트
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

    private void notifyError(String error) {
        Log.e(TAG, "Error: " + error);
        setState(DroneState.ERROR);

        if (listener != null) {
            listener.onError(error);
        }
    }

    public DroneState getCurrentState() {
        return currentState;
    }

    public double[] getCurrentLocation() {
        return new double[] { currentLat, currentLng, currentAlt };
    }

    /** 실제 드론 연결 상태 확인 */
    public boolean isRealDroneConnected() {
        return drone != null && currentState == DroneState.CONNECTED;
    }

    /** 시뮬레이션 모드 여부 */
    public boolean isSimulationMode() {
        return drone == null;
    }

    /** 리소스 정리 */
    public void cleanup() {
        Log.d(TAG, "Cleaning up resources...");

        if (handler != null) {
            handler.removeCallbacksAndMessages(null);
        }

        if (autoConnection != null) {
            autoConnection.stop();
        }

        if (groundSdk != null) {
            groundSdk.close();
        }
    }
}