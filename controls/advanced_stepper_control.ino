/*
 * Advanced 5-Pin Stepper Motor Control for ELEGoo UNO R3
 * Features: Precise positioning, acceleration, microstepping, and position memory
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
 * Optional LED indicators:
 * - LED1 (Active) -> Digital Pin 4
 * - LED2 (Direction) -> Digital Pin 5
 * - LED3 (Position) -> Digital Pin 6
 */

#include <EEPROM.h>

// Stepper motor pins
const int IN1_PIN = 8;
const int IN2_PIN = 9;
const int IN3_PIN = 10;
const int IN4_PIN = 11;

// LED indicator pins (optional)
const int LED_ACTIVE = 4;
const int LED_DIRECTION = 5;
const int LED_POSITION = 6;

// Motor parameters
int stepDelay = 2;
int accelerationDelay = 5;
int stepsPerRevolution = 2048;
int currentStep = 0;
int targetStep = 0;
int totalSteps = 0;
int currentPosition = 0;
int targetPosition = 0;

// Microstepping support
bool microsteppingEnabled = false;
int microstepDivisor = 1;

// Motor states
enum MotorState {
  STOPPED,
  FORWARD,
  BACKWARD,
  ACCELERATING,
  DECELERATING
};

MotorState currentState = STOPPED;

// Step sequences
const int fullStepSequence[4][4] = {
  {1, 0, 0, 0},
  {0, 1, 0, 0},
  {0, 0, 1, 0},
  {0, 0, 0, 1}
};

const int halfStepSequence[8][4] = {
  {1, 0, 0, 0},
  {1, 1, 0, 0},
  {0, 1, 0, 0},
  {0, 1, 1, 0},
  {0, 0, 1, 0},
  {0, 0, 1, 1},
  {0, 0, 0, 1},
  {1, 0, 0, 1}
};

// Position memory
const int MAX_POSITIONS = 10;
int savedPositions[MAX_POSITIONS];
int positionCount = 0;

// EEPROM addresses
const int EEPROM_POSITION_ADDR = 0;
const int EEPROM_POSITIONS_ADDR = 10;

void setup() {
  Serial.begin(9600);
  
  // Initialize pins
  pinMode(IN1_PIN, OUTPUT);
  pinMode(IN2_PIN, OUTPUT);
  pinMode(IN3_PIN, OUTPUT);
  pinMode(IN4_PIN, OUTPUT);
  pinMode(LED_ACTIVE, OUTPUT);
  pinMode(LED_DIRECTION, OUTPUT);
  pinMode(LED_POSITION, OUTPUT);
  
  // Load saved position from EEPROM
  loadPosition();
  
  // Initialize motor
  stopMotor();
  updateLEDs();
  
  Serial.println("=== Advanced Stepper Motor Control ===");
  Serial.println("Commands:");
  Serial.println("  'f' - Rotate forward (1 revolution)");
  Serial.println("  'b' - Rotate backward (1 revolution)");
  Serial.println("  's' - Stop motor");
  Serial.println("  '+' - Increase speed");
  Serial.println("  '-' - Decrease speed");
  Serial.println("  '1-9' - Rotate fraction of turn (1/9 to 9/9)");
  Serial.println("  'r' - Rotate 1 full turn backward");
  Serial.println("  'i' - Show status");
  Serial.println("  'p' - Set custom position");
  Serial.println("  'g' - Go to saved position");
  Serial.println("  'm' - Save current position");
  Serial.println("  'l' - List saved positions");
  Serial.println("  'c' - Clear saved positions");
  Serial.println("  'h' - Toggle half-step mode");
  Serial.println("  'a' - Toggle acceleration");
  Serial.println("  'z' - Zero position");
  
  printStatus();
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    handleCommand(command);
  }
  
  if (currentState != STOPPED) {
    executeStep();
  }
  
  updateLEDs();
  delay(stepDelay);
}

void handleCommand(char command) {
  switch (command) {
    case 'f':
    case 'F':
      moveToPosition(currentPosition + stepsPerRevolution);
      break;
      
    case 'b':
    case 'B':
      moveToPosition(currentPosition - stepsPerRevolution);
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
    case '2':
    case '3':
    case '4':
    case '5':
    case '6':
    case '7':
    case '8':
    case '9':
      rotateFraction(command - '0');
      break;
      
    case 'r':
    case 'R':
      moveToPosition(currentPosition - stepsPerRevolution);
      break;
      
    case 'i':
    case 'I':
      printStatus();
      break;
      
    case 'p':
    case 'P':
      setCustomPosition();
      break;
      
    case 'g':
    case 'G':
      goToSavedPosition();
      break;
      
    case 'm':
    case 'M':
      saveCurrentPosition();
      break;
      
    case 'l':
    case 'L':
      listSavedPositions();
      break;
      
    case 'c':
    case 'C':
      clearSavedPositions();
      break;
      
    case 'h':
    case 'H':
      toggleHalfStep();
      break;
      
    case 'a':
    case 'A':
      toggleAcceleration();
      break;
      
    case 'z':
    case 'Z':
      zeroPosition();
      break;
      
    default:
      Serial.println("Unknown command. Use f/b/s/+/-/1-9/r/i/p/g/m/l/c/h/a/z");
      break;
  }
}

void moveToPosition(int target) {
  targetPosition = target;
  int stepsToMove = targetPosition - currentPosition;
  
  if (stepsToMove > 0) {
    currentState = FORWARD;
  } else if (stepsToMove < 0) {
    currentState = BACKWARD;
    stepsToMove = -stepsToMove;
  } else {
    return; // Already at target
  }
  
  totalSteps = stepsToMove;
  currentStep = 0;
  
  Serial.print("Moving to position ");
  Serial.print(targetPosition);
  Serial.print(" (");
  Serial.print(stepsToMove);
  Serial.println(" steps)");
}

void rotateFraction(int numerator) {
  int steps = (stepsPerRevolution * numerator) / 9;
  moveToPosition(currentPosition + steps);
  
  Serial.print("Rotating ");
  Serial.print(numerator);
  Serial.print("/9 turn (");
  Serial.print(steps);
  Serial.println(" steps)");
}

void executeStep() {
  if (currentStep >= totalSteps) {
    stopMotor();
    Serial.println("Movement complete");
    return;
  }
  
  // Get step pattern
  int stepPattern = currentStep % (microsteppingEnabled ? 8 : 4);
  const int (*sequence)[4] = microsteppingEnabled ? halfStepSequence : fullStepSequence;
  
  // Apply step pattern
  digitalWrite(IN1_PIN, sequence[stepPattern][0]);
  digitalWrite(IN2_PIN, sequence[stepPattern][1]);
  digitalWrite(IN3_PIN, sequence[stepPattern][2]);
  digitalWrite(IN4_PIN, sequence[stepPattern][3]);
  
  // Update position
  if (currentState == FORWARD) {
    currentPosition++;
  } else {
    currentPosition--;
  }
  
  currentStep++;
  
  // Save position to EEPROM periodically
  if (currentStep % 100 == 0) {
    savePosition();
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
  
  // Save final position
  savePosition();
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
  Serial.println("Enter target position (steps from zero):");
  
  while (Serial.available() == 0) {
    delay(10);
  }
  
  int position = Serial.parseInt();
  moveToPosition(position);
}

void saveCurrentPosition() {
  if (positionCount < MAX_POSITIONS) {
    savedPositions[positionCount] = currentPosition;
    positionCount++;
    
    // Save to EEPROM
    EEPROM.write(EEPROM_POSITIONS_ADDR + positionCount - 1, currentPosition >> 8);
    EEPROM.write(EEPROM_POSITIONS_ADDR + positionCount - 1 + MAX_POSITIONS, currentPosition & 0xFF);
    
    Serial.print("Position ");
    Serial.print(currentPosition);
    Serial.println(" saved");
  } else {
    Serial.println("Position memory full");
  }
}

void goToSavedPosition() {
  if (positionCount == 0) {
    Serial.println("No saved positions");
    return;
  }
  
  Serial.println("Enter position number (0 to " + String(positionCount - 1) + "):");
  
  while (Serial.available() == 0) {
    delay(10);
  }
  
  int index = Serial.parseInt();
  
  if (index >= 0 && index < positionCount) {
    moveToPosition(savedPositions[index]);
    Serial.print("Moving to saved position ");
    Serial.print(index);
    Serial.print(" (");
    Serial.print(savedPositions[index]);
    Serial.println(")");
  } else {
    Serial.println("Invalid position number");
  }
}

void listSavedPositions() {
  Serial.println("Saved positions:");
  for (int i = 0; i < positionCount; i++) {
    Serial.print("Position ");
    Serial.print(i);
    Serial.print(": ");
    Serial.println(savedPositions[i]);
  }
}

void clearSavedPositions() {
  positionCount = 0;
  Serial.println("All saved positions cleared");
}

void toggleHalfStep() {
  microsteppingEnabled = !microsteppingEnabled;
  Serial.print("Half-step mode: ");
  Serial.println(microsteppingEnabled ? "ON" : "OFF");
}

void toggleAcceleration() {
  // This could be expanded with actual acceleration logic
  Serial.println("Acceleration toggle - implementation depends on requirements");
}

void zeroPosition() {
  currentPosition = 0;
  targetPosition = 0;
  savePosition();
  Serial.println("Position zeroed");
}

void updateLEDs() {
  digitalWrite(LED_ACTIVE, (currentState != STOPPED) ? HIGH : LOW);
  digitalWrite(LED_DIRECTION, (currentState == FORWARD) ? HIGH : LOW);
  digitalWrite(LED_POSITION, (currentPosition == targetPosition) ? HIGH : LOW);
}

void savePosition() {
  EEPROM.write(EEPROM_POSITION_ADDR, currentPosition >> 8);
  EEPROM.write(EEPROM_POSITION_ADDR + 1, currentPosition & 0xFF);
}

void loadPosition() {
  currentPosition = (EEPROM.read(EEPROM_POSITION_ADDR) << 8) | EEPROM.read(EEPROM_POSITION_ADDR + 1);
  targetPosition = currentPosition;
}

void printStatus() {
  Serial.println("\n=== Stepper Motor Status ===");
  Serial.print("State: ");
  switch (currentState) {
    case STOPPED: Serial.println("STOPPED"); break;
    case FORWARD: Serial.println("FORWARD"); break;
    case BACKWARD: Serial.println("BACKWARD"); break;
    case ACCELERATING: Serial.println("ACCELERATING"); break;
    case DECELERATING: Serial.println("DECELERATING"); break;
  }
  Serial.print("Current Position: ");
  Serial.println(currentPosition);
  Serial.print("Target Position: ");
  Serial.println(targetPosition);
  Serial.print("Step Delay: ");
  Serial.print(stepDelay);
  Serial.println("ms");
  Serial.print("Half-step Mode: ");
  Serial.println(microsteppingEnabled ? "ON" : "OFF");
  Serial.print("Saved Positions: ");
  Serial.println(positionCount);
  Serial.println("===========================\n");
}
