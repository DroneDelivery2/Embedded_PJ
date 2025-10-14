package com.example.dronedilivery;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

public class LoginActivity extends AppCompatActivity {
    @Override protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        EditText etId = findViewById(R.id.etId);
        EditText etPw = findViewById(R.id.etPw);
        Button btn = findViewById(R.id.btnLogin);

        btn.setOnClickListener(v -> {
            // 데모: 아이디/비번 체크 생략
            startActivity(new Intent(this, HomeActivity.class));
            finish();
        });
    }
}
