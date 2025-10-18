#include <Arduino.h>
#include "config.h"
#include "motor.h"

Hubmotor motor_1(MOTOR1_PWM, MOTOR1_DIR, MOTOR_MAX_RPM, MOTOR1_INV);
Hubmotor motor_2(MOTOR2_PWM, MOTOR2_DIR, MOTOR_MAX_RPM, MOTOR2_INV);
Hubmotor motor_3(MOTOR3_PWM, MOTOR3_DIR, MOTOR_MAX_RPM, MOTOR3_INV);
Hubmotor motor_4(MOTOR4_PWM, MOTOR4_DIR, MOTOR_MAX_RPM, MOTOR4_INV);

void setup() {
    Serial.begin(115200);
}

void loop() {
    motor_1.spin(200);
    motor_2.spin(200);
    motor_3.spin(200);
    motor_4.spin(200);
    delay(2000);

    motor_1.spin(0);
    motor_2.spin(0);
    motor_3.spin(0);
    motor_4.spin(0);
    delay(1000);

    motor_1.spin(-200);
    motor_2.spin(-200);
    motor_3.spin(-200);
    motor_4.spin(-200);
    delay(2000);

    motor_1.spin(0);
    motor_2.spin(0);
    motor_3.spin(0);
    motor_4.spin(0);
    delay(1000);
}