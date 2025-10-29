/*
 * Simple motor test sketch
 * Tests each motor pin individually
 */

void setup() {
  Serial.begin(9600);
  
  // Set all motor pins as outputs
  for(int i = 4; i <= 11; i++) {
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }
  
  Serial.println("Motor test ready");
  Serial.println("Commands: l=left motor, r=right motor, p#=test pin #");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readString();
    command.trim();
    
    if (command == "l") {
      // Test left motor (pins 8-11)
      Serial.println("Testing LEFT motor...");
      testMotor(8, 9, 10, 11);
    }
    else if (command == "r") {
      // Test right motor (pins 4-7)
      Serial.println("Testing RIGHT motor...");
      testMotor(4, 5, 6, 7);
    }
    else if (command.startsWith("p")) {
      // Test individual pin
      int pin = command.substring(1).toInt();
      if (pin >= 4 && pin <= 11) {
        Serial.println("Testing pin " + String(pin));
        testPin(pin);
      }
    }
  }
}

void testMotor(int pin1, int pin2, int pin3, int pin4) {
  // Simple step sequence for testing
  int pins[] = {pin1, pin2, pin3, pin4};
  
  for (int step = 0; step < 8; step++) {
    // Turn on one pin at a time
    for (int i = 0; i < 4; i++) {
      digitalWrite(pins[i], (step == i) ? HIGH : LOW);
    }
    delay(100);
  }
  
  // Turn all off
  for (int i = 0; i < 4; i++) {
    digitalWrite(pins[i], LOW);
  }
  
  Serial.println("Motor test complete");
}

void testPin(int pin) {
  // Blink the pin 5 times
  for (int i = 0; i < 5; i++) {
    digitalWrite(pin, HIGH);
    delay(200);
    digitalWrite(pin, LOW);
    delay(200);
  }
  Serial.println("Pin test complete");
}
