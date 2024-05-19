from machine import Pin, PWM, I2C
import utime

buzzer_pin = Pin(27, Pin.OUT)
buzzer = PWM(buzzer_pin)

led = Pin(5, Pin.OUT)

matrix_keys = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

keypad_rows = [9, 8, 7, 6]
keypad_columns = [5, 4, 3, 2]
password = "0519" 

col_pins = [Pin(pin, Pin.IN, Pin.PULL_DOWN) for pin in keypad_columns]
row_pins = [Pin(pin, Pin.OUT) for pin in keypad_rows]

trigger = Pin(10, Pin.OUT)
echo = Pin(11, Pin.IN)

for row in row_pins:
    row.value(1)

motion_detected_flag = False
password_correct_time = 0

def scankeys():
    entered_password = ""
    while len(entered_password) < 4:  # loops until 4 keys are pressed
        for row in range(4):
            row_pins[row].high()
            for col in range(4):
                if col_pins[col].value() == 1:
                    print("You have pressed: ", matrix_keys[row][col])
                    entered_password += matrix_keys[row][col]
                    utime.sleep(0.3)
                    row_pins[row].low()
                    if len(entered_password) == 4:
                        return entered_password
            row_pins[row].low()
    return entered_password

def measure_distance():
    trigger.low()
    utime.sleep_us(5)
    trigger.high()
    utime.sleep_us(10)
    trigger.low()
    
    while echo.value() == 0:
        signaloff = utime.ticks_us()
    while echo.value() == 1:
        signalon = utime.ticks_us()
        
    timepassed = utime.ticks_diff(signalon, signaloff)
    distance = (timepassed * 0.0343) / 2
    print("The distance from object is ", distance, "cm.")
    return distance

def check_distance():
    global motion_detected_flag, password_correct_time
    
    if not motion_detected_flag and utime.time() - password_correct_time >= 10:
        distance = measure_distance()
        if distance <= 50:  # cutoff is 50 cm
            motion_detected_flag = True
            print("Motion detected!")

            buzzer.duty_u16(1000)  
            buzzer.freq(500)
            led.on()

            print("Please enter the 4-digit password from the keypad")
            entered_password = scankeys()
            
            if entered_password == password:
                buzzer.duty_u16(0)
                led.off()
                print("Correct password entered, alarm deactivated.")
                password_correct_time = utime.time()
                utime.sleep(2)  # wait before allowing new motion detection

            motion_detected_flag = False

# main loop
try:
    while True:
        check_distance()
        utime.sleep(1) 

except KeyboardInterrupt:
    buzzer.deinit()
    led.off()
    print("Exiting...")

except KeyboardInterrupt:
    pir_pin.irq(handler=None) 
    buzzer.deinit()
    led.off()
    print("Exiting...")
