#include <Arduino.h>
#include "motor.h"

Hubmotor::Hubmotor(int pwm_pin, int direct_pin, int motor_max_rpm, bool invert_dir) :
    pwm_pin_(pwm_pin),
    direct_pin_(direct_pin),
    motor_max_rpm_(motor_max_rpm),
    invert_dir_(invert_dir)
{
    motor_min_rpm_ = motor_max_rpm_ * 0.10; //minimum rpm to overcome motor's static friction

    pinMode(pwm_pin_, OUTPUT);
    pinMode(direct_pin_, OUTPUT);
}

void Hubmotor::spin(int rpm)
{
    int pwm_value;
    bool direction;

    if(rpm < 0)
        direction = invert_dir_ ? LOW : HIGH;
    else
        direction = invert_dir_ ? HIGH : LOW;

    rpm = abs(rpm);
    if(rpm < motor_min_rpm_ && rpm != 0)
        rpm = motor_min_rpm_;
    else if(rpm > motor_max_rpm_)
        rpm = motor_max_rpm_;

    pwm_value = map(rpm, 0, motor_max_rpm_, 0, 255);
    digitalWrite(direct_pin_, direction);
    analogWrite(pwm_pin_, pwm_value);
}