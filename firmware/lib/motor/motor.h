// Copyright (c) 2021 Juan Miguel Jimeno
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#ifndef MOTOR_H
#define MOTOR_H

#include <Arduino.h>

class Hubmotor
{
    public:
        Hubmotor(int pwm_pin, int direct_pin, int motor_max_rpm, bool invert_dir);
        void spin(int rpm);
    private:
        int pwm_pin_;
        int direct_pin_;
        int motor_max_rpm_;
        int motor_min_rpm_;
        bool invert_dir_;
};

#endif
