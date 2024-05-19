from machine import Pin, PWM, I2C
import utime

pir_pin = Pin(18, Pin.IN)

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
password = "0"

col_pins = [Pin(pin, Pin.IN, Pin.PULL_DOWN) for pin in keypad_columns]
row_pins = [Pin(pin, Pin.OUT) for pin in keypad_rows]

for row in row_pins:
    row.value(1)

motion_detected_flag = False
password_correct_time = 0

def scankeys():
    for row in range(4):
        row_pins[row].high()
        for col in range(4):
            if col_pins[col].value() == 1:
                print("You have pressed: ", matrix_keys[row][col])
                key_press = matrix_keys[row][col]
                utime.sleep(0.3)  # Debounce delay
                row_pins[row].low()
                return key_press 
        row_pins[row].low()
    return None

def motion_detected(pin):
    global motion_detected_flag, password_correct_time
    if not motion_detected_flag:
        motion_detected_flag = True
        print("Motion detected!")

        buzzer.duty_u16(1000)  
        buzzer.freq(500)
        led.on()

        print("Please enter a key from the keypad")
        key = None
        while key is None:
            key = scankeys()
        
        if key == password:
            buzzer.duty_u16(0)
            led.off()
            print("Correct password entered, alarm deactivated.")
            password_correct_time = utime.time()
            utime.sleep(8)  # wait before allowing new motion detection

        motion_detected_flag = False

# Configure the PIR sensor to trigger an interrupt on motion
pir_pin.irq(trigger=Pin.IRQ_RISING, handler=motion_detected)

# Main loop
try:
    while True:
        current_time = utime.time()
        if current_time - password_correct_time >= 10:
            print("Waiting for motion...")
            utime.sleep(1)

except KeyboardInterrupt:
    pir_pin.irq(handler=None) 
    buzzer.deinit()
    led.off()
    print("Exiting...")