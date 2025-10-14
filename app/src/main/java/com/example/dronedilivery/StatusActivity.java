package com.example.dronedilivery;

import android.content.Intent;
import android.os.Bundle;
import android.os.CountDownTimer;
import android.widget.TextView;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import java.util.List;

public class StatusActivity extends AppCompatActivity {

    private TextView tvBanner, tvDetail;

    @Override protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_status);

        tvBanner = findViewById(R.id.tvBanner);
        tvDetail = findViewById(R.id.tvDetail);

        String origin = getIntent().getStringExtra("origin");
        String dest = getIntent().getStringExtra("destination");
        List<String> wps = getIntent().getStringArrayListExtra("wps");

        String detail = "5분 이내 도착 예정\n" +
                (origin != null ? origin : "XXX 우체국") + "\n" +
                (wps != null && !wps.isEmpty() ? "경유지: " + wps + "\n" : "") +
                (dest != null ? dest : "N4동 5층 옥상");
        tvDetail.setText(detail);

        // 5분 카운트다운 (데모로 15초로 축소: 15000ms)
        new CountDownTimer(15000, 1000) {
            @Override public void onTick(long ms) {
                long sec = ms / 1000;
                tvBanner.setText("팝업알림\nXXX 님이 우편물을 보냈습니다.\n" + sec + "초 뒤 도착 예정입니다.");
            }
            @Override public void onFinish() {
                // 완료 화면으로
                Intent i = new Intent(StatusActivity.this, CompleteActivity.class);
                i.putExtra("origin", origin);
                i.putExtra("destination", dest);
                i.putStringArrayListExtra("wps",
                        wps != null ? new java.util.ArrayList<>(wps) : null);
                startActivity(i);
                finish();
            }
        }.start();
    }
}
