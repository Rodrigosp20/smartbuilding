#include <ArduinoMqttClient.h>
#include <user_interface.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>

#define STASSID "Pereira_Network_5GHz"
#define STAPSK  "pereira73"

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

const char* ssid = STASSID;
const char* password = STAPSK;

const char broker[] = "192.168.1.118";
int        port     = 1883;

String house, room;
int version = 1;
int previousTime = 0;


//callback to receive messages on the server
void onMqttMessage(int messageSize) {
  String message = "";

  // use the Stream interface to print the contents
  while (mqttClient.available()) {
    message += (char)mqttClient.read();
  }
  
  //check the command from the server
  if (message == "update") {
    version++;

    //blink led
    for(int i=0; i<2; i++){
      digitalWrite(LED_BUILTIN, 0);
      delay(500);
      digitalWrite(LED_BUILTIN, 1);
      delay(500);
    } 
    
    mqttClient.beginMessage("sensor/version/house/"+house+"/room/"+room, true);
    mqttClient.print(version);
    mqttClient.endMessage();
    return;
  }
}
  
void connectToBroker() {
  WiFi.begin(ssid, password);
  while ( WiFi.status() != WL_CONNECTED) {
    // failed, retry
    Serial.print(".");
    delay(500);
  }

  mqttClient.onMessage(onMqttMessage);
  while (!mqttClient.connect(broker, port)) {
    Serial.print("MQTT connection failed! Error code = ");
    Serial.println(mqttClient.connectError());
    delay(1000);
  }
} 


void setup() {
    // Serial setup
  Serial.begin(115200);
  delay(10);
  connectToBroker();
  
  Serial.print("Insert house name: ");
  while(Serial.available()== 0){}
  house = Serial.readString();
  house.trim();
  Serial.println(house);
  Serial.print("Insert room name: ");
  while(Serial.available()== 0){}
  room = Serial.readString();
  room.trim();
  Serial.println(room);

  mqttClient.subscribe("sensor/house/"+ house + "/room/"+ room);
  
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, 1);
  mqttClient.beginMessage("sensor/version/house/"+house+"/room/"+room, true);
  mqttClient.print(version);
  mqttClient.endMessage();
}

void loop() {
  Serial.println("");
  Serial.println("1) Human");
  Serial.println("2) Temperature");
  Serial.println("3) CO2 level");
  Serial.println("4) Light level");
  Serial.print("Select a environmental parameter:");
  previousTime = millis();
  while(Serial.available() == 0){
    if((millis() - previousTime) > 300) {
      previousTime = millis();   
      mqttClient.poll();
    }
  }
  int opt = Serial.parseInt();
  Serial.println(opt);
  if (opt > 4 || opt <1){
    Serial.println("Invalid option");
    return;
  }

  Serial.print("Enter a value:");
  previousTime = millis();
  while(Serial.available() == 0){
    if((millis() - previousTime) > 300) {
      previousTime = millis();   
      mqttClient.poll();
    }
   }
  int value = Serial.parseInt();
  Serial.println(value);
  
  switch (opt){
    case 1:
      mqttClient.beginMessage("sensor/human/house/"+house+"/room/"+room, true);
      mqttClient.print(value);
      mqttClient.endMessage();  
      break;
    case 2:
      mqttClient.beginMessage("sensor/temp/house/"+house+"/room/"+room, true);
      mqttClient.print(value);
      mqttClient.endMessage();
      break;
    case 3:
      mqttClient.beginMessage("sensor/co2/house/"+house+"/room/"+room, true);
      mqttClient.print(value);
      mqttClient.endMessage();
      break;
    case 4:
      mqttClient.beginMessage("sensor/light/house/"+house+"/room/"+room, true);
      mqttClient.print(value);
      mqttClient.endMessage();
      break;
  }
}
