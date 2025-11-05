/*
  RC Car Controller Sketch for Arduino R4
  -----------------------------------------
  This sketch turns the R4 into a real-time controller that listens 
  for commands from a Raspberry Pi (or other computer) over USB Serial.

  THE NEW SETUP:
  1. RASPBERRY PI:
     - Powered by its own USB power bank.
     - Runs the "brain" code (Python).
     - Connects to the Arduino R4 via a USB-C cable.
  2. ARDUINO R4:
     - Powered by the Raspberry Pi over that same USB-C cable.
     - Receives commands from the Pi (e.g., "<90,200>").
     - Controls the hardware (servo and motor driver).
  3. MOTOR SYSTEM:
     - Powered by the 7.4V RC battery pack.
     - Motor Driver (e.g., TB6612FNG or L298N) is connected to the 7.4V battery.
  4. CRITICAL CONNECTION:
     - A single wire MUST connect a GND pin on the R4 to the GND pin on the
       motor driver's LOGIC side. This is the "Common Ground".

  COMMUNICATION PROTOCOL:
  The Pi will send a command string in this exact format:
  <steer,throttle>

  - < and > are the start/end markers.
  - 'steer' is an angle (e.g., 45-135, with 90 as center).
  - 'throttle' is a speed (e.g., -255 to 255, with 0 as stop).
  
  Example commands:
  - "<90,0>"     : Center steering, stop.
  - "<90,200>"   : Center steering, 200/255 speed forward.
  - "<120,-150>" : Steer right, 150/255 speed reverse.
*/

#include <Servo.h>

// --- Pin Definitions ---
// (You can change these to any suitable pins)
const int SERVO_PIN = 9;  // Must be a PWM pin for the servo

// For the motor driver (e.g., L298N or TB6612FNG)
const int MOTOR_PWM_PIN = 5;  // PWM pin for Speed
const int MOTOR_IN1_PIN = 6;  // Direction Pin 1
const int MOTOR_IN2_PIN = 7;  // Direction Pin 2

// --- Safety Watchdog ---
// If we don't get a command from the Pi for this long (in ms),
// the car will automatically stop. This is a critical safety feature!
const unsigned long COMMAND_TIMEOUT = 500; // 500ms
unsigned long lastCommandTime = 0;

// --- Global Objects & Variables ---
Servo steeringServo;
int currentSteerAngle = 90;
int currentThrottleSpeed = 0;

// --- Serial Command Parser ---
const int SERIAL_BUFFER_SIZE = 32;
char serialBuffer[SERIAL_BUFFER_SIZE];
bool receivingCommand = false;
int bufferIndex = 0;


void setup() {
  // Start serial port to talk to Pi.
  // 115200 is a good, fast baud rate.
  Serial.begin(115200);

  // Set up hardware pins
  steeringServo.attach(SERVO_PIN);
  pinMode(MOTOR_PWM_PIN, OUTPUT);
  pinMode(MOTOR_IN1_PIN, OUTPUT);
  pinMode(MOTOR_IN2_PIN, OUTPUT);

  // Start in a safe, stopped state
  setHardware(90, 0); // Center steer, stop motor
  lastCommandTime = millis(); // Start the watchdog timer

  Serial.println("Arduino R4 RC Controller: Ready.");
}

void loop() {
  // 1. Check for new commands from the Pi
  checkSerial();

  // 2. Check the safety watchdog
  checkWatchdog();
}

/**
 * @brief Reads the serial port and parses incoming commands.
 */
void checkSerial() {
  while (Serial.available() > 0) {
    char inChar = Serial.read();

    if (inChar == '<') {
      // Start of a new command
      bufferIndex = 0;
      receivingCommand = true;
      
    } else if (inChar == '>') {
      // End of a command
      receivingCommand = false;
      serialBuffer[bufferIndex] = '\0'; // Null-terminate the string
      
      // Parse the command
      parseCommand(serialBuffer);

    } else if (receivingCommand) {
      // Add character to the buffer
      if (bufferIndex < SERIAL_BUFFER_SIZE - 1) {
        serialBuffer[bufferIndex] = inChar;
        bufferIndex++;
      }
      // If buffer overflows, it will just be ignored.
    }
  }
}

/**
 * @brief Parses the command string (e.g., "90,200")
 * and updates the hardware.
 */
void parseCommand(char* command) {
  // strtok splits the string at the comma
  char* steerStr = strtok(command, ",");
  char* throttleStr = strtok(NULL, ",");

  if (steerStr != NULL && throttleStr != NULL) {
    // We found both parts!
    // Convert text to integers
    int newSteer = atoi(steerStr);
    int newThrottle = atoi(throttleStr);

    // Update our target values
    currentSteerAngle = newSteer;
    currentThrottleSpeed = newThrottle;
    
    // Update the hardware
    setHardware(currentSteerAngle, currentThrottleSpeed);

    // Reset the safety watchdog timer
    lastCommandTime = millis();

    // Optional: Send a confirmation back to the Pi for debugging
    // Serial.print("ACK: Steer=");
    // Serial.print(currentSteerAngle);
    // Serial.print(", Throttle=");
    // Serial.println(currentThrottleSpeed);
  }
}

/**
 * @brief Checks if we've received a command recently.
 * If not, stops the car.
 */
void checkWatchdog() {
  if (millis() - lastCommandTime > COMMAND_TIMEOUT) {
    // We lost connection to the Pi! Stop the car!
    setHardware(90, 0);
    // We don't reset lastCommandTime here, so it keeps stopping
    // until a new command comes in.
  }
}

/**
 * @brief Applies the given steer and throttle values
 * to the servo and motor driver.
 */
void setHardware(int steer, int throttle) {
  // 1. Set Steering
  // Constrain to safe servo values (e.g., 45-135)
  steer = constrain(steer, 45, 135); 
  steeringServo.write(steer);

  // 2. Set Motor Speed & Direction
  // Constrain throttle to -255 to 255
  throttle = constrain(throttle, -255, 255);

  if (throttle > 0) {
    // Go Forward
    digitalWrite(MOTOR_IN1_PIN, HIGH);
    digitalWrite(MOTOR_IN2_PIN, LOW);
    analogWrite(MOTOR_PWM_PIN, throttle);
    
  } else if (throttle < 0) {
    // Go Reverse
    digitalWrite(MOTOR_IN1_PIN, LOW);
    digitalWrite(MOTOR_IN2_PIN, HIGH);
    analogWrite(MOTOR_PWM_PIN, abs(throttle)); // analogWrite needs positive #
    
  } else {
    // Stop (Brake)
    digitalWrite(MOTOR_IN1_PIN, HIGH);
    digitalWrite(MOTOR_IN2_PIN, HIGH);
    analogWrite(MOTOR_PWM_PIN, 0);
  }
}

