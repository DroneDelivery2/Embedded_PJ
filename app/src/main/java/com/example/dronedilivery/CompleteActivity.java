package com.example.dronedilivery;

import android.os.Bundle;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import com.google.android.material.button.MaterialButton;

import java.util.List;

public class CompleteActivity extends AppCompatActivity {

    @Override protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_complete);

        TextView detail = findViewById(R.id.tvCompleteDetail);
        MaterialButton btn = findViewById(R.id.btnReceive);

        String origin = getIntent().getStringExtra("origin");
        String dest = getIntent().getStringExtra("destination");
        List<String> wps = getIntent().getStringArrayListExtra("wps");

        String d = "우편물이 도착하였습니다.\n" +
                (origin != null ? origin : "XXX 우체국") + "\n" +
                (wps != null && !wps.isEmpty() ? "경유지: " + wps + "\n" : "") +
                (dest != null ? dest : "N4동 5층 옥상");
        detail.setText(d);

        btn.setOnClickListener(v -> {
            Toast.makeText(this, "팝업알림: OOO님이 우편물을 수령했습니다.\n드론이 XX 우체국 이착륙장으로 복귀하였습니다.", Toast.LENGTH_LONG).show();
            finish(); // 홈으로 뒤로가기
        });
    }
}
