from machine import Pin, ADC, PWM
import ufirebase as firebase
from time import sleep
import dht, machine, network, time

def wlan_connect(ssid,pwd):
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active() or not wlan.isconnected():
        wlan.active(True)
        wlan.connect(ssid,pwd)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    
wlan_connect('kmit', '12345678')

firebase.setURL("https://smart-agriculture-system-7f2c1-default-rtdb.firebaseio.com/")

#define the soil_mositure object for the soil moisture sensor
soil_moisture = ADC(Pin(33))
soil_moisture.atten(ADC.ATTN_11DB)  # sets the attenuation to 11db, which allows the ADC to handle input voltages in the range of 0-3.3v
#pin2 is using for pump
pump_pin=Pin(2,Pin.OUT)
d = dht.DHT22(machine.Pin(14))
# PWM setup
ir_pin = Pin(26, Pin.IN)  # Analog pin for IR sensor 1
buzzer_pin = Pin(13, Pin.OUT)
# ADC setup

while True:
  # moisture_raw variable contains the raw value read from ADC, which is a number between min=0 and max=4095 that the ADC can handle
    moisture_raw = soil_moisture.read()
    #print("moisture_raw:" ,+moisture_raw)
    
    # Read temperature and humidity from the sensor
    d.measure()
    temp_c = d.temperature()
    humidity = d.humidity()
    
    #To convert the raw value to a percentage moisture level, we first divide the raw value by 4095 to get a value between 0 and 1,
    #representing the percentage of the maximum voltage. We then multiply this value by 100 to convert it to a percentage.
    moisture_level = 100- (moisture_raw/4095)*100
    #print("moisture_level:", +moisture_level)
    
    if moisture_level > 30:
        soil="WET"
        print("soil: ",soil)
        pump = "OFF"
        print("pump: ",pump)
        pump_pin.off()
        
    if moisture_level<30:
        soil="DRY"
        print("soil: ", soil)
        pump= "ON"
        print("pump: ", pump)
        pump_pin.on()

    firebase.get("SAS", "var1", bg=0)
    print("SAS: "+str(firebase.var1))
    
    firebase.put("SAS", { "SM": soil, "DC": pump}, bg=0)
    
    # Print the temperature and humidity values
    print('Temperature: {:.2f}°C'.format(temp_c))
    print('Humidity: {:.2f}%'.format(humidity))
    firebase.put("dht22", { "humd": humidity, "temp": temp_c}, bg=0) 
    
    firebase.get("IR", "var1", bg=0)
    print("IR: "+str(firebase.var1))
    sens = firebase.var1["sensor"]
    print(sens)
    
    if 'ON' in sens:
        if ir_pin.value() == 0:  # IR sensor detects an object
            buzzer_pin.on()  # Turn on the buzzer
            print("Object detected!")
        else:
            buzzer_pin.off()  # Turn off the buzzer
            print("No object detected.")
    else:
        buzzer_pin.off()
        
    firebase.put("IR", { "sensor/ir": sens}, bg=0)
        
    time.sleep(1)