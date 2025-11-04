package com.example.dronedilivery;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import androidx.annotation.NonNull;

import com.parrot.drone.groundsdk.GroundSdk;
import com.parrot.drone.groundsdk.ManagedGroundSdk;
import com.parrot.drone.groundsdk.Ref;
import com.parrot.drone.groundsdk.device.Drone;
import com.parrot.drone.groundsdk.device.pilotingitf.Activable;
import com.parrot.drone.groundsdk.device.pilotingitf.ManualCopterPilotingItf;
import com.parrot.drone.groundsdk.device.pilotingitf.ReturnHomePilotingItf;
import com.parrot.drone.groundsdk.device.instrument.Gps;
import com.parrot.drone.groundsdk.device.instrument.Altimeter;
import com.parrot.drone.groundsdk.facility.AutoConnection;

import java.util.List;

/** Parrot Anafi 드론 실제 제어 전용 클래스 - Ground SDK 7.x */
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
    private final Handler handler = new Handler(Looper.getMainLooper());

    // Parrot Ground SDK 관련
    private GroundSdk groundSdk;
    private Drone drone;
    private Ref<Drone> droneRef;
    private Ref<ManualCopterPilotingItf> pilotingItfRef;
    private Ref<ReturnHomePilotingItf> returnHomeRef;
    private Ref<Gps> gpsRef;
    private Ref<Altimeter> altimeterRef;
    private AutoConnection autoConnection;

    // 실제 드론 위치 정보
    private double currentLat = 0;
    private double currentLng = 0;
    private double currentAlt = 0;
    private double originLat, originLng;
    private double destLat, destLng;

    // 드론 연결 상태
    private boolean isDroneConnected = false;

    public DroneController(Context context) {
        this.context = context;
        initGroundSdk();
    }

    /** Ground SDK 초기화 및 실제 드론 검색 */
    private void initGroundSdk() {
        Log.d(TAG, "Initializing Parrot Ground SDK 7.x for real drone connection...");
        
        try {
            // GroundSdk 인스턴스 생성
            groundSdk = GroundSdk.newSession(context, null);
            
            // 자동 연결 기능 활성화
            autoConnection = groundSdk.getFacility(AutoConnection.class);
            if (autoConnection != null) {
                autoConnection.start();
                Log.d(TAG, "AutoConnection started - searching for Parrot drones");
            }

            setState(DroneState.CONNECTING);
            
            // 실제 드론 검색 시작
            searchForRealDrones();
            
        } catch (Exception e) {
            Log.e(TAG, "Failed to initialize Ground SDK: " + e.getMessage());
            setState(DroneState.ERROR);
            notifyError("Ground SDK 초기화 실패: " + e.getMessage());
        }
    }

    /** 실제 Parrot 드론 검색 */
    private void searchForRealDrones() {
        Log.d(TAG, "Searching for real Parrot Anafi drones...");
        
        // 드론 목록 모니터링
        droneRef = groundSdk.getDrone(null, drone -> {
            if (drone != null) {
                Log.d(TAG, "Found Parrot drone: " + drone.getName());
                connectToRealDrone(drone);
            } else {
                Log.w(TAG, "No Parrot drones found. Make sure drone is powered on and in WiFi range.");
                // 5초 후 재검색
                handler.postDelayed(this::searchForRealDrones, 5000);
            }
        });
    }

    /** 실제 드론에 연결 */
    private void connectToRealDrone(@NonNull Drone realDrone) {
        this.drone = realDrone;
        Log.d(TAG, "Connecting to real Parrot drone: " + realDrone.getName());

        // 드론 상태 모니터링
        realDrone.getState(state -> {
            Log.d(TAG, "Real drone connection state: " + state.getConnectionState());
            
            switch (state.getConnectionState()) {
                case CONNECTED:
                    onRealDroneConnected();
                    break;
                case CONNECTING:
                    setState(DroneState.CONNECTING);
                    break;
                case DISCONNECTED:
                    setState(DroneState.DISCONNECTED);
                    isDroneConnected = false;
                    break;
            }
        });

        // 드론이 연결되지 않은 경우 연결 시도
        if (realDrone.getState().getConnectionState() != Drone.ConnectionState.CONNECTED) {
            Log.d(TAG, "Attempting to connect to real drone...");
            realDrone.connect();
        }
    }

    /** 실제 드론 연결 완료 */
    private void onRealDroneConnected() {
        Log.d(TAG, "Real Parrot drone connected successfully!");
        setState(DroneState.CONNECTED);
        isDroneConnected = true;

        // Piloting Interface 설정
        pilotingItfRef = drone.getPilotingItf(ManualCopterPilotingItf.class, pilotingItf -> {
            if (pilotingItf != null) {
                Log.d(TAG, "Manual piloting interface available");
            }
        });

        // Return Home Interface 설정
        returnHomeRef = drone.getPilotingItf(ReturnHomePilotingItf.class, rth -> {
            if (rth != null) {
                Log.d(TAG, "Return Home piloting interface available");
            }
        });

        // 실제 GPS 모니터링
        gpsRef = drone.getInstrument(Gps.class, gps -> {
            if (gps != null && gps.lastKnownLocation() != null) {
                currentLat = gps.lastKnownLocation().getLatitude();
                currentLng = gps.lastKnownLocation().getLongitude();
                currentAlt = gps.lastKnownLocation().getAltitude();
                notifyLocationUpdate();
                Log.d(TAG, "Real GPS location: " + currentLat + ", " + currentLng + ", " + currentAlt + "m");
            }
        });

        // 실제 고도계 모니터링
        altimeterRef = drone.getInstrument(Altimeter.class, altimeter -> {
            if (altimeter != null) {
                currentAlt = altimeter.takeoffRelativeAltitude();
                notifyLocationUpdate();
            }
        });
    }

    public void setStateListener(DroneStateListener listener) {
        this.listener = listener;
    }

    /** 실제 드론으로 배송 미션 시작 */
    public void startDeliveryMission(String origin, String destination, List<String> waypoints) {
        Log.d(TAG, "Starting REAL drone delivery mission from " + origin + " to " + destination);

        if (!isDroneConnected || currentState != DroneState.CONNECTED) {
            notifyError("실제 Parrot Anafi 드론이 연결되지 않았습니다. 드론을 켜고 WiFi에 연결하세요.");
            return;
        }

        ManualCopterPilotingItf pilotingItf = pilotingItfRef != null ? pilotingItfRef.get() : null;
        if (pilotingItf == null) {
            notifyError("드론 조종 인터페이스를 사용할 수 없습니다.");
            return;
        }

        // 현재 실제 위치를 원점으로 저장
        Gps gps = gpsRef != null ? gpsRef.get() : null;
        if (gps != null && gps.lastKnownLocation() != null) {
            originLat = currentLat;
            originLng = currentLng;
            
            // 목적지 좌표 설정 (실제로는 주소를 좌표로 변환 필요)
            destLat = originLat + 0.001; // 약 100m 이동
            destLng = originLng + 0.001;
            
            realTakeOff();
        } else {
            notifyError("GPS 신호를 받을 수 없습니다. 야외에서 시도하세요.");
        }
    }

    /** 실제 드론 이륙 */
    private void realTakeOff() {
        ManualCopterPilotingItf pilotingItf = pilotingItfRef != null ? pilotingItfRef.get() : null;
        if (pilotingItf == null) {
            notifyError("드론 조종 인터페이스를 사용할 수 없습니다.");
            return;
        }

        Log.d(TAG, "Real drone taking off...");
        setState(DroneState.TAKING_OFF);
        
        // 실제 이륙 명령
        pilotingItf.takeOff();
        
        // 이륙 완료 모니터링
        monitorRealTakeoff();
    }

    /** 실제 이륙 모니터링 */
    private void monitorRealTakeoff() {
        handler.postDelayed(() -> {
            if (currentAlt > 5) { // 5m 이상 올라가면 이륙 완료
                Log.d(TAG, "Real takeoff completed at altitude: " + currentAlt + "m");
                realFlyToDestination();
            } else if (currentState == DroneState.TAKING_OFF) {
                // 아직 이륙 중이면 계속 모니터링
                monitorRealTakeoff();
            }
        }, 2000);
    }

    /** 실제 드론으로 목적지 이동 */
    private void realFlyToDestination() {
        setState(DroneState.FLYING_TO_DEST);
        Log.d(TAG, "Real drone flying to destination: " + destLat + ", " + destLng);
        
        // 실제로는 FlightPlan API나 수동 조종으로 목적지 이동
        // 현재는 간단한 예시로 10초 후 착륙
        handler.postDelayed(this::realLandAtDestination, 10000);
    }

    /** 실제 드론 목적지 착륙 */
    private void realLandAtDestination() {
        ManualCopterPilotingItf pilotingItf = pilotingItfRef != null ? pilotingItfRef.get() : null;
        if (pilotingItf == null) {
            notifyError("드론 조종 인터페이스를 사용할 수 없습니다.");
            return;
        }

        Log.d(TAG, "Real drone landing at destination...");
        setState(DroneState.LANDING);
        
        // 실제 착륙 명령
        pilotingItf.land();
        
        // 착륙 완료 모니터링
        monitorRealLanding(() -> setState(DroneState.WAITING_PICKUP));
    }

    /** 실제 착륙 모니터링 */
    private void monitorRealLanding(Runnable onComplete) {
        handler.postDelayed(() -> {
            if (currentAlt < 1) { // 1m 이하로 내려가면 착륙 완료
                Log.d(TAG, "Real landing completed");
                if (onComplete != null) onComplete.run();
            } else if (currentState == DroneState.LANDING) {
                // 아직 착륙 중이면 계속 모니터링
                monitorRealLanding(onComplete);
            }
        }, 2000);
    }

    /** 실제 드론 복귀 */
    public void startReturn() {
        if (!isDroneConnected) {
            notifyError("실제 드론이 연결되지 않았습니다.");
            return;
        }

        ManualCopterPilotingItf pilotingItf = pilotingItfRef != null ? pilotingItfRef.get() : null;
        if (pilotingItf == null) {
            notifyError("드론 조종 인터페이스를 사용할 수 없습니다.");
            return;
        }

        Log.d(TAG, "Starting real drone return journey");
        
        setState(DroneState.TAKING_OFF);
        
        // 실제 이륙
        pilotingItf.takeOff();
        
        handler.postDelayed(() -> {
            setState(DroneState.RETURNING);
            realReturnToHome();
        }, 5000);
    }

    /** 실제 드론 RTH (Return To Home) */
    private void realReturnToHome() {
        Log.d(TAG, "Real drone returning to home...");
        
        ReturnHomePilotingItf rth = returnHomeRef != null ? returnHomeRef.get() : null;
        if (rth != null && rth.state() == Activable.State.IDLE) {
            // 실제 Return Home 기능 사용
            rth.activate();
            Log.d(TAG, "Real Return to Home activated");
            
            // RTH 완료 모니터링
            handler.postDelayed(() -> {
                setState(DroneState.LANDED);
            }, 20000);
        } else {
            notifyError("Return Home 기능을 사용할 수 없습니다.");
        }
    }

    private void setState(DroneState state) {
        this.currentState = state;
        Log.d(TAG, "Real drone state changed to: " + state);
        
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
        Log.e(TAG, "Real drone error: " + error);
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
        return isDroneConnected && drone != null && 
               drone.getState().getConnectionState() == Drone.ConnectionState.CONNECTED;
    }

    /** 드론 이름 가져오기 */
    public String getDroneName() {
        return drone != null ? drone.getName() : "No Drone";
    }

    /** 리소스 정리 */
    public void cleanup() {
        Log.d(TAG, "Cleaning up real drone resources...");
        
        if (handler != null) {
            handler.removeCallbacksAndMessages(null);
        }
        
        // Ref 객체들 정리
        if (droneRef != null) {
            droneRef.close();
        }
        if (pilotingItfRef != null) {
            pilotingItfRef.close();
        }
        if (returnHomeRef != null) {
            returnHomeRef.close();
        }
        if (gpsRef != null) {
            gpsRef.close();
        }
        if (altimeterRef != null) {
            altimeterRef.close();
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
        
        isDroneConnected = false;
    }
}