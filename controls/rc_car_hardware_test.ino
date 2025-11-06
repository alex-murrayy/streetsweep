/*
  RC Car Hardware Test
  Tests servo and motor independently to verify wiring and power
  
  This sketch will:
  1. Test servo by sweeping 45-135 degrees
  2. Test motor forward at different speeds
  3. Test motor reverse at different speeds
  4. Test motor stop
  
  Use this to verify your hardware is working before using the main controller
*/

#include <Servo.h>

// Pin Definitions (must match main sketch)
const int SERVO_PIN = 9;
const int MOTOR_PWM_PIN = 5;
const int MOTOR_IN1_PIN = 6;
const int MOTOR_IN2_PIN = 7;

Servo steeringServo;

void setup() {
  Serial.begin(115200);
  
  // Wait for serial
  while (!Serial && millis() < 3000) {
    delay(10);
  }
  
  Serial.println("========================================");
  Serial.println("RC Car Hardware Test");
  Serial.println("========================================");
  Serial.println();
  
  // Initialize pins
  steeringServo.attach(SERVO_PIN);
  pinMode(MOTOR_PWM_PIN, OUTPUT);
  pinMode(MOTOR_IN1_PIN, OUTPUT);
  pinMode(MOTOR_IN2_PIN, OUTPUT);
  
  Serial.println("Pin Configuration:");
  Serial.print("  Servo: Pin ");
  Serial.println(SERVO_PIN);
  Serial.print("  Motor PWM: Pin ");
  Serial.println(MOTOR_PWM_PIN);
  Serial.print("  Motor IN1: Pin ");
  Serial.println(MOTOR_IN1_PIN);
  Serial.print("  Motor IN2: Pin ");
  Serial.println(MOTOR_IN2_PIN);
  Serial.println();
  
  delay(1000);
}

void loop() {
  Serial.println("=== TEST 1: Servo Sweep ===");
  Serial.println("Servo should move from left to right");
  
  // Sweep servo from 45 to 135 degrees
  for (int angle = 45; angle <= 135; angle += 5) {
    steeringServo.write(angle);
    Serial.print("Servo: ");
    Serial.print(angle);
    Serial.println(" degrees");
    delay(100);
  }
  
  // Return to center
  steeringServo.write(90);
  Serial.println("Servo: 90 degrees (center)");
  delay(1000);
  
  Serial.println();
  Serial.println("=== TEST 2: Motor Forward ===");
  Serial.println("Motor should spin FORWARD");
  
  // Test forward at increasing speeds
  digitalWrite(MOTOR_IN1_PIN, HIGH);
  digitalWrite(MOTOR_IN2_PIN, LOW);
  
  for (int speed = 50; speed <= 200; speed += 50) {
    analogWrite(MOTOR_PWM_PIN, speed);
    Serial.print("Motor FORWARD at speed: ");
    Serial.println(speed);
    delay(2000);
  }
  
  // Stop motor
  digitalWrite(MOTOR_IN1_PIN, HIGH);
  digitalWrite(MOTOR_IN2_PIN, HIGH);
  analogWrite(MOTOR_PWM_PIN, 0);
  Serial.println("Motor STOP");
  delay(2000);
  
  Serial.println();
  Serial.println("=== TEST 3: Motor Reverse ===");
  Serial.println("Motor should spin REVERSE");
  
  // Test reverse at increasing speeds
  digitalWrite(MOTOR_IN1_PIN, LOW);
  digitalWrite(MOTOR_IN2_PIN, HIGH);
  
  for (int speed = 50; speed <= 200; speed += 50) {
    analogWrite(MOTOR_PWM_PIN, speed);
    Serial.print("Motor REVERSE at speed: ");
    Serial.println(speed);
    delay(2000);
  }
  
  // Stop motor
  digitalWrite(MOTOR_IN1_PIN, HIGH);
  digitalWrite(MOTOR_IN2_PIN, HIGH);
  analogWrite(MOTOR_PWM_PIN, 0);
  Serial.println("Motor STOP");
  delay(2000);
  
  Serial.println();
  Serial.println("=== TEST 4: Pin State Verification ===");
  
  // Test all pin states
  Serial.println("Setting pins and reading back:");
  
  // Test IN1
  digitalWrite(MOTOR_IN1_PIN, HIGH);
  Serial.print("IN1 set HIGH, read: ");
  Serial.println(digitalRead(MOTOR_IN1_PIN) == HIGH ? "HIGH ✓" : "LOW ✗");
  delay(100);
  
  digitalWrite(MOTOR_IN1_PIN, LOW);
  Serial.print("IN1 set LOW, read: ");
  Serial.println(digitalRead(MOTOR_IN1_PIN) == LOW ? "LOW ✓" : "HIGH ✗");
  delay(100);
  
  // Test IN2
  digitalWrite(MOTOR_IN2_PIN, HIGH);
  Serial.print("IN2 set HIGH, read: ");
  Serial.println(digitalRead(MOTOR_IN2_PIN) == HIGH ? "HIGH ✓" : "LOW ✗");
  delay(100);
  
  digitalWrite(MOTOR_IN2_PIN, LOW);
  Serial.print("IN2 set LOW, read: ");
  Serial.println(digitalRead(MOTOR_IN2_PIN) == LOW ? "LOW ✓" : "HIGH ✗");
  delay(100);
  
  // Reset to safe state
  digitalWrite(MOTOR_IN1_PIN, HIGH);
  digitalWrite(MOTOR_IN2_PIN, HIGH);
  analogWrite(MOTOR_PWM_PIN, 0);
  steeringServo.write(90);
  
  Serial.println();
  Serial.println("=== Tests Complete ===");
  Serial.println("If servo/motor didn't move, check:");
  Serial.println("  1. Power supply (servo and motor need external power)");
  Serial.println("  2. Wiring connections");
  Serial.println("  3. Ground connections (all grounds must be connected)");
  Serial.println("  4. Motor driver module is working");
  Serial.println();
  Serial.println("Restarting tests in 5 seconds...");
  Serial.println();
  delay(5000);
}

