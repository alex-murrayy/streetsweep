/*
 * Advanced Motor Control for ELEGoo UNO R3
 * Features: Speed control, direction control, acceleration, and safety features
 * 
 * Wiring for L298N Motor Driver:
 * - IN1 -> Digital Pin 2
 * - IN2 -> Digital Pin 3
 * - ENA -> Digital Pin 9 (PWM)
 * - VCC -> 5V
 * - GND -> GND
 * - VM -> External power supply (6-12V)
 * - OUT1, OUT2 -> Motor terminals
 * 
 * Optional: Add LED indicators
 * - LED1 (Forward) -> Digital Pin 4
 * - LED2 (Backward) -> Digital Pin 5
 * - LED3 (Stop) -> Digital Pin 6
 */

#include <EEPROM.h>

// Motor control pins
const int IN1_PIN = 2;
const int IN2_PIN = 3;
const int ENA_PIN = 9;

// LED indicator pins (optional)
const int LED_FORWARD = 4;
const int LED_BACKWARD = 5;
const int LED_STOP = 6;

// Motor parameters
int currentSpeed = 0;
int targetSpeed = 0;
int maxSpeed = 255;
int minSpeed = 50;  // Minimum speed to overcome friction

// Acceleration parameters
const int ACCELERATION_STEP = 5;
const int ACCELERATION_DELAY = 50;  // milliseconds

// Motor direction states
enum MotorDirection {
  STOP,
  FORWARD,
  BACKWARD
};

MotorDirection currentDirection = STOP;
MotorDirection targetDirection = STOP;

// Safety features
bool emergencyStop = false;
unsigned long lastCommandTime = 0;
const unsigned long SAFETY_TIMEOUT = 30000;  // 30 seconds

// EEPROM addresses for storing settings
const int EEPROM_SPEED_ADDR = 0;
const int EEPROM_DIRECTION_ADDR = 1;

void setup() {
  Serial.begin(9600);
  
  // Initialize pins
  pinMode(IN1_PIN, OUTPUT);
  pinMode(IN2_PIN, OUTPUT);
  pinMode(ENA_PIN, OUTPUT);
  pinMode(LED_FORWARD, OUTPUT);
  pinMode(LED_BACKWARD, OUTPUT);
  pinMode(LED_STOP, OUTPUT);
  
  // Load saved settings from EEPROM
  loadSettings();
  
  // Initialize motor
  stopMotor();
  updateLEDs();
  
  Serial.println("=== Advanced Motor Control System ===");
  Serial.println("Commands:");
  Serial.println("  'f' - Forward");
  Serial.println("  'b' - Backward");
  Serial.println("  's' - Stop");
  Serial.println("  '+' - Increase speed");
  Serial.println("  '-' - Decrease speed");
  Serial.println("  '0-9' - Set speed (0-9)");
  Serial.println("  'e' - Emergency stop");
  Serial.println("  'r' - Reset to defaults");
  Serial.println("  'i' - Show info");
  Serial.println("  'a' - Auto-acceleration on/off");
  
  printStatus();
}

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    char command = Serial.read();
    handleCommand(command);
    lastCommandTime = millis();
  }
  
  // Handle acceleration
  if (currentSpeed != targetSpeed) {
    accelerateMotor();
  }
  
  // Safety timeout check
  if (millis() - lastCommandTime > SAFETY_TIMEOUT && !emergencyStop) {
    Serial.println("Safety timeout - stopping motor");
    emergencyStopMotor();
  }
  
  // Update LEDs
  updateLEDs();
  
  delay(10);
}

void handleCommand(char command) {
  if (emergencyStop && command != 'e' && command != 'r') {
    Serial.println("Emergency stop active. Press 'e' to reset or 'r' to reset all.");
    return;
  }
  
  switch (command) {
    case 'f':
    case 'F':
      setDirection(FORWARD);
      break;
      
    case 'b':
    case 'B':
      setDirection(BACKWARD);
      break;
      
    case 's':
    case 'S':
      setDirection(STOP);
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
      
    case 'e':
    case 'E':
      if (emergencyStop) {
        emergencyStop = false;
        Serial.println("Emergency stop released");
      } else {
        emergencyStopMotor();
      }
      break;
      
    case 'r':
    case 'R':
      resetToDefaults();
      break;
      
    case 'i':
    case 'I':
      printStatus();
      break;
      
    case 'a':
    case 'A':
      toggleAutoAcceleration();
      break;
      
    default:
      Serial.println("Unknown command. Type 'i' for help.");
      break;
  }
}

void setDirection(MotorDirection direction) {
  if (emergencyStop) return;
  
  targetDirection = direction;
  
  switch (direction) {
    case FORWARD:
      digitalWrite(IN1_PIN, HIGH);
      digitalWrite(IN2_PIN, LOW);
      currentDirection = FORWARD;
      Serial.println("Direction: FORWARD");
      break;
      
    case BACKWARD:
      digitalWrite(IN1_PIN, LOW);
      digitalWrite(IN2_PIN, HIGH);
      currentDirection = BACKWARD;
      Serial.println("Direction: BACKWARD");
      break;
      
    case STOP:
      digitalWrite(IN1_PIN, LOW);
      digitalWrite(IN2_PIN, LOW);
      currentDirection = STOP;
      targetSpeed = 0;
      Serial.println("Direction: STOP");
      break;
  }
  
  saveSettings();
}

void setSpeedLevel(int level) {
  if (emergencyStop) return;
  
  targetSpeed = map(level, 0, 9, 0, maxSpeed);
  
  if (targetSpeed > 0 && targetSpeed < minSpeed) {
    targetSpeed = minSpeed;
  }
  
  Serial.print("Target speed set to level ");
  Serial.print(level);
  Serial.print(" (PWM: ");
  Serial.print(targetSpeed);
  Serial.println(")");
  
  saveSettings();
}

void increaseSpeed() {
  if (emergencyStop) return;
  
  targetSpeed += 25;
  if (targetSpeed > maxSpeed) targetSpeed = maxSpeed;
  
  Serial.print("Speed increased to: ");
  Serial.println(targetSpeed);
}

void decreaseSpeed() {
  if (emergencyStop) return;
  
  targetSpeed -= 25;
  if (targetSpeed < 0) targetSpeed = 0;
  
  Serial.print("Speed decreased to: ");
  Serial.println(targetSpeed);
}

void accelerateMotor() {
  if (currentSpeed < targetSpeed) {
    currentSpeed += ACCELERATION_STEP;
    if (currentSpeed > targetSpeed) currentSpeed = targetSpeed;
  } else if (currentSpeed > targetSpeed) {
    currentSpeed -= ACCELERATION_STEP;
    if (currentSpeed < targetSpeed) currentSpeed = targetSpeed;
  }
  
  analogWrite(ENA_PIN, currentSpeed);
  delay(ACCELERATION_DELAY);
}

void stopMotor() {
  digitalWrite(IN1_PIN, LOW);
  digitalWrite(IN2_PIN, LOW);
  analogWrite(ENA_PIN, 0);
  currentSpeed = 0;
  targetSpeed = 0;
  currentDirection = STOP;
  targetDirection = STOP;
}

void emergencyStopMotor() {
  stopMotor();
  emergencyStop = true;
  Serial.println("EMERGENCY STOP ACTIVATED!");
}

void updateLEDs() {
  digitalWrite(LED_FORWARD, (currentDirection == FORWARD) ? HIGH : LOW);
  digitalWrite(LED_BACKWARD, (currentDirection == BACKWARD) ? HIGH : LOW);
  digitalWrite(LED_STOP, (currentDirection == STOP || emergencyStop) ? HIGH : LOW);
}

void printStatus() {
  Serial.println("\n=== Motor Status ===");
  Serial.print("Direction: ");
  switch (currentDirection) {
    case FORWARD: Serial.println("FORWARD"); break;
    case BACKWARD: Serial.println("BACKWARD"); break;
    case STOP: Serial.println("STOPPED"); break;
  }
  Serial.print("Current Speed: ");
  Serial.println(currentSpeed);
  Serial.print("Target Speed: ");
  Serial.println(targetSpeed);
  Serial.print("Emergency Stop: ");
  Serial.println(emergencyStop ? "ACTIVE" : "INACTIVE");
  Serial.print("Uptime: ");
  Serial.print(millis() / 1000);
  Serial.println(" seconds");
  Serial.println("==================\n");
}

void loadSettings() {
  targetSpeed = EEPROM.read(EEPROM_SPEED_ADDR);
  targetDirection = (MotorDirection)EEPROM.read(EEPROM_DIRECTION_ADDR);
  
  // Validate loaded values
  if (targetSpeed > maxSpeed) targetSpeed = 0;
  if (targetDirection > BACKWARD) targetDirection = STOP;
}

void saveSettings() {
  EEPROM.write(EEPROM_SPEED_ADDR, targetSpeed);
  EEPROM.write(EEPROM_DIRECTION_ADDR, targetDirection);
}

void resetToDefaults() {
  targetSpeed = 0;
  targetDirection = STOP;
  emergencyStop = false;
  stopMotor();
  
  // Clear EEPROM
  EEPROM.write(EEPROM_SPEED_ADDR, 0);
  EEPROM.write(EEPROM_DIRECTION_ADDR, 0);
  
  Serial.println("Reset to defaults complete");
}

void toggleAutoAcceleration() {
  // This could be expanded to include acceleration settings
  Serial.println("Auto-acceleration feature - implementation depends on requirements");
}
