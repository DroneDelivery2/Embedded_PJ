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
        
        // 드론 목록 모니터링
        groundSdk.getLiveData(GroundSdk.newLiveDataQuery(Drone.class))
            .observeForever(drones -> {
                Log.d(TAG, "Found " + drones.size() + " drone(s)");
                
                if (!drones.isEmpty()) {
                    // 첫 번째 드론에 연결
                    Drone firstDrone = drones.iterator().next();
                    connectToDrone(firstDrone);
                } else {
                    Log.w(TAG, "No drones found");
                    // 5초 후 재검색
                    handler.postDelayed(this::searchForDrones, 5000);
                }
            });
    }

    /** 특정 드론에 연결 */
    private void connectToDrone(@NonNull Drone drone) {
        this.drone = drone;
        Log.d(TAG, "Attempting to connect to drone: " + drone.getName());

        // 드론 상태 모니터링
        drone.getState(state -> {
            Log.d(TAG, "Drone connection state: " + state.getConnectionState());
            
            switch (state.getConnectionState()) {
                case CONNECTED:
                    onDroneConnected();
                    break;
                case CONNECTING:
                    setState(DroneState.CONNECTING);
                    break;
                case DISCONNECTED:
                    setState(DroneState.DISCONNECTED);
                    break;
            }
        });

        // 드론이 연결되지 않은 경우 연결 시도
        if (drone.getState().getConnectionState() != Drone.ConnectionState.CONNECTED) {
            Log.d(TAG, "Connecting to drone...");
            drone.connect();
        }
    }

    /** 드론 연결 완료 처리 */
    private void onDroneConnected() {
        Log.d(TAG, "Drone connected successfully!");
        setState(DroneState.CONNECTED);

        // Piloting Interface 설정
        pilotingItf = drone.getPilotingItf(ManualCopterPilotingItf.class);
        if (pilotingItf != null) {
            Log.d(TAG, "Manual piloting interface available");
        }

        // GPS 위치 모니터링
        drone.getInstrument(Gps.class, gps -> {
            if (gps != null && gps.isFixed()) {
                currentLat = gps.getLastKnownLocation().getLatitude();
                currentLng = gps.getLastKnownLocation().getLongitude();
                currentAlt = gps.getLastKnownLocation().getAltitude();
                notifyLocationUpdate();
                Log.d(TAG, "GPS location: " + currentLat + ", " + currentLng + ", " + currentAlt + "m");
            }
        });

        // 고도계 모니터링
        drone.getInstrument(Altimeter.class, altimeter -> {
            if (altimeter != null) {
                currentAlt = altimeter.getTakeoffRelativeAltitude();
                notifyLocationUpdate();
            }
        });
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
        if (pilotingItf == null) {
            notifyError("Piloting interface not available");
            return;
        }

        Log.d(TAG, "Taking off...");
        setState(DroneState.TAKING_OFF);
        
        // 이륙 명령
        pilotingItf.takeOff();
        
        // 이륙 완료 대기 (고도 모니터링)
        monitorTakeoff();
    }

    /** 이륙 모니터링 */
    private void monitorTakeoff() {
        handler.postDelayed(() -> {
            if (currentAlt > 5) { // 5m 이상 올라가면 이륙 완료
                Log.d(TAG, "Takeoff completed at altitude: " + currentAlt + "m");
                flyToDestination();
            } else if (currentState == DroneState.TAKING_OFF) {
                // 아직 이륙 중이면 계속 모니터링
                monitorTakeoff();
            }
        }, 1000);
    }

    /** 목적지로 이동 */
    private void flyToDestination() {
        setState(DroneState.FLYING_TO_DEST);
        Log.d(TAG, "Flying to destination: " + destLat + ", " + destLng);
        
        // 실제로는 FlightPlan API나 수동 조종으로 목적지 이동
        // 여기서는 간단한 예시로 10초 후 착륙
        handler.postDelayed(this::landAtDestination, 10000);
    }

    /** 목적지 착륙 */
    private void landAtDestination() {
        Log.d(TAG, "Landing at destination...");
        setState(DroneState.LANDING);
        
        if (pilotingItf != null) {
            pilotingItf.land();
        }
        
        // 착륙 완료 대기
        monitorLanding(() -> setState(DroneState.WAITING_PICKUP));
    }

    /** 착륙 모니터링 */
    private void monitorLanding(Runnable onComplete) {
        handler.postDelayed(() -> {
            if (currentAlt < 1) { // 1m 이하로 내려가면 착륙 완료
                Log.d(TAG, "Landing completed");
                if (onComplete != null) onComplete.run();
            } else if (currentState == DroneState.LANDING) {
                // 아직 착륙 중이면 계속 모니터링
                monitorLanding(onComplete);
            }
        }, 1000);
    }

    /** 수령 완료 후 복귀 */
    public void startReturn() {
        Log.d(TAG, "Starting return journey");
        
        setState(DroneState.TAKING_OFF);
        
        if (pilotingItf != null) {
            pilotingItf.takeOff();
        }
        
        handler.postDelayed(() -> {
            setState(DroneState.RETURNING);
            returnToHome();
        }, 5000);
    }

    /** 원점 복귀 (RTH - Return To Home) */
    private void returnToHome() {
        Log.d(TAG, "Returning to home...");
        
        // Return Home 기능 사용
        ReturnHomePilotingItf rth = drone.getPilotingItf(ReturnHomePilotingItf.class);
        if (rth != null && rth.getState() == Activable.State.IDLE) {
            rth.activate();
            Log.d(TAG, "Return to Home activated");
        }
        
        // 착륙 완료 대기
        handler.postDelayed(() -> {
            setState(DroneState.LANDED);
        }, 15000);
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
        return new double[]{currentLat, currentLng, currentAlt};
    }

    /** 실제 드론 연결 상태 확인 */
    public boolean isRealDroneConnected() {
        return drone != null && drone.getState().getConnectionState() == Drone.ConnectionState.CONNECTED;
    }

    /** 시뮬레이션 모드 여부 (항상 false - 실제 드론만 사용) */
    public boolean isSimulationMode() {
        return false;
    }

    /** 리소스 정리 */
    public void cleanup() {
        Log.d(TAG, "Cleaning up resources...");
        
        if (handler != null) {
            handler.removeCallbacksAndMessages(null);
        }
        
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