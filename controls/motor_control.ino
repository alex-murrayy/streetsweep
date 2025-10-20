/*
 * Motor Control for ELEGoo UNO R3
 * Controls a DC motor with speed and direction control
 * 
 * Wiring:
 * - Motor driver IN1 -> Digital Pin 2
 * - Motor driver IN2 -> Digital Pin 3  
 * - Motor driver ENA -> Digital Pin 9 (PWM)
 * - Motor driver VCC -> 5V
 * - Motor driver GND -> GND
 * - Motor driver VM -> External power supply (6-12V)
 * - Motor connected to OUT1 and OUT2 of motor driver
 */

// Motor control pins
const int IN1_PIN = 2;    // Motor direction pin 1
const int IN2_PIN = 3;    // Motor direction pin 2
const int ENA_PIN = 9;    // Motor speed control (PWM)

// Motor speed (0-255)
int motorSpeed = 150;

// Motor direction states
enum MotorDirection {
  STOP,
  FORWARD,
  BACKWARD
};

MotorDirection currentDirection = STOP;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Set motor control pins as outputs
  pinMode(IN1_PIN, OUTPUT);
  pinMode(IN2_PIN, OUTPUT);
  pinMode(ENA_PIN, OUTPUT);
  
  // Initialize motor in stopped state
  stopMotor();
  
  Serial.println("Motor Control System Initialized");
  Serial.println("Commands:");
  Serial.println("  'f' - Forward");
  Serial.println("  'b' - Backward");
  Serial.println("  's' - Stop");
  Serial.println("  '+' - Increase speed");
  Serial.println("  '-' - Decrease speed");
  Serial.println("  '0-9' - Set speed (0-9, where 9 = max speed)");
}

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    char command = Serial.read();
    handleCommand(command);
  }
  
  // Small delay to prevent overwhelming the serial buffer
  delay(10);
}

void handleCommand(char command) {
  switch (command) {
    case 'f':
    case 'F':
      moveForward();
      break;
      
    case 'b':
    case 'B':
      moveBackward();
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
      setSpeed(command - '0');
      break;
      
    default:
      Serial.println("Unknown command. Use f/b/s/+/-/0-9");
      break;
  }
}

void moveForward() {
  digitalWrite(IN1_PIN, HIGH);
  digitalWrite(IN2_PIN, LOW);
  analogWrite(ENA_PIN, motorSpeed);
  currentDirection = FORWARD;
  Serial.print("Moving FORWARD at speed: ");
  Serial.println(motorSpeed);
}

void moveBackward() {
  digitalWrite(IN1_PIN, LOW);
  digitalWrite(IN2_PIN, HIGH);
  analogWrite(ENA_PIN, motorSpeed);
  currentDirection = BACKWARD;
  Serial.print("Moving BACKWARD at speed: ");
  Serial.println(motorSpeed);
}

void stopMotor() {
  digitalWrite(IN1_PIN, LOW);
  digitalWrite(IN2_PIN, LOW);
  analogWrite(ENA_PIN, 0);
  currentDirection = STOP;
  Serial.println("Motor STOPPED");
}

void increaseSpeed() {
  if (motorSpeed < 255) {
    motorSpeed += 25;
    if (motorSpeed > 255) motorSpeed = 255;
    
    // Update current motor speed if motor is running
    if (currentDirection != STOP) {
      analogWrite(ENA_PIN, motorSpeed);
    }
    
    Serial.print("Speed increased to: ");
    Serial.println(motorSpeed);
  } else {
    Serial.println("Already at maximum speed");
  }
}

void decreaseSpeed() {
  if (motorSpeed > 0) {
    motorSpeed -= 25;
    if (motorSpeed < 0) motorSpeed = 0;
    
    // Update current motor speed if motor is running
    if (currentDirection != STOP) {
      analogWrite(ENA_PIN, motorSpeed);
    }
    
    Serial.print("Speed decreased to: ");
    Serial.println(motorSpeed);
  } else {
    Serial.println("Already at minimum speed");
  }
}

void setSpeed(int speedLevel) {
  // Convert 0-9 scale to 0-255 PWM range
  motorSpeed = map(speedLevel, 0, 9, 0, 255);
  
  // Update current motor speed if motor is running
  if (currentDirection != STOP) {
    analogWrite(ENA_PIN, motorSpeed);
  }
  
  Serial.print("Speed set to level ");
  Serial.print(speedLevel);
  Serial.print(" (PWM: ");
  Serial.print(motorSpeed);
  Serial.println(")");
}
