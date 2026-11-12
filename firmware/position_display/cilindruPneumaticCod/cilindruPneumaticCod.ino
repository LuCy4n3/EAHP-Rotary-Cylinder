#define B 3
#define C 5
#define A 6
#define D 10
#define E 11
#define F 12

void setup() {
  // put your setup code here, to run once:
  pinMode(A,OUTPUT);
  pinMode(B,OUTPUT);
  pinMode(C,OUTPUT);
  pinMode(D,OUTPUT);
  pinMode(E,OUTPUT);
  pinMode(F,OUTPUT);
  pinMode(2,OUTPUT);
  pinMode(13,OUTPUT);
  Serial.begin(9600);
  Serial.println("Starting seq ===========");
  digitalWrite(2,LOW);
  digitalWrite(13,HIGH);
  for(int i = 0; i < 8;i++)
  {
    analogWrite(A,i&(0b001) ? 255:0 );
    analogWrite(B,i&(0b010) ? 255:0 );
    analogWrite(C,i&(0b100) ? 255:0 );
    analogWrite(D,0);
    analogWrite(E,0);
    analogWrite(F,0);
    delay(500);

  }
  delay(1000);
  digitalWrite(2,HIGH);
  digitalWrite(13,LOW);
  for(int i = 0 ;i < 8;i++)
  {
    analogWrite(D,i&(0b001) ? 255:0 );
    analogWrite(E,i&(0b010) ? 255:0 );
    analogWrite(F,i&(0b100) ? 255:0 );
    analogWrite(A,0);
    analogWrite(B,0);
    analogWrite(C,0);
    delay(500);
  }
  delay(1000);
  digitalWrite(2,LOW);
  digitalWrite(13,LOW);
  analogWrite(D, 255 );
  analogWrite(E, 255 );
  analogWrite(F, 255 );
  analogWrite(A, 255 );
  analogWrite(B, 255 );
  analogWrite(C, 255 );
  delay(1000);
  analogWrite(D, 0 );
  analogWrite(E, 0 );
  analogWrite(F, 0 );
  analogWrite(A, 0 );
  analogWrite(B, 0 );
  analogWrite(C, 0 );
  delay(1000);
  Serial.println("Ending seq========");
  
  //digitalWrite(A,LOW);
  //digitalWrite(B,LOW);
  //digitalWrite(C,LOW);
  // digitalWrite(D,LOW);
  // digitalWrite(E,LOW);
  // digitalWrite(F,LOW);
}

void loop() {
  int sensorValue = analogRead(A0);
  // put your main code here, to run repeatedly:
  int i = sensorValue >> 6;
  if(i<8)
  {
     digitalWrite(2,LOW);
    digitalWrite(13,HIGH);
    
    analogWrite(A,i&(0b001) ? 255:0 );
    analogWrite(B,i&(0b010) ? 255:0 );
    analogWrite(C,i&(0b100) ? 255:0 );
    analogWrite(D,0);
    analogWrite(E,0);
    analogWrite(F,0);
    //Serial.print("<");
  }
  
  else
  {
    i = i - 8;
    digitalWrite(2,HIGH);
    digitalWrite(13,LOW);
    analogWrite(D,i&(0b001) ? 255:0 );
    analogWrite(E,i&(0b010) ? 255:0 );
    analogWrite(F,i&(0b100) ? 255:0 );
    analogWrite(A,0);
    analogWrite(B,0);
    analogWrite(C,0);
    //Serial.print(">");
  }
  
  
  //Serial.println(i);

    // digitalWrite(D,i&(0b001) ? HIGH:LOW );
    // digitalWrite(E,i&(0b010) ? HIGH:LOW );
    // digitalWrite(F,i&(0b100) ? HIGH:LOW );
   
    // Serial.print(i);
    // Serial.print(" ");
    // Serial.print(i&(0b001)? 1 : 0);
    // Serial.print(" ");
    // Serial.print(i&(0b010)? 1 : 0);
    // Serial.print(" ");
    // Serial.print(i&(0b100)? 1 : 0);
    // Serial.print(" ");
    // Serial.println();
    delay(1);
  
}
