#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char* ssid = "REPLACE_WITH_YOUR_SSID";
const char* password = "REPLACE_WITH_YOUR_PASSWORD";

ESP8266WebServer server(80);

// Motor Pins (NodeMCU / Wemos D1 Mini mapping)
#define ENA 5   // D1
#define IN1 4   // D2
#define IN2 0   // D3

#define IN3 2   // D4
#define IN4 14  // D5
#define ENB 12  // D6

// IR Sensor Pins
#define IR_LEFT 13  // D7
#define IR_RIGHT 15 // D8

unsigned long lastCmdTime = 0;
const unsigned long WATCHDOG_TIMEOUT = 500; // ms

int currentLeftSpeed = 0;
int currentRightSpeed = 0;

void setupMotors() {
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);

  setMotors(0, 0);
}

void setMotors(int leftSpeed, int rightSpeed) {
  // Constrain speeds to -255 to 255
  leftSpeed = constrain(leftSpeed, -255, 255);
  rightSpeed = constrain(rightSpeed, -255, 255);

  currentLeftSpeed = leftSpeed;
  currentRightSpeed = rightSpeed;

  // Left Motor
  if (leftSpeed > 0) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    analogWrite(ENA, leftSpeed);
  } else if (leftSpeed < 0) {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    analogWrite(ENA, -leftSpeed);
  } else {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    analogWrite(ENA, 0);
  }

  // Right Motor
  if (rightSpeed > 0) {
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    analogWrite(ENB, rightSpeed);
  } else if (rightSpeed < 0) {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    analogWrite(ENB, -rightSpeed);
  } else {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
    analogWrite(ENB, 0);
  }
}

void handleControl() {
  if (server.hasArg("left") && server.hasArg("right")) {
    int left = server.arg("left").toInt();
    int right = server.arg("right").toInt();
    setMotors(left, right);
    lastCmdTime = millis();
    server.send(200, "text/plain", "OK");
  } else {
    server.send(400, "text/plain", "Missing left or right parameter");
  }
}

void handleStatus() {
  // Read IR sensors (LOW means obstacle detected for FC-51)
  int irLeft = digitalRead(IR_LEFT);
  int irRight = digitalRead(IR_RIGHT);
  
  bool leftBlocked = (irLeft == LOW);
  bool rightBlocked = (irRight == LOW);

  String json = "{";
  json += "\"left_blocked\":" + String(leftBlocked ? "true" : "false") + ",";
  json += "\"right_blocked\":" + String(rightBlocked ? "true" : "false") + ",";
  json += "\"left_speed\":" + String(currentLeftSpeed) + ",";
  json += "\"right_speed\":" + String(currentRightSpeed);
  json += "}";

  server.send(200, "application/json", json);
}

void setup() {
  Serial.begin(115200);
  
  setupMotors();
  pinMode(IR_LEFT, INPUT);
  pinMode(IR_RIGHT, INPUT);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi..");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("Connected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  server.on("/control", HTTP_GET, handleControl);
  server.on("/status", HTTP_GET, handleStatus);
  server.begin();
}

void loop() {
  server.handleClient();

  // Watchdog
  if (millis() - lastCmdTime > WATCHDOG_TIMEOUT && (currentLeftSpeed != 0 || currentRightSpeed != 0)) {
    Serial.println("Watchdog triggered, stopping motors");
    setMotors(0, 0);
  }
}
