package com.example.dronedilivery;

import android.app.Application;
import android.util.Log;

/** 드론 배달 앱의 Application 클래스 */
public class DroneDeliveryApplication extends Application {
  private static final String TAG = "DroneDeliveryApp";

  @Override
  public void onCreate() {
    super.onCreate();
    Log.d(TAG, "Drone Delivery App initialized");

    // Parrot Ground SDK는 DroneController에서 필요할 때 초기화됩니다.
    // 여기서는 앱 전역 설정만 수행합니다.
  }
}
