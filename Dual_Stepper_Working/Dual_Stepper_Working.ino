/*
 * Dual 28BYJ-48 (ULN2003) "rear wheels" with WASD drive on Arduino Uno
 * Power motors from a regulated 5V (>=2A) supply. Tie ALL grounds together.
 *
 * Pins:
 *   Motor Left  (A): IN1..IN4 → 8, 9, 10, 11
 *   Motor Right (B): IN1..IN4 → 4, 5, 6, 7
 *
 * Controls (Serial Monitor @ 9600 baud):
 *   W = forward        S = reverse
 *   A = pivot left     D = pivot right
 *   X or ' ' (space) = stop
 *   Q = slower         E = faster
 *   1..5 = speed presets (lowest→highest)
 */

 // ---------- Config ----------
const int stepsPerRev = 2048;     // 28BYJ-48 (half-steps)
const int MIN_SPS = 100;          // min steps/sec
const int MAX_SPS = 1600;         // max steps/sec (go higher only if your rig can handle it)
int baseSPS = 800;                // default steps/sec (speed preset)

 // ---------- Pin maps ----------
const int leftPins[4]  = {8, 9, 10, 11}; // Left wheel (Motor A)
const int rightPins[4] = {4, 5, 6, 7};   // Right wheel (Motor B)

// 8-step half-step sequence
const uint8_t seq[8][4] = {
  {1,0,0,0}, {1,1,0,0}, {0,1,0,0}, {0,1,1,0},
  {0,0,1,0}, {0,0,1,1}, {0,0,0,1}, {1,0,0,1}
};

struct Wheel {
  const int* pins;                    // 4-pin array
  int idx = 0;                        // current sequence index 0..7
  int sps = 0;                        // signed steps/sec (direction in sign)
  unsigned long lastStepUs = 0;       // last step timestamp
  unsigned long intervalUs = 0;       // microseconds between steps (abs)
  bool energized = false;             // coils currently driven
};

Wheel left;
Wheel right;

void setupWheels() {
  left.pins  = leftPins;
  left.idx   = 0;
  left.sps   = 0;
  left.lastStepUs = 0;
  left.intervalUs = 0;
  left.energized  = false;

  right.pins  = rightPins;
  right.idx   = 0;
  right.sps   = 0;
  right.lastStepUs = 0;
  right.intervalUs = 0;
  right.energized  = false;
}

// ---------- Helpers ----------
void pinsModeOut(const int p[4]) {
  for (int i=0; i<4; i++) pinMode(p[i], OUTPUT);
}
void coilsOff(const int p[4]) {
  for (int i=0; i<4; i++) digitalWrite(p[i], LOW);
}
inline unsigned long spsToIntervalUs(int spsAbs) {
  if (spsAbs < 1) spsAbs = 1; // avoid div0
  return (unsigned long)(1000000UL / (unsigned long)spsAbs);
}

// Set wheel speed in steps/sec (signed: + = forward, - = backward, 0 = stop)
void setWheelSpeed(Wheel &w, int sps) {
  w.sps = sps;
  int a = abs(sps);
  if (a == 0) {
    coilsOff(w.pins);
    w.energized = false;
    w.intervalUs = 0;
  } else {
    if (a < MIN_SPS) a = MIN_SPS;
    if (a > MAX_SPS) a = MAX_SPS;
    w.intervalUs = spsToIntervalUs(a);
    if (!w.energized) {
      // Energize with current pattern so the first step has valid state
      for (int i=0; i<4; i++) digitalWrite(w.pins[i], seq[w.idx][i]);
      w.energized = true;
      w.lastStepUs = micros();
    }
  }
}

// Service one wheel: step when time interval elapsed
void serviceWheel(Wheel &w) {
  if (w.sps == 0) return;
  unsigned long now = micros();
  if ((unsigned long)(now - w.lastStepUs) < w.intervalUs) return;
  w.lastStepUs = now;

  // Direction: +1 for forward, -1 for backward
  int delta = (w.sps > 0) ? 1 : -1;
  w.idx = (w.idx + delta) & 0x7;  // wrap 0..7 quickly

  // Output new pattern
  for (int i=0; i<4; i++) digitalWrite(w.pins[i], seq[w.idx][i]);
}

// High-level driving modes
void driveStop() {
  setWheelSpeed(left, 0);
  setWheelSpeed(right, 0);
  Serial.println("STOP");
}

void driveForward() {
  setWheelSpeed(left,  +baseSPS);
  setWheelSpeed(right, +baseSPS);
  Serial.print("FORWARD @ "); Serial.print(baseSPS); Serial.println(" sps");
}

void driveReverse() {
  setWheelSpeed(left,  -baseSPS);
  setWheelSpeed(right, -baseSPS);
  Serial.print("REVERSE @ "); Serial.print(baseSPS); Serial.println(" sps");
}

void drivePivotLeft() {   // left wheel backward, right forward
  setWheelSpeed(left,  -baseSPS);
  setWheelSpeed(right, +baseSPS);
  Serial.print("PIVOT LEFT @ "); Serial.print(baseSPS); Serial.println(" sps");
}

void drivePivotRight() {  // left wheel forward, right backward
  setWheelSpeed(left,  +baseSPS);
  setWheelSpeed(right, -baseSPS);
  Serial.print("PIVOT RIGHT @ "); Serial.print(baseSPS); Serial.println(" sps");
}

void printHelp() {
  Serial.println("\n=== WASD Drive ===");
  Serial.println("W forward | S reverse | A pivot left | D pivot right");
  Serial.println("X or Space = stop | Q slower | E faster | 1..5 speed presets");
  Serial.print("Current speed preset (steps/sec): "); Serial.println(baseSPS);
  Serial.println("===================\n");
}

// ---------- Arduino ----------
void setup() {
  setupWheels();
  Serial.begin(9600);
  pinsModeOut(left.pins);
  pinsModeOut(right.pins);
  coilsOff(left.pins);
  coilsOff(right.pins);
  printHelp();
}

void loop() {
  // keyboard input
  if (Serial.available() > 0) {
    char c = Serial.read();
    switch (c) {
      case 'w': case 'W': driveForward(); break;
      case 's': case 'S': driveReverse(); break;
      case 'a': case 'A': drivePivotLeft(); break;
      case 'd': case 'D': drivePivotRight(); break;
      case 'x': case 'X': case ' ': driveStop(); break;

      // speed trim
      case 'q': case 'Q':
        baseSPS -= 100;
        if (baseSPS < MIN_SPS) baseSPS = MIN_SPS;
        Serial.print("Speed ↓ -> "); Serial.println(baseSPS);
        // if moving, update to new speed
        if (left.sps  != 0) setWheelSpeed(left,  (left.sps  > 0 ? +baseSPS : -baseSPS));
        if (right.sps != 0) setWheelSpeed(right, (right.sps > 0 ? +baseSPS : -baseSPS));
        break;

      case 'e': case 'E':
        baseSPS += 100;
        if (baseSPS > MAX_SPS) baseSPS = MAX_SPS;
        Serial.print("Speed ↑ -> "); Serial.println(baseSPS);
        if (left.sps  != 0) setWheelSpeed(left,  (left.sps  > 0 ? +baseSPS : -baseSPS));
        if (right.sps != 0) setWheelSpeed(right, (right.sps > 0 ? +baseSPS : -baseSPS));
        break;

      // speed presets
      case '1': baseSPS = 300;  Serial.println("Preset 1 -> 300 sps");  break;
      case '2': baseSPS = 600;  Serial.println("Preset 2 -> 600 sps");  break;
      case '3': baseSPS = 800;  Serial.println("Preset 3 -> 800 sps");  break;
      case '4': baseSPS = 1000; Serial.println("Preset 4 -> 1000 sps"); break;
      case '5': baseSPS = 1200; Serial.println("Preset 5 -> 1200 sps"); break;

      case 'h': case 'H': printHelp(); break;
      default: /* ignore */ break;
    }
  }

  // service both wheels without blocking
  serviceWheel(left);
  serviceWheel(right);
}
