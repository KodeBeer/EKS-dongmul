#include <MapFloat.h>
#include <avr/io.h>
#include <avr/interrupt.h>  
#define Open 1
#define Close 0

/*Soft Robot*/
int vacuumPump = 10;
int pressurePump = 11;
const int Valve1 = 4;
const int Valve2 = 5;
const int Valve3 = 6;
int pressureSpeed = 0;
int vacuumSpeed = 0;
int setPressure = 0;
int currentPressure = 0;
unsigned int interruptTime = 16000;

/*Communication*/
static char buffer[32];
static size_t pos = 0;
int endIdx = 0;
int startIdx = 0;
float firstFloat = 0;
float secondFloat = 0;
char complete = 'r';
char executing = 'e';
char initialized = 'i';
char message = 'm';
int BasePressure = 0;

ISR(TIMER1_COMPA_vect)
{
doTheMove();
}

void doTheMove(){
    currentPressure = analogRead(A3);
    pressureSpeed = mapFloat(firstFloat, 0, 1, 100, 180);
    setPressure = mapFloat(secondFloat, 0, 1, 495, 529);  
    Serial.println(message);
    Serial.println(currentPressure);
    Serial.println(setPressure);
    //If currentPressure smaller than set pressure,  then: Inflate
    // else deflate
    if (currentPressure < setPressure) {
      analogWrite(vacuumPump, pressureSpeed);
      analogWrite(pressurePump, pressureSpeed);
      
      digitalWrite (Valve1, Close);
      digitalWrite (Valve2, Close);
      digitalWrite (Valve3, Open);
    } else
     {     
      analogWrite(vacuumPump, pressureSpeed);
      analogWrite(pressurePump, 0);
      //digitalWrite (Valve1, Close);
      //digitalWrite (Valve2, Close);
      //digitalWrite (Valve3, Close);      
    }   
} 

void setup() {
  Serial.begin(9600);
  pinMode (A3, INPUT);
  pinMode(vacuumPump, OUTPUT);
  pinMode(pressurePump, OUTPUT);
  pinMode(Valve1, OUTPUT);
  pinMode(Valve2, OUTPUT);
  pinMode(Valve3, OUTPUT);
 
  digitalWrite (Valve1, Open);
  digitalWrite (Valve2, Open);
  digitalWrite (Valve3, Open);

  delay (1000);

  digitalWrite (Valve1, Close);
  digitalWrite (Valve2, Close);
  digitalWrite (Valve3, Close);
  BasePressure = analogRead (A3);

  // Initialize the timers and interrupt routine
  cli();
  TCCR1A = 0;
  TCCR1B = 0; 
  OCR1A = interruptTime;
  TCCR1B = (1<<WGM12) | (1<<CS12); 
  TIMSK1 = (1<<OCIE1A); 
  sei(); 
  Serial.print(initialized); //Signal to Python you are initialized and data transfer can start

  //  initializePins();
}
void loop() {
  bool execute = false;
  if (Serial.available()) {
    execute = readProcessLine();
  }
  if (execute) {
    // Here the stuff with the muscles starts    
    Serial.println(executing);
    delay(100);
    Serial.println(complete);
  }
}

int findCharacter(int startat, char toFind, char searchThis[], int maxLength ) {
  while ((searchThis[startat] != toFind) && (startat < maxLength)) {
    startat++;
  }
  if (searchThis[startat] == toFind) {
    return startat;
  } else {
    return -1;
  }
}

float makeFloat(int startCopy, int endCopy, char buffer[]) {
  static char numberHolder[10];
  int i = 0;
  while (startCopy < endCopy) {
    numberHolder[i] = buffer[startCopy];
    startCopy++;
    i++;
  }
  numberHolder[i] = '\0';
  return atof(numberHolder);
}

bool readProcessLine() {
  bool processed = false;
  char c;
  while (Serial.available()) {
    c = Serial.read();
    if (c == '\n') {  // on end of line, parse the number
      buffer[pos] = c;
      endIdx = findCharacter(0, ',', buffer, pos);
      if (endIdx != -1) {
        firstFloat = makeFloat(0, endIdx, buffer);
        //Serial.println(firstFloat);
      }
      startIdx = endIdx;
      endIdx = findCharacter(startIdx, '\n', buffer, pos);
      if (endIdx != -1) {
        secondFloat = makeFloat(startIdx + 1, endIdx, buffer);
        //Serial.println(secondFloat);
      }
      processed = true;
      pos = 0;
    } else if (pos < sizeof buffer - 1) {  // otherwise, buffer it
      buffer[pos++] = c;
      processed = false;
    }
  }
  return processed;
}
