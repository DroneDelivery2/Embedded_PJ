package com.example.dronedilivery;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

public class HomeActivity extends AppCompatActivity {
  @Override
  protected void onCreate(@Nullable Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_home);

    Button btnStatus = findViewById(R.id.btnStatus);
    Button btnStart = findViewById(R.id.btnStart);

    btnStatus.setOnClickListener(v -> startActivity(new Intent(this, StatusActivity.class)));

    btnStart.setOnClickListener(v -> startActivity(new Intent(this, RequestActivity.class)));
  }
}
