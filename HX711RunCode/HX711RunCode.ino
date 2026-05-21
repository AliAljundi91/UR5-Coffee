#include "HX711.h"
#include <EEPROM.h>

#define DOUT 3
#define CLK  2
#define EEPROM_ADDR 0

HX711 scale;

float calibrationFactor = 1.0;

void setup() {
  Serial.begin(115200);

  scale.begin(DOUT, CLK);

  EEPROM.get(EEPROM_ADDR, calibrationFactor);

  if (isnan(calibrationFactor) || calibrationFactor == 0.0f) {
    calibrationFactor = 1.0f;
  }

  scale.set_scale(calibrationFactor);

  Serial.println("READY");
}

void loop() {

  // handle commands from Python
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "TARE") {
      scale.tare();
      Serial.println("TARED");
    }
  }

  if (scale.is_ready()) {
    float weight = scale.get_units(1);

    Serial.print("Weight:");
    Serial.println(weight, 2);
  }

  delay(10);
}