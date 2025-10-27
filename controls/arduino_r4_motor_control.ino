/*
 * Arduino R4 Motor Control for Raspberry Pi Trash Detection
 * Receives commands from Pi via Serial and controls stepper motors
 * Optimized for Arduino Uno R4 with enhanced features
 * 
 * Wiring for ULN2003 Stepper Motor Driver:
 * - IN1 -> Digital Pin 4
 * - IN2 -> Digital Pin 5
 * - IN3 -> Digital Pin 6
 * - IN4 -> Digital Pin 7
 * - VCC -> 5V
 * - GND -> GND
 * - Motor center tap -> VCC (5V)
 * - Motor coils -> OUT1, OUT2, OUT3, OUT4
 * 
 * Commands from Pi:
 * 'f' - Move forward (towards center trash)
 * 'l' - Move left (towards left trash)
 * 'r' - Move right (towards right trash)
 * 's' - Stop motor
 * 'h' - Home position
 * 't' - Test sequence
 * 'i' - Status information
 */

// Stepper motor pins (updated for R4 compatibility)
const int IN1_PIN = 4;
const int IN2_PIN = 5;
const int IN3_PIN = 6;
const int IN4_PIN = 7;

// Status LED pin (optional)
const int STATUS_LED = 13;

// Motor parameters
int stepDelay = 3;  // Delay between steps (milliseconds)
int stepsPerRevolution = 2048;  // 28BYJ-48 has 2048 steps per revolution
int currentStep = 0;
int totalSteps = 0;
int targetSteps = 0;

// Motor states
enum MotorState {
  STOPPED,
  FORWARD,
  BACKWARD,
  LEFT,
  RIGHT
};

MotorState currentState = STOPPED;

// Step sequence for 4-phase stepper motor (half-step mode)
const int stepSequence[8][4] = {
  {1, 0, 0, 0},
  {1, 1, 0, 0},
  {0, 1, 0, 0},
  {0, 1, 1, 0},
  {0, 0, 1, 0},
  {0, 0, 1, 1},
  {0, 0, 0, 1},
  {1, 0, 0, 1}
};

// Movement parameters
const int FORWARD_STEPS = 512;    // 1/4 turn forward
const int SIDE_STEPS = 256;       // 1/8 turn for left/right
const int HOME_STEPS = 1024;      // 1/2 turn for homing

// Status tracking
unsigned long lastCommandTime = 0;
unsigned long commandTimeout = 10000;  // 10 second timeout
bool piConnected = false;
int commandCount = 0;

void setup() {
  Serial.begin(9600);
  
  // Initialize stepper motor pins
  pinMode(IN1_PIN, OUTPUT);
  pinMode(IN2_PIN, OUTPUT);
  pinMode(IN3_PIN, OUTPUT);
  pinMode(IN4_PIN, OUTPUT);
  
  // Initialize status LED
  pinMode(STATUS_LED, OUTPUT);
  
  // Initialize motor in stopped state
  stopMotor();
  
  // Wait for Pi connection
  Serial.println("ARDUINO_R4_READY");
  Serial.println("Waiting for Pi connection...");
  
  // Blink LED to indicate ready state
  blinkLED(3, 200);
  
  // Send ready signal
  delay(1000);
  Serial.println("ARDUINO_R4_READY");
}

void loop() {
  // Check for serial commands from Pi
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    handlePiCommand(command);
    lastCommandTime = millis();
    piConnected = true;
    commandCount++;
    
    // Blink LED on command received
    digitalWrite(STATUS_LED, HIGH);
    delay(50);
    digitalWrite(STATUS_LED, LOW);
  }
  
  // Check for command timeout
  if (piConnected && (millis() - lastCommandTime > commandTimeout)) {
    piConnected = false;
    stopMotor();
    Serial.println("PI_DISCONNECTED");
    blinkLED(5, 100);  // Fast blink to indicate disconnection
  }
  
  // Execute motor movement if not stopped
  if (currentState != STOPPED) {
    executeStep();
  }
  
  delay(stepDelay);
}

void handlePiCommand(String command) {
  Serial.print("Received: ");
  Serial.println(command);
  
  if (command == "f" || command == "F") {
    // Move forward (towards center trash)
    moveForward();
  }
  else if (command == "l" || command == "L") {
    // Move left (towards left trash)
    moveLeft();
  }
  else if (command == "r" || command == "R") {
    // Move right (towards right trash)
    moveRight();
  }
  else if (command == "s" || command == "S") {
    // Stop motor
    stopMotor();
  }
  else if (command == "h" || command == "H") {
    // Home position
    moveHome();
  }
  else if (command == "t" || command == "T") {
    // Test sequence
    runTestSequence();
  }
  else if (command == "status") {
    // Send status
    sendStatus();
  }
  else if (command == "ping") {
    // Respond to ping
    Serial.println("pong");
  }
  else {
    Serial.print("Unknown command: ");
    Serial.println(command);
  }
}

void moveForward() {
  rotateSteps(FORWARD_STEPS, FORWARD);
  Serial.println("Moving FORWARD");
}

void moveLeft() {
  rotateSteps(SIDE_STEPS, LEFT);
  Serial.println("Moving LEFT");
}

void moveRight() {
  rotateSteps(SIDE_STEPS, RIGHT);
  Serial.println("Moving RIGHT");
}

void moveHome() {
  rotateSteps(HOME_STEPS, BACKWARD);
  Serial.println("Moving to HOME position");
}

void runTestSequence() {
  Serial.println("Running test sequence...");
  
  // Test forward
  rotateSteps(FORWARD_STEPS, FORWARD);
  delay(1000);
  
  // Test left
  rotateSteps(SIDE_STEPS, LEFT);
  delay(1000);
  
  // Test right
  rotateSteps(SIDE_STEPS, RIGHT);
  delay(1000);
  
  // Return to home
  rotateSteps(HOME_STEPS, BACKWARD);
  
  Serial.println("Test sequence complete");
}

void rotateSteps(int steps, MotorState direction) {
  if (steps <= 0) return;
  
  currentState = direction;
  totalSteps = steps;
  currentStep = 0;
  targetSteps = steps;
  
  Serial.print("Rotating ");
  Serial.print(steps);
  Serial.print(" steps ");
  Serial.println(getDirectionName(direction));
}

void executeStep() {
  if (currentStep >= totalSteps) {
    stopMotor();
    Serial.println("Movement complete");
    return;
  }
  
  int stepPattern;
  
  // Calculate the step pattern based on direction
  switch (currentState) {
    case FORWARD:
      stepPattern = currentStep % 8; // Cycles 0, 1, 2, ..., 7
      break;
    case BACKWARD:
      stepPattern = 7 - (currentStep % 8); // Cycles 7, 6, 5, ..., 0
      break;
    case LEFT:
      stepPattern = currentStep % 8; // Same as forward for left movement
      break;
    case RIGHT:
      stepPattern = 7 - (currentStep % 8); // Same as backward for right movement
      break;
    default:
      stepPattern = 0;
      break;
  }
  
  // Apply step pattern to motor pins
  digitalWrite(IN1_PIN, stepSequence[stepPattern][0]);
  digitalWrite(IN2_PIN, stepSequence[stepPattern][1]);
  digitalWrite(IN3_PIN, stepSequence[stepPattern][2]);
  digitalWrite(IN4_PIN, stepSequence[stepPattern][3]);
  
  // Move to the next step
  currentStep++;
}

void stopMotor() {
  currentState = STOPPED;
  totalSteps = 0;
  currentStep = 0;
  targetSteps = 0;
  
  // Turn off all motor pins
  digitalWrite(IN1_PIN, LOW);
  digitalWrite(IN2_PIN, LOW);
  digitalWrite(IN3_PIN, LOW);
  digitalWrite(IN4_PIN, LOW);
  
  Serial.println("Motor STOPPED");
}

void sendStatus() {
  Serial.println("=== ARDUINO R4 STATUS ===");
  Serial.print("State: ");
  Serial.println(getDirectionName(currentState));
  Serial.print("Current Step: ");
  Serial.println(currentStep);
  Serial.print("Total Steps: ");
  Serial.println(totalSteps);
  Serial.print("Pi Connected: ");
  Serial.println(piConnected ? "YES" : "NO");
  Serial.print("Commands Received: ");
  Serial.println(commandCount);
  Serial.print("Step Delay: ");
  Serial.print(stepDelay);
  Serial.println("ms");
  Serial.print("Uptime: ");
  Serial.print(millis() / 1000);
  Serial.println(" seconds");
  Serial.println("========================");
}

String getDirectionName(MotorState state) {
  switch (state) {
    case STOPPED: return "STOPPED";
    case FORWARD: return "FORWARD";
    case BACKWARD: return "BACKWARD";
    case LEFT: return "LEFT";
    case RIGHT: return "RIGHT";
    default: return "UNKNOWN";
  }
}

void blinkLED(int times, int delayMs) {
  for (int i = 0; i < times; i++) {
    digitalWrite(STATUS_LED, HIGH);
    delay(delayMs);
    digitalWrite(STATUS_LED, LOW);
    delay(delayMs);
  }
}
