#ifndef ROBOT_H
#define ROBOT_H

#define MOTOR_MAX_RPM 600               // motor's max RPM
#define MAX_RPM_RATIO 1.0               // max RPM allowed for each MAX_RPM_ALLOWED = MOTOR_MAX_RPM * MAX_RPM_RATIO
#define MOTOR_OPERATING_VOLTAGE 36      // motor's operating voltage (used to calculate max RPM) 
#define MOTOR_POWER_MAX_VOLTAGE 36      // max voltage of the motor's power source (used to calculate max RPM) 
#define MOTOR_POWER_MEASURED_VOLTAGE 36 // current voltage reading of the power connected to the motor (used for calibration) 
#define WHEEL_DIAMETER 0.2032            // wheel's diameter in meters
#define LR_WHEELS_DISTANCE 0.71        // distance between left and right wheels 
#define PWM_BITS 10                     // PWM Resolution of the microcontroller 
#define PWM_FREQUENCY 20000             // PWM Frequency
#define PWM_MAX pow(2, PWM_BITS) - 1 * 0.7
#define PWM_MIN (pow(2, PWM_BITS) - 1) * -0.7

#endif