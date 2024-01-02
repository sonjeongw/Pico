#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>

#define redled 0    // 빨
#define blueLed 5   // 블루
#define yellowled 9 // 노
#define greenled 13  // 초

byte mac[] = {0xDE, 0xED, 0xBA, 0xFE, 0xFE, 0xED};
IPAddress ip(172, 16, 0, 100);
const char *mqtt_server = "broker.mqtt-dashboard.com";

unsigned long t = 0;
String lastMessage;  // Variable to store the last LED status

EthernetClient ethClient;
PubSubClient client(ethClient);

void callback(char *topic, byte *payload, unsigned int length)
{
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++)
  {
    Serial.print((char)payload[i]);
  }
  Serial.println();

 if (payload[0] == '1')
  {
    digitalWrite(redled, HIGH);
    lastMessage = "red";
  }
  else if (payload[0] == '2')
  {
    digitalWrite(blueLed, HIGH);
    lastMessage = "blue";
  }
  else if (payload[0] == '3')
  {
    digitalWrite(greenled, HIGH);
    lastMessage = "green";
  }
  else if (payload[0] == '4')
  {
    digitalWrite(yellowled, HIGH);
    lastMessage = "yellow";
  }
  else if (payload[0] == '5')
  {
    digitalWrite(redled, LOW);
    digitalWrite(blueLed, LOW);
    digitalWrite(greenled, LOW);
    digitalWrite(yellowled, LOW);
    lastMessage = "모든 LED 꺼짐";
  }
}

void reconnect()
{
  while (!client.connected())
  {
    Serial.print("Attempting MQTT connection...");
    String clientId = "Nockanda-";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str()))
    {
      Serial.println("connected");
      client.subscribe("nockanda/ethernet/rx");
    }
    else
    {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup()
{
  Serial.begin(9600);
  pinMode(redled, OUTPUT);
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  Ethernet.begin(mac);

  randomSeed(micros());
  delay(1500);
}

void loop()
{
  if (!client.connected())
  {
    reconnect();
  }
  client.loop();

  if (millis() - t > 5000)
  {
    t = millis();
    // Publish the last LED status every 5 seconds
    client.publish("nockanda/ethernet/tx", lastMessage.c_str());
  }
}
