/*
 * 5-Pin Stepper Motor Control for ELEGoo UNO R3
 * Controls a 5-pin stepper motor with ULN2003 driver
 * 
 * Wiring for ULN2003 Stepper Motor Driver:
 * - IN1 -> Digital Pin 8
 * - IN2 -> Digital Pin 9
 * - IN3 -> Digital Pin 10
 * - IN4 -> Digital Pin 11
 * - VCC -> 5V
 * - GND -> GND
 * - Motor center tap -> VCC (5V)
 * - Motor coils -> OUT1, OUT2, OUT3, OUT4
 * 
 * Stepper Motor: 28BYJ-48 (5V, 4-phase, 1/64 gear ratio)
 */

// Stepper motor pins
const int IN1_PIN = 8;
const int IN2_PIN = 9;
const int IN3_PIN = 10;
const int IN4_PIN = 11;

// Motor parameters
int stepDelay = 2;  // Delay between steps (milliseconds)
int stepsPerRevolution = 2048;  // 28BYJ-48 has 2048 steps per revolution
int currentStep = 0;
int totalSteps = 0;

// Motor states
enum MotorState {
  STOPPED,
  FORWARD,
  BACKWARD
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

void setup() {
  Serial.begin(9600);
  
  // Initialize stepper motor pins
  pinMode(IN1_PIN, OUTPUT);
  pinMode(IN2_PIN, OUTPUT);
  pinMode(IN3_PIN, OUTPUT);
  pinMode(IN4_PIN, OUTPUT);
  
  // Initialize motor in stopped state
  stopMotor();
  
  Serial.println("=== 5-Pin Stepper Motor Control ===");
  Serial.println("Commands:");
  Serial.println("  'f' - Rotate forward (1 revolution)");
  Serial.println("  'b' - Rotate backward (1 revolution)");
  Serial.println("  's' - Stop motor");
  Serial.println("  '+' - Increase speed (decrease delay)");
  Serial.println("  '-' - Decrease speed (increase delay)");
  Serial.println("  '1' - Rotate 1/4 turn forward");
  Serial.println("  '2' - Rotate 1/2 turn forward");
  Serial.println("  '3' - Rotate 3/4 turn forward");
  Serial.println("  '4' - Rotate 1 full turn forward");
  Serial.println("  'r' - Rotate 1 full turn backward");
  Serial.println("  'c' - Rotate 1/4 turn backward");
  Serial.println("  'h' - Rotate 1/2 turn backward");
  Serial.println("  't' - Rotate 3/4 turn backward");
  Serial.println("  'i' - Show status");
  Serial.println("  'p' - Set custom position");
  
  printStatus();
}

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    char command = Serial.read();
    handleCommand(command);
  }
  
  // Execute motor movement if not stopped
  if (currentState != STOPPED) {
    executeStep();
  }
  
  delay(stepDelay);
}

void handleCommand(char command) {
  switch (command) {
    case 'f':
    case 'F':
      rotateSteps(stepsPerRevolution, FORWARD);
      break;
      
    case 'b':
    case 'B':
      rotateSteps(stepsPerRevolution, BACKWARD);
      break;
      
    case 's':
    case 'S':
      stopMotor();
      break;
      
    case '+':
      increaseSpeed();
      break;
      
    case '-':
      decreaseSpeed();
      break;
      
    case '1':
      rotateSteps(stepsPerRevolution / 4, FORWARD);
      break;
      
    case '2':
      rotateSteps(stepsPerRevolution / 2, FORWARD);
      break;
      
    case '3':
      rotateSteps((stepsPerRevolution * 3) / 4, FORWARD);
      break;
      
    case '4':
      rotateSteps(stepsPerRevolution, FORWARD);
      break;
      
    case 'r':
      rotateSteps(stepsPerRevolution, BACKWARD);
      break;
      
    case 'c':
      rotateSteps(stepsPerRevolution / 4, BACKWARD);
      break;
      
    case 'h':
      rotateSteps(stepsPerRevolution / 2, BACKWARD);
      break;
      
    case 't':
      rotateSteps((stepsPerRevolution * 3) / 4, BACKWARD);
      break;
      
    case 'i':
    case 'I':
      printStatus();
      break;
      
    case 'p':
    case 'P':
      setCustomPosition();
      break;
      
    default:
      Serial.println("Unknown command. Use f/b/s/+/-/1/2/3/4/r/c/h/t/i/p");
      break;
  }
}

void rotateSteps(int steps, MotorState direction) {
  if (steps <= 0) return;
  
  currentState = direction;
  totalSteps = steps;
  currentStep = 0;
  
  Serial.print("Rotating ");
  Serial.print(steps);
  Serial.print(" steps ");
  Serial.println(direction == FORWARD ? "FORWARD" : "BACKWARD");
}

void executeStep() {
  if (currentStep >= totalSteps) {
    stopMotor();
    Serial.println("Rotation complete");
    return;
  }
  
  // Get current step pattern
  int stepPattern = currentStep % 8;
  
  // Apply step pattern to motor pins
  digitalWrite(IN1_PIN, stepSequence[stepPattern][0]);
  digitalWrite(IN2_PIN, stepSequence[stepPattern][1]);
  digitalWrite(IN3_PIN, stepSequence[stepPattern][2]);
  digitalWrite(IN4_PIN, stepSequence[stepPattern][3]);
  
  // Move to next step
  if (currentState == FORWARD) {
    currentStep++;
  } else if (currentState == BACKWARD) {
    currentStep++;
    // For backward, we'll reverse the sequence in the next iteration
  }
}

void stopMotor() {
  currentState = STOPPED;
  totalSteps = 0;
  currentStep = 0;
  
  // Turn off all motor pins
  digitalWrite(IN1_PIN, LOW);
  digitalWrite(IN2_PIN, LOW);
  digitalWrite(IN3_PIN, LOW);
  digitalWrite(IN4_PIN, LOW);
  
  Serial.println("Motor STOPPED");
}

void increaseSpeed() {
  if (stepDelay > 1) {
    stepDelay--;
    Serial.print("Speed increased. Delay: ");
    Serial.print(stepDelay);
    Serial.println("ms");
  } else {
    Serial.println("Already at maximum speed");
  }
}

void decreaseSpeed() {
  if (stepDelay < 10) {
    stepDelay++;
    Serial.print("Speed decreased. Delay: ");
    Serial.print(stepDelay);
    Serial.println("ms");
  } else {
    Serial.println("Already at minimum speed");
  }
}

void setCustomPosition() {
  Serial.println("Enter number of steps (positive for forward, negative for backward):");
  
  // Wait for user input
  while (Serial.available() == 0) {
    delay(10);
  }
  
  int steps = Serial.parseInt();
  
  if (steps > 0) {
    rotateSteps(steps, FORWARD);
  } else if (steps < 0) {
    rotateSteps(-steps, BACKWARD);
  } else {
    Serial.println("Invalid input");
  }
}

void printStatus() {
  Serial.println("\n=== Stepper Motor Status ===");
  Serial.print("State: ");
  switch (currentState) {
    case STOPPED: Serial.println("STOPPED"); break;
    case FORWARD: Serial.println("FORWARD"); break;
    case BACKWARD: Serial.println("BACKWARD"); break;
  }
  Serial.print("Current Step: ");
  Serial.println(currentStep);
  Serial.print("Total Steps: ");
  Serial.println(totalSteps);
  Serial.print("Step Delay: ");
  Serial.print(stepDelay);
  Serial.println("ms");
  Serial.print("Steps per Revolution: ");
  Serial.println(stepsPerRevolution);
  Serial.println("=======================\n");
}
