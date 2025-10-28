package com.example.dronedilivery;

import android.content.Intent;
import android.os.Bundle;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import com.google.android.material.button.MaterialButton;
import java.util.List;

public class CompleteActivity extends AppCompatActivity {

  @Override
  protected void onCreate(@Nullable Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_complete);

    TextView detail = findViewById(R.id.tvCompleteDetail);
    MaterialButton btn = findViewById(R.id.btnReceive);

    String origin = getIntent().getStringExtra("origin");
    String dest = getIntent().getStringExtra("destination");
    List<String> wps = getIntent().getStringArrayListExtra("waypoints");

    String d =
        "우편물이 도착하였습니다.\n"
            + (origin != null ? origin : "XXX 우체국")
            + "\n"
            + (wps != null && !wps.isEmpty() ? "경유지: " + wps + "\n" : "")
            + (dest != null ? dest : "N4동 5층 옥상");
    detail.setText(d);

    btn.setOnClickListener(
        v -> {
          // 드론 복귀 시작
          DroneController droneController = DroneManager.getInstance().getDroneController();
          if (droneController != null) {
            droneController.startReturn();
            Toast.makeText(this, "수령 완료! 드론이 복귀를 시작합니다.", Toast.LENGTH_SHORT).show();

            // StatusActivity로 돌아가서 복귀 과정 모니터링
            Intent intent = new Intent(this, StatusActivity.class);
            intent.putExtra("origin", getIntent().getStringExtra("origin"));
            intent.putExtra("destination", getIntent().getStringExtra("destination"));
            intent.putStringArrayListExtra(
                "waypoints", getIntent().getStringArrayListExtra("waypoints"));
            intent.putExtra("returning", true);
            startActivity(intent);
          } else {
            Toast.makeText(this, "드론 연결을 찾을 수 없습니다.", Toast.LENGTH_SHORT).show();
          }
          finish();
        });
  }
}
