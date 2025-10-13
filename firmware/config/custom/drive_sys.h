#ifndef DRIVE_SYS_H
#define DRIVE_SYS_H
#include "robot.h"
#define K_P 0.1
#define K_I 0.03
#define K_D 0

/*
ROBOT ORIENTATION
         FRONT
    MOTOR1  MOTOR2  (2WD/ACKERMANN)
    MOTOR3  MOTOR4  (4WD/MECANUM)
         BACK
*/

bool MOTOR1_INV = -1;
bool MOTOR2_INV = -1;
bool MOTOR3_INV = -1;
bool MOTOR4_INV = -1;

#define MOTOR1_PWM 14
#define MOTOR1_DIR 15

#define MOTOR2_PWM 8
#define MOTOR2_DIR 10

#define MOTOR3_PWM 5
#define MOTOR3_DIR 7

#define MOTOR4_PWM 2
#define MOTOR4_DIR 4

#endif