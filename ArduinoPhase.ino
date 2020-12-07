String readString;
const int trig = 2;     // chân trig của HC-SR04
const int echo = 3;     // chân echo của HC-SR04
const int R_EN = 4;
const int L_EN = 5;

const int LeftMotorForward = 8;
const int LeftMotorBackward = 9;

const int RightMotorForward = 7;
const int RightMotorBackward = 6;
int checkPeople;
int check;
int distance;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);     // giao tiếp Serial với baudrate 9600
  pinMode(trig, OUTPUT);  // chân trig sẽ phát tín hiệu
  pinMode(echo, INPUT);   // chân echo sẽ nhận tín hiệu

  pinMode(RightMotorForward, OUTPUT);
  pinMode(LeftMotorForward, OUTPUT);
  pinMode(LeftMotorBackward, OUTPUT);
  pinMode(RightMotorBackward, OUTPUT);

  pinMode(L_EN, OUTPUT);
  pinMode(R_EN, OUTPUT);


  digitalWrite(R_EN, HIGH);
  digitalWrite(L_EN, HIGH);
  distance = readSensor();    // Get Ping Distance.
  delay(100);               // Wait for 100ms.
  distance = readSensor();
  delay(100);
  distance = readSensor();
  delay(100);

}

void loop() {
  Serial.flush();
  // put your main code here, to run repeatedly:
  distance = readSensor();
  if (distance < 60) {
    moveStop();
    delay(300);
    moveBackward();
    delay(300);
    moveStop();
    delay(300);
    turnRight();
    delay(2000);
    moveStop();
    delay(2500);
  } else {

    checkPeople = checkingPeople();

    if (checkPeople == 1) {
      turnLeft();
      delay(200);
      moveStop();
    } else if (checkPeople == 2) {
      moveForward();
      delay(2000);
      moveStop();
    } else if (checkPeople == 3) {
      turnRight();
      delay(200);
      moveStop();
    } else {
      moveStop();
    }
  }
}

int readSensor() {
  unsigned long duration; // biến đo thời gian
  int distance;           // biến lưu khoảng cách

  //    /* Phát xung từ chân trig */
  digitalWrite(trig, 0);  // tắt chân trig
  delayMicroseconds(2);
  digitalWrite(trig, 1);  // phát xung từ chân trig
  delayMicroseconds(5);   // xung có độ dài 5 microSeconds
  digitalWrite(trig, 0);  // tắt chân trig
  //
  //    /* Tính toán thời gian */
  //    // Đo độ rộng xung HIGH ở chân echo.
  duration = pulseIn(echo, HIGH);
  // Tính khoảng cách đến vật.
  distance = int(duration / 2 / 29.412);
  //
  //    /* In kết quả ra Serial Monitor */
  Serial.print(distance);
  Serial.println("cm");
  delay(200);
  return distance;
}

void moveStop()       // Move Stop Function for Motor Driver.
{
  digitalWrite(RightMotorForward, LOW);
  digitalWrite(RightMotorBackward, LOW);
  digitalWrite(LeftMotorForward, LOW);
  digitalWrite(LeftMotorBackward, LOW);
  Serial.println("moveStop");
}
void moveForward()    // Move Forward Function for Motor Driver.
{

  analogWrite(RightMotorForward, 200);
  analogWrite(RightMotorBackward, 0);
  analogWrite(LeftMotorForward, 200);
  analogWrite(LeftMotorBackward, 0);

  Serial.println("moveForward");
}

void moveBackward()   // Move Backward Function for Motor Driver.
{
  //analogWrite(RightMotorForward, HIGH);
  analogWrite(RightMotorForward, 0);
  analogWrite(RightMotorBackward, 150);
  analogWrite(LeftMotorForward, 0);
  analogWrite(LeftMotorBackward, 150);
  //analogWrite(RightMotorForward, HIGH);
  Serial.println("moveBackward");
}

void turnRight()      // Turn Right Function for Motor Driver.
{
  //delay(3500);
  analogWrite(RightMotorForward, 0);
  analogWrite(RightMotorBackward, 155);
  analogWrite(LeftMotorForward, 155);
  analogWrite(LeftMotorBackward, 0);
  delay(300);
  Serial.println(" turnRight-----------  ");
  //Serial.print( checkcam);
}

void turnLeft()       // Turn Left Function for Motor Driver.
{
  Serial.println("turnLeft");
  //Serial.print(checkcam);
  //delay(3500);
  analogWrite(RightMotorForward, 155);
  analogWrite(RightMotorBackward, 0);
  analogWrite(LeftMotorForward, 0);
  analogWrite(LeftMotorBackward, 155);
  delay(300);

}

int checkingPeople() {

  Serial.print("Turn into checkingPeople: ");
  int ans = 10;
  // serial read section
  while (Serial.available())
  {
    Serial.print("pass");
    if (Serial.available() == 2) {
      Serial.print("Turn into received: ");
      String c = Serial.readStringUntil('\n');  //gets one byte from serial buffer
      Serial.print("end received: ");
      readString = c; //makes the string readString
      Serial.print("Arduino received: ");
//      ans = readString.charAt(0) - '0';
//      Serial.println(ans);
//      Serial.flush();
//      check = ans;
//      sendingMessage(ans);
      return c.charAt(0) - '0';
    }
    String c = Serial.readStringUntil('\n'); 

  }
//  Serial.flush();
//  Serial.print(Serial.available());
//  Serial.setTimeout(10);


    return ans;

  
}
