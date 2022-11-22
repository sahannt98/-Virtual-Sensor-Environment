import paho.mqtt.client as mqtt
import threading
import time
import random
import json

keepalive = 60

class Sensor:
    def __init__(self, group_id, sensor_id, host, port, usrname, passwd, min, max, unit, interval):
        self.host = host
        self.port = port
        self.usrname = usrname
        self.passwd = passwd
        self.sensor_id = sensor_id
        self.topic = "/{0}/{1}".format(group_id, sensor_id)
        self.interval = interval
        self.pre_data = min
        self.min = min
        self.max = max
        self.unit = unit
        self.client = mqtt.Client(sensor_id, True, sensor_id, mqtt.MQTTv311, "tcp") # check reconnect on faliure parameter

    def on_connect(self, client, userdata, flags, rc):
        print("sensor_Id: {0} connected to host: {1}, port: {2}, returned code: {3}".format(userdata, client._host, client._port, rc))

    def data_generator(self):
        val = 0.4*self.pre_data + 0.6*random.randint(self.min, self.max)
        self.pre_data = val
        return {"Sensor_Id": self.sensor_id, "Value": round(val, 2), "Unit": self.unit}

    def periodic_publish(self):
        self.client.loop_start()
        while True:
            time.sleep(self.interval)
            data = json.dumps(self.data_generator())
            result = self.client.publish(self.topic, data)
            if result[0] == 0:
                print("published : ", data)
            else:
                print("falied to publish data by sensor {0}".format(self.sensor_id))

    # generated data should be numerical values
    def event_triggered_publish(self, case, threashold):
        self.client.loop_start()
        while True:
            time.sleep(self.interval)
            data = self.data_generator()
            val = data.get("Value")
            if case < 0 or case > 4:
                print("Unsupported rule")
                return
            else:
                rule_check = (case == 0 and val < threashold) or (case == 1 and val <= threashold) or \
                            (case == 2 and val == threashold) or (case == 3 and val > threashold) or \
                            (case == 4 and val >= threashold)
                if rule_check:
                    result2 = self.client.publish(self.topic, json.dumps(data))
                    if result2[0] == 0:
                         print("published : event triggered ['case': {0}, 'threashold': {1}] : {2}".format(case, threashold, str(data)))
                    else:
                        print("falied to publish data by sensor {0}".format(self.sensor_id))

    def exec(self, rule=None, threshold=None):
        self.client.on_connect = self.on_connect
        self.client.username_pw_set(self.usrname, self.passwd)
        self.client.connect(self.host, self.port, keepalive)
        if rule != None and threshold != None :
            threading.Thread(target=self.event_triggered_publish, args=(rule, threshold), daemon=True).start()
        else:
            threading.Thread(target=self.periodic_publish, daemon=True).start()

class Virtual_Env:
    def __init__(self, env_name, group_id, host, port, usrname, passwd):
        self.group_id  = group_id
        self.host = host
        self.port = port
        self.usrname = usrname
        self.passwd = passwd
        print(".... {0} - Virtual Sensor Environment - {1} ....\n".format(env_name, group_id))

    def activate_sensor(self, sensor_id, min, max, unit, interval):
        new_sensor = Sensor(self.group_id, sensor_id, self.host, self.port, self.usrname, self.passwd, min, max, unit, interval)
        new_sensor.exec()

    def activate_event_triggered_sensor(self, sensor_id, min, max, unit, interval, rule, threashold):
        new_sensor = Sensor(self.group_id, sensor_id, self.host, self.port, self.usrname, self.passwd, min, max, unit, interval)
        new_sensor.exec(rule, threashold) 

    def loop_forever(self):
        while True:
            input()


broker_host = "broker.hivemq.com"
broker_port = 1883
power_plant = "Solar Power Plant"
group_id = "group06w"
power_plant_usrname = "g6@iot_pp"
power_plant_passwd = "g6@test123"

if __name__ == "__main__":
    pp = Virtual_Env(power_plant, group_id, broker_host, broker_port, power_plant_usrname, power_plant_passwd)
   
    pp.activate_sensor(sensor_id="Temp01", min=20, max=35, unit="Celsius", interval=30)
    pp.activate_sensor(sensor_id="Temp02", min=20, max=65, unit="Celsius", interval=20)
    pp.activate_sensor(sensor_id="Hum01", min=55, max=95, unit="RH", interval=25)
    pp.activate_sensor(sensor_id="WindSp01", min=5, max=40, unit="Km/h", interval=40)
    pp.activate_sensor(sensor_id="WindDir01", min=0, max=360, unit="degrees", interval=40)
    pp.activate_sensor(sensor_id="BatCap01", min=1000, max=7000, unit="AH", interval=60)
    pp.activate_sensor(sensor_id="BatCap02", min=1000, max=7000, unit="AH", interval=60)
    pp.activate_sensor(sensor_id="BatCap03", min=1000, max=7000, unit="AH", interval=60)

    pp.activate_event_triggered_sensor(sensor_id="Illum01", min=10, max=1500, unit="lux",
        interval=30, rule=4, threashold=50)
    pp.activate_event_triggered_sensor(sensor_id="PowGen01", min=500, max=1400, unit="KW", 
        interval=25, rule=0, threashold=800)

    pp.loop_forever()

### To run program ###
# Navigate to root directory of group06w_legend.py
# Execute the command "py group06w_legend.py"

### Notes ###
## for event triggered data publishing, user should set a `rule` and a `threashold` value
# | rule  |  check event       |
# ------------------------------
# |   0   |  val <  threashold |
# |   1   |  val <= threashold |
# |   2   |  val == threashold |
# |   3   |  val > threashold  |
# |   4   |  val >= threashold |