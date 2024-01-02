import random
import time
from paho.mqtt import client as mqtt_client
import pyodbc

broker = 'broker.mqtt-dashboard.com'
port = 1883
topic = "nockanda/ethernet/rx"
client_id = f'publish-{random.randint(0, 1000)}'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("MQTT 브로커에 연결되었습니다!")
        else:
            print(f"연결 실패, 반환 코드: {rc}")

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client, message):
    result, _ = client.publish(topic, message)
    if result == mqtt_client.MQTT_ERR_SUCCESS:
        print(f"메시지를 Topic '{topic}'로 전송했습니다: {message}")
    else:
        print(f"메시지 전송 실패: {topic}")

def run():
    client = connect_mqtt()
    client.loop_start()
    
    # SQLite 데이터베이스 연결
    server = 'localhost'
    database = 'PicoDB'
    username = 'sa'
    password = 'sa1234'

    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    
    last_color = None  # 마지막으로 전송한 색상을 저장하는 변수

    while True:
        connection = pyodbc.connect(conn_str)
        cursor = connection.cursor()

        try:
            # Orders 테이블에서 마지막 행 가져오기
            cursor.execute("SELECT TOP 1 OrderColor FROM Orders ORDER BY OrderNo DESC")
            result = cursor.fetchone()

            if result:
                color_value = result[0]

                # 마지막으로 전송한 색상과 현재 색상이 다를 때만 '5'를 토픽에 보내기
                if color_value != last_color:
                    publish(client, '5')
                    time.sleep(1)  
                    last_color = color_value

                # 적절한 숫자를 토픽으로 한 번만 보내기
                if color_value.lower() == 'red':
                    publish(client, '1')
                elif color_value.lower() == 'blue':
                    publish(client, '2')
                elif color_value.lower() == 'green':
                    publish(client, '3')
                elif color_value.lower() == 'yellow':
                    publish(client, '4')
                elif color_value.lower() == 'off':
                    publish(client, '5')
                time.sleep(1)


        except KeyboardInterrupt:
            print("사용자에 의해 종료되었습니다.")
            break
        finally:
            connection.close()

if __name__ == '__main__':
    run()
