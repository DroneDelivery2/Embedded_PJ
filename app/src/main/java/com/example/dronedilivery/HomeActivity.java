package com.example.dronedilivery;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

public class HomeActivity extends AppCompatActivity implements DroneController.DroneStateListener {

  private DroneController droneController;
  private TextView tvDroneStatus;
  private Button btnTestConnection;

  @Override
  protected void onCreate(@Nullable Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_home);

    Button btnStatus = findViewById(R.id.btnStatus);
    Button btnStart = findViewById(R.id.btnStart);
    tvDroneStatus = findViewById(R.id.tvDroneStatus);
    btnTestConnection = findViewById(R.id.btnTestConnection);

    btnStatus.setOnClickListener(v -> startActivity(new Intent(this, StatusActivity.class)));
    btnStart.setOnClickListener(v -> startActivity(new Intent(this, RequestActivity.class)));

    // 드론 연결 테스트 버튼
    btnTestConnection.setOnClickListener(v -> testDroneConnection());

    // 드론 컨트롤러 초기화
    initDroneController();
  }

  private void initDroneController() {
    droneController = new DroneController(this);
    droneController.setStateListener(this);
    DroneManager.getInstance().setDroneController(droneController);
  }

  private void testDroneConnection() {
    if (droneController != null) {
      if (droneController.isRealDroneConnected()) {
        Toast.makeText(this, "✅ " + droneController.getDroneName() + " 연결됨!", Toast.LENGTH_SHORT).show();
      } else {
        Toast.makeText(this, "❌ Parrot Anafi 드론을 찾을 수 없습니다.\n드론을 켜고 WiFi에 연결하세요.", Toast.LENGTH_LONG).show();
      }
    }
  }

  @Override
  public void onStateChanged(DroneController.DroneState state) {
    runOnUiThread(() -> {
      String statusText = "드론 상태: ";
      switch (state) {
        case IDLE:
          statusText += "대기 중";
          break;
        case CONNECTING:
          statusText += "연결 중...";
          break;
        case CONNECTED:
          statusText += "연결됨 - " + droneController.getDroneName();
          break;
        case DISCONNECTED:
          statusText += "연결 해제됨";
          break;
        case ERROR:
          statusText += "오류 발생";
          break;
        default:
          statusText += state.toString();
      }
      tvDroneStatus.setText(statusText);
    });
  }

  @Override
  public void onLocationUpdate(double lat, double lng, double altitude) {
    // 위치 업데이트는 여기서 처리하지 않음
  }

  @Override
  public void onError(String error) {
    runOnUiThread(() -> {
      tvDroneStatus.setText("드론 오류: " + error);
      Toast.makeText(this, "드론 오류: " + error, Toast.LENGTH_LONG).show();
    });
  }

  @Override
  protected void onDestroy() {
    super.onDestroy();
    if (droneController != null) {
      droneController.cleanup();
    }
  }
}
