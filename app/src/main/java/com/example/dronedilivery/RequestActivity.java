package com.example.dronedilivery;

import android.content.Intent;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.example.dronedilivery.model.Site;
import com.example.dronedilivery.ui.WaypointAdapter;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;
import java.util.ArrayList;
import java.util.List;

public class RequestActivity extends AppCompatActivity {

  private enum ActiveTarget {
    ORIGIN,
    DEST,
    WAYPOINT
  }

  private LinearLayout llOrigin, llDestination;
  private TextView tvOrigin, tvDestination, tvAddWp;
  private TextInputEditText etSearch;
  private ActiveTarget active = ActiveTarget.ORIGIN;

  private final List<String> waypoints = new ArrayList<>();
  private WaypointAdapter adapter;

  @Override
  protected void onCreate(@Nullable Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_request);

    llOrigin = findViewById(R.id.llOrigin);
    llDestination = findViewById(R.id.llDestination);
    tvOrigin = findViewById(R.id.tvOrigin);
    tvDestination = findViewById(R.id.tvDestination);
    tvAddWp = findViewById(R.id.tvAddWp);
    etSearch = findViewById(R.id.etSearch);
    MaterialButton btnStart = findViewById(R.id.btnStartDelivery);

    // 더미 데이터
    List<Site> sites = new ArrayList<>();
    sites.add(new Site("site 1"));
    sites.add(new Site("site 2"));
    sites.add(new Site("site 3"));
    sites.add(new Site("site 4"));
    sites.add(new Site("N4동 5층 옥상"));
    sites.add(new Site("XXX 우체국"));

    RecyclerView rv = findViewById(R.id.rvSites);
    rv.setLayoutManager(new LinearLayoutManager(this));
    adapter = new WaypointAdapter(sites, this::onSitePicked);
    rv.setAdapter(adapter);

    // 박스 탭해서 활성화
    llOrigin.setOnClickListener(v -> setActive(ActiveTarget.ORIGIN));
    llDestination.setOnClickListener(v -> setActive(ActiveTarget.DEST));
    tvAddWp.setOnClickListener(v -> setActive(ActiveTarget.WAYPOINT));

    // 기본 활성: 출발지
    setActive(ActiveTarget.ORIGIN);

    // 검색 필터
    etSearch.addTextChangedListener(
        new TextWatcher() {
          @Override
          public void beforeTextChanged(CharSequence s, int start, int count, int after) {}

          @Override
          public void onTextChanged(CharSequence s, int start, int before, int count) {
            adapter.filter(s != null ? s.toString() : "");
          }

          @Override
          public void afterTextChanged(Editable s) {}
        });

    btnStart.setOnClickListener(
        v -> {
          String origin = tvOrigin.getText().toString();
          String destination = tvDestination.getText().toString();

          if (origin.equals("출발지") || destination.equals("도착지")) {
            Toast.makeText(this, "출발지와 도착지를 모두 선택해주세요.", Toast.LENGTH_SHORT).show();
            return;
          }

          // StatusActivity로 이동하면서 드론 미션 시작
          Intent intent = new Intent(this, StatusActivity.class);
          intent.putExtra("origin", origin);
          intent.putExtra("destination", destination);
          intent.putStringArrayListExtra("waypoints", new ArrayList<>(waypoints));
          startActivity(intent);
        });
  }

  /** 리스트의 + 버튼 눌렀을 때 동작 */
  private void onSitePicked(Site site) {
    switch (active) {
      case ORIGIN:
        tvOrigin.setText("출발지: " + site.getName());
        break;
      case DEST:
        tvDestination.setText("도착지: " + site.getName());
        break;
      case WAYPOINT:
        waypoints.add(site.getName());
        tvAddWp.setText("경유지: " + waypoints);
        break;
    }
  }

  /** 어떤 입력 칸이 활성인지 표시(배경 강조) */
  private void setActive(ActiveTarget target) {
    this.active = target;

    // reset
    llOrigin.setBackgroundColor(getColor(R.color.card_bg));
    llDestination.setBackgroundColor(getColor(R.color.card_bg));
    tvAddWp.setTextColor(getColor(R.color.primary));

    // highlight
    if (target == ActiveTarget.ORIGIN) {
      llOrigin.setBackgroundColor(0xFFE0D7FF); // 연보라 강조(원하면 values 색으로)
    } else if (target == ActiveTarget.DEST) {
      llDestination.setBackgroundColor(0xFFE0D7FF);
    } else { // WAYPOINT
      tvAddWp.setTextColor(0xFF7E57C2);
    }
  }
}
