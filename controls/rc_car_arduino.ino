/*
  RC Car Controller for Arduino R4
  Controls servo (steering) and motor driver (throttle)
  
  Commands from Raspberry Pi: <steer,throttle>
  - steer: 45-135 degrees (90 = center)
  - throttle: -255 to 255 (0 = stop, positive = forward, negative = reverse)
  
  Example: <90,200> = center steering, forward at speed 200
*/

#include <Servo.h>

// Pin Definitions
const int SERVO_PIN = 9;        // Servo for steering (must be PWM)
const int MOTOR_PWM_PIN = 5;    // Motor speed (PWM)
const int MOTOR_IN1_PIN = 6;    // Motor direction 1
const int MOTOR_IN2_PIN = 7;    // Motor direction 2

// Safety Watchdog - stops car if no commands received
const unsigned long COMMAND_TIMEOUT = 500; // milliseconds
unsigned long lastCommandTime = 0;

// Global Variables
Servo steeringServo;
int currentSteer = 90;
int currentThrottle = 0;

// Serial Command Buffer
const int BUFFER_SIZE = 32;
char buffer[BUFFER_SIZE];
bool receiving = false;
int bufferIndex = 0;

void setup() {
  Serial.begin(115200);
  
  // Wait for serial port to be ready (important for some systems)
  while (!Serial && millis() < 3000) {
    ; // Wait up to 3 seconds for serial port
  }
  
  steeringServo.attach(SERVO_PIN);
  pinMode(MOTOR_PWM_PIN, OUTPUT);
  pinMode(MOTOR_IN1_PIN, OUTPUT);
  pinMode(MOTOR_IN2_PIN, OUTPUT);
  
  setHardware(90, 0); // Start stopped
  lastCommandTime = millis();
  
  Serial.println("RC Car Controller Ready");
  Serial.println("Send commands as: <steer,throttle>");
  Serial.println("Example: <90,200>");
}

void loop() {
  checkSerial();
  checkWatchdog();
}

void checkSerial() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    
    // Debug: Echo every character received (helps diagnose)
    Serial.print("RX: 0x");
    Serial.print((int)c, HEX);
    Serial.print(" ('");
    if (c >= 32 && c <= 126) {
      Serial.print(c);
    } else {
      Serial.print("?");
    }
    Serial.println("')");
    
    if (c == '<') {
      // Start of command
      bufferIndex = 0;
      receiving = true;
      Serial.println("Command start detected");
    } 
    else if (c == '>') {
      // End of command
      receiving = false;
      buffer[bufferIndex] = '\0';
      Serial.print("Command end detected, buffer: '");
      Serial.print(buffer);
      Serial.println("'");
      parseCommand(buffer);
    }
    else if (receiving && bufferIndex < BUFFER_SIZE - 1) {
      buffer[bufferIndex++] = c;
    }
    else if (!receiving && c != '\n' && c != '\r' && c != ' ') {
      // Debug: Show unexpected characters (helps diagnose issues)
      Serial.print("Unexpected char: '");
      Serial.print(c);
      Serial.print("' (0x");
      Serial.print((int)c, HEX);
      Serial.println(") - Waiting for '<' to start command");
    }
  }
}

void parseCommand(char* cmd) {
  char* steerStr = strtok(cmd, ",");
  char* throttleStr = strtok(NULL, ",");
  
  if (steerStr && throttleStr) {
    currentSteer = atoi(steerStr);
    currentThrottle = atoi(throttleStr);
    
    // Debug: Echo received command
    Serial.print("Received: <");
    Serial.print(steerStr);
    Serial.print(",");
    Serial.print(throttleStr);
    Serial.print("> -> Steer=");
    Serial.print(currentSteer);
    Serial.print(", Throttle=");
    Serial.println(currentThrottle);
    
    setHardware(currentSteer, currentThrottle);
    lastCommandTime = millis();
  } else {
    // Debug: Show parse error
    Serial.print("Parse error: '");
    Serial.print(cmd);
    Serial.println("' (expected format: <steer,throttle>)");
  }
}

void checkWatchdog() {
  if (millis() - lastCommandTime > COMMAND_TIMEOUT) {
    setHardware(90, 0); // Emergency stop
  }
}

void setHardware(int steer, int throttle) {
  // Constrain values to safe ranges
  steer = constrain(steer, 45, 135);
  throttle = constrain(throttle, -255, 255);
  
  // Debug: Show what we're setting
  Serial.print("Setting hardware - Steer: ");
  Serial.print(steer);
  Serial.print(", Throttle: ");
  Serial.println(throttle);
  
  // Set steering
  steeringServo.write(steer);
  Serial.print("Servo pin ");
  Serial.print(SERVO_PIN);
  Serial.print(" set to ");
  Serial.println(steer);
  
  // Set motor
  if (throttle > 0) {
    // Forward
    digitalWrite(MOTOR_IN1_PIN, HIGH);
    digitalWrite(MOTOR_IN2_PIN, LOW);
    analogWrite(MOTOR_PWM_PIN, throttle);
    Serial.print("Motor FORWARD - IN1=HIGH, IN2=LOW, PWM=");
    Serial.println(throttle);
  }
  else if (throttle < 0) {
    // Reverse
    digitalWrite(MOTOR_IN1_PIN, LOW);
    digitalWrite(MOTOR_IN2_PIN, HIGH);
    analogWrite(MOTOR_PWM_PIN, abs(throttle));
    Serial.print("Motor REVERSE - IN1=LOW, IN2=HIGH, PWM=");
    Serial.println(abs(throttle));
  }
  else {
    // Stop
    digitalWrite(MOTOR_IN1_PIN, HIGH);
    digitalWrite(MOTOR_IN2_PIN, HIGH);
    analogWrite(MOTOR_PWM_PIN, 0);
    Serial.println("Motor STOP - IN1=HIGH, IN2=HIGH, PWM=0");
  }
  
  // Verify pin states (read back)
  Serial.print("Pin states - IN1: ");
  Serial.print(digitalRead(MOTOR_IN1_PIN));
  Serial.print(", IN2: ");
  Serial.print(digitalRead(MOTOR_IN2_PIN));
  Serial.print(", PWM pin ");
  Serial.print(MOTOR_PWM_PIN);
  Serial.print(": ");
  // Note: Can't directly read PWM value, but we can verify it's configured
  Serial.println("(PWM output)");
}

