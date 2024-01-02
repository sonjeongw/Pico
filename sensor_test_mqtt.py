import paho.mqtt.client as mqtt
import pyodbc
import datetime

mqtt_server = "broker.mqtt-dashboard.com"
# mqtt_topic_rx = "nockanda/ethernet/rx"
mqtt_topic_tx = "nockanda/ethernet/tx"

# MSSQL 서버 연결 정보
server = 'localhost'
database = 'PicoDB'
username = 'sa'
password = 'sa1234'

conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
connection = pyodbc.connect(conn_str)
cursor = connection.cursor()

def on_connect(client, userdata, flags, rc):
    # 클라이언트가 브로커에 연결될 때 호출되는 함수
    print("Connected with result code " + str(rc))
    client.subscribe(mqtt_topic_tx)

def on_publish(client, userdata, mid):
    # 메시지가 성공적으로 발행되었을 때 호출되는 함수
    print("Message Published")

def on_message(client, userdata, msg):
    # 구독한 토픽에서 메시지를 받았을 때 호출되는 함수
    received_data = msg.payload.decode("utf-8")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"Received data: {received_data} | Timestamp: {timestamp}")

    # 'Sensors' 테이블에 데이터를 삽입하는 SQL 쿼리
    sql = f"INSERT INTO Sensors (SensorColor, SensorDate) VALUES (?, ?)"

    try:
        # 받은 데이터를 파싱하고 SQL 쿼리를 실행
        color_data = received_data  
        cursor.execute(sql, (color_data, timestamp))
        connection.commit()
    except pyodbc.Error as error:
        print("Error : {}".format(error))



mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_publish = on_publish
mqtt_client.on_message = on_message

mqtt_client.connect(mqtt_server, 1883, 60)

mqtt_client.loop_forever()
