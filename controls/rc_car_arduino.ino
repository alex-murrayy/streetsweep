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
  
  steeringServo.attach(SERVO_PIN);
  pinMode(MOTOR_PWM_PIN, OUTPUT);
  pinMode(MOTOR_IN1_PIN, OUTPUT);
  pinMode(MOTOR_IN2_PIN, OUTPUT);
  
  setHardware(90, 0); // Start stopped
  lastCommandTime = millis();
  
  Serial.println("RC Car Controller Ready");
}

void loop() {
  checkSerial();
  checkWatchdog();
}

void checkSerial() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    
    if (c == '<') {
      // Start of command
      bufferIndex = 0;
      receiving = true;
    } 
    else if (c == '>') {
      // End of command
      receiving = false;
      buffer[bufferIndex] = '\0';
      parseCommand(buffer);
    }
    else if (receiving && bufferIndex < BUFFER_SIZE - 1) {
      buffer[bufferIndex++] = c;
    }
  }
}

void parseCommand(char* cmd) {
  char* steerStr = strtok(cmd, ",");
  char* throttleStr = strtok(NULL, ",");
  
  if (steerStr && throttleStr) {
    currentSteer = atoi(steerStr);
    currentThrottle = atoi(throttleStr);
    setHardware(currentSteer, currentThrottle);
    lastCommandTime = millis();
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
  
  // Set steering
  steeringServo.write(steer);
  
  // Set motor
  if (throttle > 0) {
    // Forward
    digitalWrite(MOTOR_IN1_PIN, HIGH);
    digitalWrite(MOTOR_IN2_PIN, LOW);
    analogWrite(MOTOR_PWM_PIN, throttle);
  }
  else if (throttle < 0) {
    // Reverse
    digitalWrite(MOTOR_IN1_PIN, LOW);
    digitalWrite(MOTOR_IN2_PIN, HIGH);
    analogWrite(MOTOR_PWM_PIN, abs(throttle));
  }
  else {
    // Stop
    digitalWrite(MOTOR_IN1_PIN, HIGH);
    digitalWrite(MOTOR_IN2_PIN, HIGH);
    analogWrite(MOTOR_PWM_PIN, 0);
  }
}

