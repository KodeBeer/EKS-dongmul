#include <MapFloat.h>

/* Valve control */
#define Open 1
#define Close 0

/* Soft Robot hardware settings */
int vacuumPump = 10;
int pressurePump = 11;
const int Valve1 = 4;
const int Valve2 = 5;
const int Valve3 = 6;

/* Pressure controls */
int pressureSpeed = 0;
int vacuumSpeed = 0;
int setPressure = 0;
int currentPressure = 0;
int maxPressure = 531;
int basePressure = 0; // base line calibration for low pressure

/* Communication */
float firstFloat = 0; // First float number that enters in the comm protocol
float secondFloat = 0; // Second float number that enters in the comm protocol
char initialized = 'i';

/* Timing parameters */
long int moveTime = 0; // Determines the time that the next movement is made must be long (mSec)
long int nextMoveTime = 300; // time in mSec before next move is made after completion.
long int reportPressureTime = 0; //do not report pressure too quickly
long int nextReportPressureTime = 1000;

/* send the measured pressure to Python */
void reportPressure(){
    currentPressure = analogRead(A3);
    Serial.print("Current Pressure: ");
    Serial.println(currentPressure);
    reportPressureTime = millis() + nextReportPressureTime;
}

/* Actual move execution */
void doTheMove(){
    currentPressure = analogRead(A3);
    //If currentPressure smaller than set pressure,  then: Inflate else deflate
    if (currentPressure < setPressure) {
      analogWrite(vacuumPump, 0);
      analogWrite(pressurePump, pressureSpeed);
    } else {  
      if (currentPressure > basePressure) {
        analogWrite(vacuumPump, pressureSpeed);
        analogWrite(pressurePump, 0); 
      }     
    } 
    moveTime = millis() + nextMoveTime;  
} 

void processInput(){
    firstFloat = Serial.parseFloat(); 
    secondFloat = Serial.parseFloat(); 
    pressureSpeed = mapFloat(firstFloat, 0, 1, 100, 180);
    setPressure = mapFloat(secondFloat, 0, 1, basePressure, maxPressure);  
    Serial.print("Set speed and pressure: ");
    Serial.print(pressureSpeed);
    Serial.print(" ");
    Serial.println(setPressure);  
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(500);
  pinMode (A3, INPUT);
  pinMode(vacuumPump, OUTPUT);
  pinMode(pressurePump, OUTPUT);
  pinMode(Valve1, OUTPUT);
  pinMode(Valve2, OUTPUT);
  pinMode(Valve3, OUTPUT);
  
  /* Set for emptying out air */
  digitalWrite (Valve1, Open); 
  digitalWrite (Valve2, Open);
  digitalWrite (Valve3, Close);
  delay (1000); // Wait for all mechanical action to finish
  basePressure = analogRead (A3); // measure and provide the base pressure  
  
  // Set for control by pumps:
  digitalWrite (Valve1, Close); 
  digitalWrite (Valve2, Close);
  digitalWrite (Valve3, Open);

  /* Signal that Arduino has started to Python program, and remove any bytes that 
     during startup spikes might have entered the serial pipeline */
  Serial.print(initialized); 
  while (Serial.available()) {
      Serial.read();
    }
}

void loop() {
  if (millis() > moveTime){
    doTheMove();
  }  
  if (millis() > reportPressureTime) {
    reportPressure();
  }
  if (Serial.available()) {
    processInput();
  }
}
  
