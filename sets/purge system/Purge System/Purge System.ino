float flow_frequency; // Measures flow sensor pulses
float l_hour; // Calculated litres/hour
unsigned char flowsensor = 2; // Sensor Input
unsigned long currentTime;
unsigned long cloopTime;
int relaypin = 7;
int relay1 = 5;
int relay2 = 4;
int relay3 = 11;
int relay4 = 12;
float Tc1, Tc2, Tc3;

void flow () // Interrupt function
{
  flow_frequency++;
}

void setup()
{
  pinMode(relay1, OUTPUT);
  digitalWrite(relay1, LOW);
  pinMode(relay2, OUTPUT);
  digitalWrite(relay2, LOW);
  pinMode(relay3, OUTPUT);
  pinMode(relay4, OUTPUT);
  pinMode(relaypin, OUTPUT);
  pinMode(flowsensor, INPUT);
  digitalWrite(flowsensor, HIGH); // Optional Internal Pull-Up
  Serial.begin(9600);
  attachInterrupt(0, flow, RISING); // Setup Interrupt
  sei(); // Enable interrupts
  currentTime = millis();
  cloopTime = currentTime;
}

void loop ()
  {
  if (Serial.available() > 0);
  {  
  int data = Serial.parseInt();
  currentTime = millis();
  if(currentTime >= (cloopTime + 1000))
  {        
    cloopTime = currentTime; // Updates cloopTime
    // Pulse frequency (Hz) = 7.5Q, Q is flow rate in L/min.
    l_hour = (flow_frequency * 60 / 21)/60; // (Pulse frequency x 60 min) / 7.5Q = flowrate in L/hour
    flow_frequency = 0; // Reset Counter
    Serial.print(l_hour, 2); // Print litres/hour
    Serial.print(" ");
    // Serial.println(" L/hour");
    T1();      
    
    if (l_hour < 0.5)
    {relayon();}

    if (l_hour >= 0.5)
    {relayoff();}

    if ((data == 3) && (l_hour == 0.00)){
      purge();}
  }
  }
  } 


void T1() 
{
    int Ro = 10, B = 3892;                           //Nominal resistance 50K, Beta constant
    int Rseries = 10;// Series resistor 10K
    float To = 298.15; // Nominal Temperature
    float Vi = analogRead(A3) * (5.0 / 1023.0);
    //Convert voltage measured to resistance value
    //All Resistance are in kilo ohms.
    float R = (Vi * Rseries) / (5 - Vi);
    float T =  1 / ((1 / To) + ((log(R / Ro)) / B));
    Tc1 = T - 273.15;                            // Converting kelvin to celsius
    float Tf = Tc1 * 9.0 / 5.0 + 32.0;                 // Converting celsius to Fahrenheit
    Serial.print(Tc1);
    Serial.println(" ");
    }

void relayon() {
  digitalWrite(relaypin, HIGH);  
}

void relayoff() {
  digitalWrite(relaypin, LOW);  
}

void airon() {
digitalWrite(relay2, HIGH);
delay(4000);
digitalWrite(relay1, HIGH);
}

void airoff() {
digitalWrite(relay1, LOW);
delay(4000);
digitalWrite(relay2, LOW);
}

void purge() {
  airon();
  delay(10000);
  airoff();
}