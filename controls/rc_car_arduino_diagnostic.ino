/*
  RC Car Controller - Diagnostic Version
  This version has maximum debugging to help diagnose serial communication issues
  Use this if the main sketch isn't working
*/

#include <Servo.h>

// Pin Definitions
const int SERVO_PIN = 9;
const int MOTOR_PWM_PIN = 5;
const int MOTOR_IN1_PIN = 6;
const int MOTOR_IN2_PIN = 7;

Servo steeringServo;

void setup() {
  Serial.begin(115200);
  
  // Wait for serial (but don't block forever)
  unsigned long start = millis();
  while (!Serial && (millis() - start) < 3000) {
    delay(10);
  }
  
  steeringServo.attach(SERVO_PIN);
  pinMode(MOTOR_PWM_PIN, OUTPUT);
  pinMode(MOTOR_IN1_PIN, OUTPUT);
  pinMode(MOTOR_IN2_PIN, OUTPUT);
  
  // Initialize to stopped
  steeringServo.write(90);
  digitalWrite(MOTOR_IN1_PIN, HIGH);
  digitalWrite(MOTOR_IN2_PIN, HIGH);
  analogWrite(MOTOR_PWM_PIN, 0);
  
  Serial.println("========================================");
  Serial.println("RC Car Diagnostic Mode");
  Serial.println("Baud rate: 115200");
  Serial.println("Waiting for commands...");
  Serial.println("Send: <steer,throttle>");
  Serial.println("Example: <90,200>");
  Serial.println("========================================");
  Serial.flush();
}

void loop() {
  // Read all available serial data
  while (Serial.available() > 0) {
    String received = Serial.readStringUntil('\n');
    received.trim();
    
    if (received.length() > 0) {
      Serial.print("Received: '");
      Serial.print(received);
      Serial.print("' (length: ");
      Serial.print(received.length());
      Serial.println(")");
      
      // Check if it's a command
      if (received.startsWith("<") && received.endsWith(">")) {
        // Extract content between <>
        String content = received.substring(1, received.length() - 1);
        Serial.print("Content: '");
        Serial.print(content);
        Serial.println("'");
        
        // Parse steer,throttle
        int commaPos = content.indexOf(',');
        if (commaPos > 0) {
          String steerStr = content.substring(0, commaPos);
          String throttleStr = content.substring(commaPos + 1);
          
          int steer = steerStr.toInt();
          int throttle = throttleStr.toInt();
          
          Serial.print("Parsed - Steer: ");
          Serial.print(steer);
          Serial.print(", Throttle: ");
          Serial.println(throttle);
          
          // Apply constraints
          steer = constrain(steer, 45, 135);
          throttle = constrain(throttle, -255, 255);
          
          Serial.print("Applied - Steer: ");
          Serial.print(steer);
          Serial.print(", Throttle: ");
          Serial.println(throttle);
          
          // Set hardware
          steeringServo.write(steer);
          
          if (throttle > 0) {
            digitalWrite(MOTOR_IN1_PIN, HIGH);
            digitalWrite(MOTOR_IN2_PIN, LOW);
            analogWrite(MOTOR_PWM_PIN, throttle);
            Serial.println("Motor: FORWARD");
          } else if (throttle < 0) {
            digitalWrite(MOTOR_IN1_PIN, LOW);
            digitalWrite(MOTOR_IN2_PIN, HIGH);
            analogWrite(MOTOR_PWM_PIN, abs(throttle));
            Serial.println("Motor: REVERSE");
          } else {
            digitalWrite(MOTOR_IN1_PIN, HIGH);
            digitalWrite(MOTOR_IN2_PIN, HIGH);
            analogWrite(MOTOR_PWM_PIN, 0);
            Serial.println("Motor: STOP");
          }
          
          Serial.println("✓ Command executed!");
        } else {
          Serial.println("✗ Error: No comma found in command");
        }
      } else {
        Serial.print("✗ Error: Command must start with '<' and end with '>'");
        Serial.print(" (got: '");
        Serial.print(received);
        Serial.println("')");
      }
    }
  }
  
  // Small delay to prevent overwhelming serial
  delay(10);
}

