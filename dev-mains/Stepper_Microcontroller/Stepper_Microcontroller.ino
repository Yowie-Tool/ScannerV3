#include <ams_as5048b.h>
#include <SPI.h>
#include <Wire.h>
//Code for A4988 Driver - not suitable for TMC 2130 driver.

//Encoder setup
#define U_RAW 1
#define U_TRN 2
#define U_DEG 3
#define U_RAD 4
#define U_GRAD 5
#define U_MOA 6
#define U_SOA 7
#define U_MILNATO 8
#define U_MILSE 9
#define U_MILRU 10
AMS_AS5048B mysensor;

//Pin designations
const int dirstp1 = 4;  // direction, clockwise or counter clockwise pin
const int stpstp1 = 3;  // step command
const int ms3stp1 = 6; // MS3/CS
const int ms2stp1 = 13; // MS2/SCK
const int ms1stp1 = 11; // MS1/MOSI
const int enable = 5; // Stepper enable
const int SERRX = 0; // UART Recv
const int SERTX = 1; // UART Transmit
const int PWMin = 2; //PWM input from encoder
int microsteps1 = 16; // Number of microsteps
int calculstep1; // integer for number of steps from degree input - stepper 1
int stpspd = 500; // Time between steps (microseconds)
int stpdir = 0; // Step Horizontal Mirror direction
float currentangle=0.0;// Current angle of stepper motor
float movedangle=0.0; // New angle to return 
int hstop = 0; // Optional Hard stop - shouldn't be neccessary now we've moved away from belts.

const byte numChars = 10;
char receivedChars[numChars]; // an array to store the received data

boolean newData = false;
char recvd;
int numstring; // integer for the second bit of the Gcode.

void setup() {

  pinMode(dirstp1, OUTPUT); // Set pin modes. You probably know this already...
  pinMode(stpstp1, OUTPUT);
  pinMode(ms3stp1, OUTPUT);
  pinMode(ms2stp1, OUTPUT);
  pinMode(ms1stp1, OUTPUT);
  pinMode(enable, OUTPUT);
  pinMode(SERRX, INPUT);
  pinMode(SERTX, OUTPUT);
  digitalWrite(ms1stp1, HIGH);
  digitalWrite(ms2stp1, HIGH);
  digitalWrite(ms3stp1, HIGH);

  digitalWrite(enable, HIGH);
  Serial.begin(9600);   // Open serial port 
  Serial.flush();       // Clear receive buffer.
  mysensor.begin();     // Start the encoder
}

void loop() {
  recvWithEndMarker();
  UseData();
}

void recvWithEndMarker() {
  static byte ndx = 0;
  char endMarker = '\n';
  char rc;

  // if (Serial.available() > 0) {
  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();

    if (rc != endMarker) {
      receivedChars[ndx] = rc;
      ndx++;
      if (ndx >= numChars) {
        ndx = numChars - 1;
      }
    }
    else {
      receivedChars[ndx] = '\0'; // terminate the string
      ndx = 0;
      newData = true;
    }
  }
}

void UseData() {

  if (newData == true) {
    newData = false;
    numstring = atoi(&receivedChars[1]);

    switch (receivedChars[0]) {
      case 'A': // Move Anticlockwise. Hopefully. stpdir will reverse direction if wired the wrong way round. input in degrees, converted to steps. Optional Hard stop is one step in reverse direction then back again to stop momentum of arm.
      case 'a':
        calculstep1 = (((numstring / 1.8) * 3) * microsteps1); // 3 is for the gearing on the horizontal stepper. 1.8 is for a 200 step for 360 degree stepper
        if (stpdir == 0) digitalWrite(dirstp1, HIGH);
        if (stpdir == 1) digitalWrite(dirstp1, LOW);
        for (int x = 0; x < calculstep1; x++) {
          digitalWrite(stpstp1, HIGH);
          delayMicroseconds(stpspd);
          digitalWrite(stpstp1, LOW);
          delayMicroseconds(stpspd);  
        }
        if (hstop==1){
          if (stpdir==0){ // Hard stop on
            digitalWrite(dirstp1, LOW);
            digitalWrite(stpstp1, HIGH);
            delayMicroseconds(stpspd);
            digitalWrite(stpstp1, LOW);
            delayMicroseconds(stpspd);
            digitalWrite(dirstp1, HIGH);
            digitalWrite(stpstp1, HIGH);
            delayMicroseconds(stpspd);
            digitalWrite(stpstp1, LOW);
            delayMicroseconds(stpspd);
          }
          if (stpdir==1){
            digitalWrite(dirstp1, HIGH);
            digitalWrite(stpstp1, HIGH);
            delayMicroseconds(stpspd);
            digitalWrite(stpstp1, LOW);
            delayMicroseconds(stpspd);
            digitalWrite(dirstp1, LOW);
            digitalWrite(stpstp1, HIGH);
            delayMicroseconds(stpspd);
            digitalWrite(stpstp1, LOW);
            delayMicroseconds(stpspd);
          }
        }
        movedangle=(currentangle-(mysensor.angleR(U_DEG, false), DEC));    
        Serial.println(movedangle);
        currentangle=(mysensor.angleR(U_DEG, false), DEC);
        break;

      case 'C': // Move Clockwise. As above
      case 'c':
        calculstep1 = (((numstring / 1.8) * 3) * microsteps1); // 3 is for the gearing on the horizontal stepper. 1.8 is for a 200 step for 360 degree stepper
        if (stpdir == 0) digitalWrite(dirstp1, LOW);
        if (stpdir == 1) digitalWrite(dirstp1, HIGH);
        for (int x = 0; x < calculstep1; x++) {
          digitalWrite(stpstp1, HIGH);
          delayMicroseconds(stpspd);
          digitalWrite(stpstp1, LOW);
          delayMicroseconds(stpspd);
        }
        if (hstop==1){ // Hard stop on
          if (stpdir==0){
            digitalWrite(dirstp1, HIGH);
            digitalWrite(stpstp1, HIGH);
            delayMicroseconds(stpspd);
            digitalWrite(stpstp1, LOW);
            delayMicroseconds(stpspd);
            digitalWrite(dirstp1, LOW);
            digitalWrite(stpstp1, HIGH);
            delayMicroseconds(stpspd);
            digitalWrite(stpstp1, LOW);
            delayMicroseconds(stpspd);
          }
          if (stpdir==1){
            digitalWrite(dirstp1, LOW);
            digitalWrite(stpstp1, HIGH);
            delayMicroseconds(stpspd);
            digitalWrite(stpstp1, LOW);
            delayMicroseconds(stpspd);
            digitalWrite(dirstp1, HIGH);
            digitalWrite(stpstp1, HIGH);
            delayMicroseconds(stpspd);
            digitalWrite(stpstp1, LOW);
            delayMicroseconds(stpspd);
          }
        }
        movedangle=((mysensor.angleR(U_DEG, false), DEC)-currentangle);    
        Serial.println(movedangle);
        currentangle=(mysensor.angleR(U_DEG, false), DEC);
        break;
       case 'E': // E for enable. Sets enable pin to low which enables both steppers. Steppers are disabled at startup. enable LED will go out when steppers are active. Enable LED coming on when board powered on shows sketch is working.
       case 'e':
        if (numstring==1) {
          digitalWrite(enable, LOW);
        }
        else {
          digitalWrite(enable, HIGH);
        }
        Serial.println("Enable status changed");
        break;

       case 'H': // Mirror direction if needed. 
       case 'h':
        if (numstring==1) {
        stpdir=1;
        }
        else {
        stpdir=0;
        }
        Serial.println("Y");
        break;
        
        case 'T': // Adjust microsecond delay between steps - default is 500ms
        case 't':
        stpspd=numstring;
        Serial.println("Delay Altered");
        break;

        case 'S': // Toggles hard stop on horizontal stepper. 
        case 's':
        if (numstring==1) {
        hstop=1;
        }
        else {
        hstop=0;
        }
        Serial.println("Hard Stop Setting Altered");
        break;

        case 'Q': // queries settings 
        case 'q':
        Serial.println("Delay: ");
        Serial.print(stpspd);
        Serial.println("Hard Stop: ");
        Serial.print(hstop);
        Serial.println("Mirror Rotation: ");
        Serial.print(stpdir);
        Serial.println("Steppers Enabled: ");
        Serial.print(enable);
        break;

         case 'M': // Microsteps
         case 'm':
         microsteps1 = numstring;
         switch (microsteps1){
          case 1:
            digitalWrite(ms1stp1, LOW);
            digitalWrite(ms2stp1, LOW);
            digitalWrite(ms3stp1, LOW);
          break;
          case 2:
            digitalWrite(ms1stp1, HIGH);
            digitalWrite(ms2stp1, LOW);
            digitalWrite(ms3stp1, LOW);
          break;   
          case 4:
            digitalWrite(ms1stp1, LOW);
            digitalWrite(ms2stp1, HIGH);
            digitalWrite(ms3stp1, LOW);
          break;   
          case 8:
            digitalWrite(ms1stp1, HIGH);
            digitalWrite(ms2stp1, HIGH);
            digitalWrite(ms3stp1, LOW);
          break;  
          case 16:
            digitalWrite(ms1stp1, HIGH);
            digitalWrite(ms2stp1, HIGH);
            digitalWrite(ms3stp1, HIGH);
          break;  
         }

    }
  }
}
