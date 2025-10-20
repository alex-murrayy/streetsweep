/*
 * Dual Motor Control for ELEGoo UNO R3
 * Controls two DC motors independently
 * Useful for robot chassis with left/right wheel control
 * 
 * Wiring:
 * Motor 1 (Left):
 * - IN1 -> Digital Pin 2
 * - IN2 -> Digital Pin 3
 * - ENA -> Digital Pin 9 (PWM)
 * 
 * Motor 2 (Right):
 * - IN1 -> Digital Pin 4
 * - IN2 -> Digital Pin 5
 * - ENA -> Digital Pin 10 (PWM)
 * 
 * Both motors share:
 * - VCC -> 5V
 * - GND -> GND
 * - VM -> External power supply (6-12V)
 */

// Motor 1 (Left) pins
const int M1_IN1 = 2;
const int M1_IN2 = 3;
const int M1_ENA = 9;

// Motor 2 (Right) pins
const int M2_IN1 = 4;
const int M2_IN2 = 5;
const int M2_ENA = 10;

// Motor speeds
int leftSpeed = 0;
int rightSpeed = 0;
int maxSpeed = 255;

// Motor states
enum MotorState {
  STOP,
  FORWARD,
  BACKWARD
};

MotorState leftState = STOP;
MotorState rightState = STOP;

void setup() {
  Serial.begin(9600);
  
  // Initialize motor pins
  pinMode(M1_IN1, OUTPUT);
  pinMode(M1_IN2, OUTPUT);
  pinMode(M1_ENA, OUTPUT);
  pinMode(M2_IN1, OUTPUT);
  pinMode(M2_IN2, OUTPUT);
  pinMode(M2_ENA, OUTPUT);
  
  // Stop both motors
  stopMotor(1);
  stopMotor(2);
  
  Serial.println("=== Dual Motor Control System ===");
  Serial.println("Commands:");
  Serial.println("  'w' - Both motors forward");
  Serial.println("  's' - Both motors backward");
  Serial.println("  'a' - Turn left (left back, right forward)");
  Serial.println("  'd' - Turn right (left forward, right back)");
  Serial.println("  'x' - Stop both motors");
  Serial.println("  'q' - Left motor forward only");
  Serial.println("  'e' - Right motor forward only");
  Serial.println("  'z' - Left motor backward only");
  Serial.println("  'c' - Right motor backward only");
  Serial.println("  '+' - Increase speed");
  Serial.println("  '-' - Decrease speed");
  Serial.println("  '0-9' - Set speed level");
  Serial.println("  'i' - Show status");
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    handleCommand(command);
  }
  
  delay(10);
}

void handleCommand(char command) {
  switch (command) {
    case 'w':
    case 'W':
      // Both forward
      moveMotor(1, FORWARD);
      moveMotor(2, FORWARD);
      Serial.println("Both motors FORWARD");
      break;
      
    case 's':
    case 'S':
      // Both backward
      moveMotor(1, BACKWARD);
      moveMotor(2, BACKWARD);
      Serial.println("Both motors BACKWARD");
      break;
      
    case 'a':
    case 'A':
      // Turn left
      moveMotor(1, BACKWARD);
      moveMotor(2, FORWARD);
      Serial.println("TURN LEFT");
      break;
      
    case 'd':
    case 'D':
      // Turn right
      moveMotor(1, FORWARD);
      moveMotor(2, BACKWARD);
      Serial.println("TURN RIGHT");
      break;
      
    case 'x':
    case 'X':
      // Stop both
      stopMotor(1);
      stopMotor(2);
      Serial.println("Both motors STOPPED");
      break;
      
    case 'q':
    case 'Q':
      // Left forward only
      moveMotor(1, FORWARD);
      stopMotor(2);
      Serial.println("Left motor FORWARD");
      break;
      
    case 'e':
    case 'E':
      // Right forward only
      stopMotor(1);
      moveMotor(2, FORWARD);
      Serial.println("Right motor FORWARD");
      break;
      
    case 'z':
    case 'Z':
      // Left backward only
      moveMotor(1, BACKWARD);
      stopMotor(2);
      Serial.println("Left motor BACKWARD");
      break;
      
    case 'c':
    case 'C':
      // Right backward only
      stopMotor(1);
      moveMotor(2, BACKWARD);
      Serial.println("Right motor BACKWARD");
      break;
      
    case '+':
      increaseSpeed();
      break;
      
    case '-':
      decreaseSpeed();
      break;
      
    case '0':
    case '1':
    case '2':
    case '3':
    case '4':
    case '5':
    case '6':
    case '7':
    case '8':
    case '9':
      setSpeedLevel(command - '0');
      break;
      
    case 'i':
    case 'I':
      printStatus();
      break;
      
    default:
      Serial.println("Unknown command. Use w/s/a/d/x/q/e/z/c/+/-/0-9/i");
      break;
  }
}

void moveMotor(int motor, MotorState direction) {
  int in1, in2, ena;
  
  if (motor == 1) {
    in1 = M1_IN1;
    in2 = M1_IN2;
    ena = M1_ENA;
    leftState = direction;
  } else {
    in1 = M2_IN1;
    in2 = M2_IN2;
    ena = M2_ENA;
    rightState = direction;
  }
  
  switch (direction) {
    case FORWARD:
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
      break;
      
    case BACKWARD:
      digitalWrite(in1, LOW);
      digitalWrite(in2, HIGH);
      break;
      
    case STOP:
      digitalWrite(in1, LOW);
      digitalWrite(in2, LOW);
      break;
  }
  
  // Apply speed
  int speed = (motor == 1) ? leftSpeed : rightSpeed;
  analogWrite(ena, speed);
}

void stopMotor(int motor) {
  moveMotor(motor, STOP);
}

void increaseSpeed() {
  leftSpeed += 25;
  rightSpeed += 25;
  
  if (leftSpeed > maxSpeed) leftSpeed = maxSpeed;
  if (rightSpeed > maxSpeed) rightSpeed = maxSpeed;
  
  // Update current motor speeds
  if (leftState != STOP) analogWrite(M1_ENA, leftSpeed);
  if (rightState != STOP) analogWrite(M2_ENA, rightSpeed);
  
  Serial.print("Speed increased to: ");
  Serial.println(leftSpeed);
}

void decreaseSpeed() {
  leftSpeed -= 25;
  rightSpeed -= 25;
  
  if (leftSpeed < 0) leftSpeed = 0;
  if (rightSpeed < 0) rightSpeed = 0;
  
  // Update current motor speeds
  if (leftState != STOP) analogWrite(M1_ENA, leftSpeed);
  if (rightState != STOP) analogWrite(M2_ENA, rightSpeed);
  
  Serial.print("Speed decreased to: ");
  Serial.println(leftSpeed);
}

void setSpeedLevel(int level) {
  int speed = map(level, 0, 9, 0, maxSpeed);
  leftSpeed = speed;
  rightSpeed = speed;
  
  // Update current motor speeds
  if (leftState != STOP) analogWrite(M1_ENA, leftSpeed);
  if (rightState != STOP) analogWrite(M2_ENA, rightSpeed);
  
  Serial.print("Speed set to level ");
  Serial.print(level);
  Serial.print(" (PWM: ");
  Serial.print(speed);
  Serial.println(")");
}

void printStatus() {
  Serial.println("\n=== Motor Status ===");
  Serial.print("Left Motor: ");
  switch (leftState) {
    case FORWARD: Serial.println("FORWARD"); break;
    case BACKWARD: Serial.println("BACKWARD"); break;
    case STOP: Serial.println("STOPPED"); break;
  }
  Serial.print("Right Motor: ");
  switch (rightState) {
    case FORWARD: Serial.println("FORWARD"); break;
    case BACKWARD: Serial.println("BACKWARD"); break;
    case STOP: Serial.println("STOPPED"); break;
  }
  Serial.print("Left Speed: ");
  Serial.println(leftSpeed);
  Serial.print("Right Speed: ");
  Serial.println(rightSpeed);
  Serial.println("==================\n");
}
