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
int setVolume = 0;
int currentVolume = 0;
int currentPressure = 0;
float deltaPosVolume = 1.5;
float deltaNegVolume = 3.6;
float pressureNormalization = 500.0;
float maxVolume = 4000.0;
int basePressure = 0; // base line calibration for low pressure

/* Communication */
int thisCommand = 0;
float firstFloat = 0; // First float number that enters in the comm protocol
float secondFloat = 0; // Second float number that enters in the comm protocol
char initialized = 'i';

/* Timing parameters */
long int moveTime = 0; // Determines the time that the next movement is made must be long (mSec)
long int nextMoveTime = 300; // time in mSec before next move is made after completion.
float integrationTime = float(nextMoveTime) / 1000.0;
long int reportPressureTime = 0; //do not report pressure too quickly
long int nextReportPressureTime = 1000;

/* send the measured pressure to Python */
void reportPressure(){
    currentPressure = analogRead(A3);
    
    Serial.print("Pressure, Volume: ");
    Serial.print(currentPressure);
    Serial.print(" ");
    Serial.print(currentVolume);
    
    reportPressureTime = millis() + nextReportPressureTime;
}

void calibrateVolume(){
    deltaPosVolume = Serial.parseFloat(); 
    deltaNegVolume = Serial.parseFloat();      
}

void executeCommand(){
    firstFloat = Serial.parseFloat(); 
    secondFloat = Serial.parseFloat(); 
    pressureSpeed = mapFloat(firstFloat, 0, 1, 100, 180);
    setVolume = mapFloat(secondFloat, 0, 1, 0, maxVolume);   
    Serial.print("Speed, Pressure: ");
    Serial.print(pressureSpeed);
    Serial.print(" ");
    Serial.println(setVolume);      
}

/* Actual move execution */
void doTheMove(){
    currentPressure = analogRead(A3);
    /* correction for smaller airdisplacement when pumping against higher pressure */
   
    /* If currentVolume smaller than set Volume,  then: Inflate else deflate
     * Note: the formula for volume integration is not correct as the time between
     * move updates is not taken into account. For now it will have to do
     * Also: in the end some form of real volume sensing is needed
     * The Formula takes the pressure measurement into account as delta Volume depends on this
     */
    if (currentVolume < setVolume) {
      analogWrite(vacuumPump, 0);
      analogWrite(pressurePump, pressureSpeed);
      currentVolume += deltaPosVolume * pressureSpeed * integrationTime * pressureNormalization / currentPressure;
    } else {  
      if (currentPressure > basePressure) {
        analogWrite(vacuumPump, pressureSpeed);
        analogWrite(pressurePump, 0); 
        currentVolume -= deltaNegVolume * pressureSpeed * integrationTime * currentPressure / pressureNormalization;
      }     
    } 
    moveTime = millis() + nextMoveTime;
} 

void processTheInput(){
    thisCommand = Serial.parseInt();
    switch (thisCommand) {
      case 0:
        executeCommand();
        break;
      case 1:
       calibrateVolume();
        break;
      default:
        // statements
        break;
    }
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
    processTheInput();
  }
}
  
