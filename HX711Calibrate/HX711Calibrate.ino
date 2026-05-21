#include "HX711.h"
#include <EEPROM.h>

#define DOUT 3
#define CLK  2
#define EEPROM_ADDR 0

HX711 scale;

float calibrationFactor = 1.0;

// Stability settings
const int NUM_SAMPLES = 20;
const long STABILITY_THRESHOLD = 150; // Lower = stricter

// --------------------------------------------------
// Wait until readings are stable
// --------------------------------------------------
long getStableReading() {
  long readings[NUM_SAMPLES];

  Serial.println("Waiting for stable weight...");

  // Fill buffer
  for (int i = 0; i < NUM_SAMPLES; i++) {
    readings[i] = scale.read();
    delay(100);
  }

  while (true) {
    // Shift left
    for (int i = 0; i < NUM_SAMPLES - 1; i++) {
      readings[i] = readings[i + 1];
    }

    // New reading
    readings[NUM_SAMPLES - 1] = scale.read();

    long minVal = readings[0];
    long maxVal = readings[0];
    long sum = 0;

    for (int i = 0; i < NUM_SAMPLES; i++) {
      if (readings[i] < minVal) minVal = readings[i];
      if (readings[i] > maxVal) maxVal = readings[i];
      sum += readings[i];
    }

    long spread = maxVal - minVal;

    Serial.print("Stability spread: ");
    Serial.println(spread);

    if (spread <= STABILITY_THRESHOLD) {
      Serial.println("Weight stabilized.");
      return sum / NUM_SAMPLES;
    }

    delay(100);
  }
}

// --------------------------------------------------
// Automatic calibration
// --------------------------------------------------
void calibrateScale() {
  Serial.println("\n=== HX711 AUTO CALIBRATION ===");
  Serial.println("Remove all weight from the scale.");
  Serial.println("Press ENTER when ready.");

  while (Serial.available()) Serial.read();
  while (Serial.available() == 0);
  while (Serial.available()) Serial.read();

  Serial.println("Taring...");
  scale.tare();
  Serial.println("Scale tared successfully.");

  Serial.println("\nEnter known weight in grams:");
  while (Serial.available() == 0);

  float knownWeight = Serial.parseFloat();

  while (knownWeight <= 0) {
    Serial.println("Invalid value. Enter a weight greater than 0:");
    while (Serial.available() == 0);
    knownWeight = Serial.parseFloat();
  }

  while (Serial.available()) Serial.read();

  Serial.print("Place ");
  Serial.print(knownWeight, 2);
  Serial.println(" g on the scale.");

  long stableRaw = getStableReading();

  calibrationFactor = (stableRaw - scale.get_offset()) / knownWeight;
  scale.set_scale(calibrationFactor);

  EEPROM.put(EEPROM_ADDR, calibrationFactor);

  Serial.println("\nCalibration complete!");
  Serial.print("Calibration factor: ");
  Serial.println(calibrationFactor, 6);
  Serial.println("Saved to EEPROM.");
  Serial.println();
}

void setup() {
  Serial.begin(9600);
  scale.begin(DOUT, CLK);

  EEPROM.get(EEPROM_ADDR, calibrationFactor);

  if (isnan(calibrationFactor) || calibrationFactor == 0.0f) {
    calibrationFactor = 1.0f;
  }

  scale.set_scale(calibrationFactor);

  calibrateScale();
}

void loop() {
  if (scale.is_ready()) {
    float weight = scale.get_units(10);

    Serial.print("Weight: ");
    Serial.print(weight, 2);
    Serial.println(" g");
  } else {
    Serial.println("HX711 not found.");
  }

  delay(500);
}