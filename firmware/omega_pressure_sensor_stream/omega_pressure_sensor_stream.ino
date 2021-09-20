#include <Adafruit_ADS1X15.h>

const long RS485_SERIAL_BAUD = 9600;

const uint8_t MAX485_RE = 4;  // MAX485 RE Pin connected to GPIO4
const uint8_t MAX485_DE = 7;  // MAX485 RE Pin connected to GPIO7

const uint8_t COMM_STATE_CHANGE_DELAY = 50;  // microseconds
const uint8_t COMM_TRANSMISSION_DELAY = 10;  // microseconds


Adafruit_ADS1015 PressueSensor;
size_t num_samples = 5;

unsigned long previousMillis = 0;
const long interval = 50; // === 20Hz (milliseconds)


// Gets the average of `num_samples` readings, discarding the min and max value
int16_t get_filtered_value() {
  int16_t _val = 0, _max = -32768, _min = 32767, sum = 0;
  for (int i = 0; i < num_samples; i++) {
    _val = PressueSensor.readADC_Differential_2_3();
    sum  += _val;
    if (_val >= _max) _max = _val;
    if (_val <= _min) _min = _val;
  }
  return ((sum - _max - _min) / (num_samples - 2));
}


void setup() {
  digitalWrite(MAX485_RE, LOW);
  digitalWrite(MAX485_DE, HIGH);
  delayMicroseconds(COMM_STATE_CHANGE_DELAY);

  PressueSensor.begin();
  Serial1.begin(RS485_SERIAL_BAUD);
  Serial1.println("Startin up...");
  rs485_delay();

  previousMillis = millis();
}

void loop() {
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    
    const long pres = get_filtered_value();
    Serial1.println(pres);
    delayMicroseconds(COMM_TRANSMISSION_DELAY);
  }
}
