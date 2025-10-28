package com.example.dronedilivery;

import android.content.Intent;
import android.os.Bundle;
import android.widget.TextView;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import java.util.List;

public class StatusActivity extends AppCompatActivity
    implements DroneController.DroneStateListener {

  private TextView tvBanner, tvDetail;
  private DroneController droneController;

  @Override
  protected void onCreate(@Nullable Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_status);

    tvBanner = findViewById(R.id.tvBanner);
    tvDetail = findViewById(R.id.tvDetail);

    String origin = getIntent().getStringExtra("origin");
    String dest = getIntent().getStringExtra("destination");
    List<String> wps = getIntent().getStringArrayListExtra("waypoints");

    String detail = "드론 배송 진행 중\n"
        + (origin != null ? origin : "XXX 우체국")
        + "\n"
        + (wps != null && !wps.isEmpty() ? "경유지: " + wps + "\n" : "")
        + (dest != null ? dest : "N4동 5층 옥상");
    tvDetail.setText(detail);

    // 복귀 모드인지 확인
    boolean isReturning = getIntent().getBooleanExtra("returning", false);

    if (isReturning) {
      // 이미 존재하는 드론 컨트롤러 사용 (복귀 중)
      droneController = DroneManager.getInstance().getDroneController();
      if (droneController != null) {
        droneController.setStateListener(this);
      }
    } else {
      // 새로운 미션 시작
      droneController = new DroneController(this);
      droneController.setStateListener(this);
      droneController.startDeliveryMission(origin, dest, wps);
    }
  }

  @Override
  public void onStateChanged(DroneController.DroneState state) {
    runOnUiThread(
        () -> {
          switch (state) {
            case CONNECTING:
              tvBanner.setText("드론에 연결 중입니다...");
              break;
            case CONNECTED:
              tvBanner.setText("드론 연결 완료. 미션을 준비합니다...");
              break;
            case TAKING_OFF:
              tvBanner.setText("드론이 이륙 중입니다...");
              break;
            case FLYING_TO_DEST:
              tvBanner.setText("목적지로 이동 중입니다...");
              break;
            case LANDING:
              tvBanner.setText("목적지에 착륙 중입니다...");
              break;
            case WAITING_PICKUP:
              // 도착 완료 - CompleteActivity로 이동
              Intent intent = new Intent(StatusActivity.this, CompleteActivity.class);
              intent.putExtra("origin", getIntent().getStringExtra("origin"));
              intent.putExtra("destination", getIntent().getStringExtra("destination"));
              intent.putStringArrayListExtra(
                  "waypoints", getIntent().getStringArrayListExtra("waypoints"));
              // 드론 컨트롤러 인스턴스를 전달하기 위해 싱글톤 패턴 사용
              DroneManager.getInstance().setDroneController(droneController);
              startActivity(intent);
              break;
            case RETURNING:
              tvBanner.setText("원점으로 복귀 중입니다...");
              break;
            case LANDED:
              tvBanner.setText("드론이 원점에 착륙했습니다.");
              DroneManager.getInstance().clearDroneController();
              finish(); // 홈으로 돌아가기
              break;
            case DISCONNECTED:
              tvBanner.setText("드론 연결이 끊어졌습니다.");
              break;
            case ERROR:
              tvBanner.setText("드론 오류가 발생했습니다.");
              break;
          }
        });
  }

  @Override
  public void onLocationUpdate(double lat, double lng, double altitude) {
    runOnUiThread(
        () -> {
          String locationInfo = String.format(java.util.Locale.US, "위치: %.6f, %.6f (고도: %.0fm)", lat, lng, altitude);
          // 필요시 위치 정보를 UI에 표시할 수 있음
        });
  }

  @Override
  public void onError(String error) {
    runOnUiThread(
        () -> {
          tvBanner.setText("오류 발생: " + error);
        });
  }
}
