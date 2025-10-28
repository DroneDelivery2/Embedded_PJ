package com.example.dronedilivery;

/** 드론 컨트롤러를 Activity 간에 공유하기 위한 싱글톤 매니저 */
public class DroneManager {
  private static DroneManager instance;
  private DroneController droneController;

  private DroneManager() {
  }

  public static DroneManager getInstance() {
    if (instance == null) {
      instance = new DroneManager();
    }
    return instance;
  }

  public void setDroneController(DroneController controller) {
    this.droneController = controller;
  }

  public DroneController getDroneController() {
    return droneController;
  }

  public void clearDroneController() {
    this.droneController = null;
  }
}
