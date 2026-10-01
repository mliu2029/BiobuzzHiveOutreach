/*   MIT License
 *   Copyright (c) [2026] [Base 10 Assets, LLC]
 *
 *   Permission is hereby granted, free of charge, to any person obtaining a copy
 *   of this software and associated documentation files (the "Software"), to deal
 *   in the Software without restriction, including without limitation the rights
 *   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 *   copies of the Software, and to permit persons to whom the Software is
 *   furnished to do so, subject to the following conditions:

 *   The above copyright notice and this permission notice shall be included in all
 *   copies or substantial portions of the Software.

 *   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 *   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 *   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 *   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 *   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 *   SOFTWARE.
 */

package org.firstinspires.ftc.teamcode.mechanisms;

import com.pedropathing.ivy.Command;
import com.qualcomm.robotcore.hardware.DcMotor;
import com.qualcomm.robotcore.hardware.Gamepad;
import com.qualcomm.robotcore.hardware.HardwareMap;
import dev.nextftc.robot.Mechanism;

public class Intake implements Mechanism {
    private DcMotor motor;
    private Gamepad driver;
    private double power;

    public void initialize(HardwareMap hardwareMap, Gamepad driver) {
        this.driver = driver;
        motor = hardwareMap.get(DcMotor.class, "intake");
        motor.setZeroPowerBehavior(DcMotor.ZeroPowerBehavior.BRAKE);
        stop();
    }

    @Override
    public Command getDefaultCommand() {
        return infinite(() -> {
            if (driver.circle) power = 1;
            if (driver.square) power = -1;
            applyPower();
        });
    }

    private void applyPower() {
        motor.setPower(power);
    }

    public void stop() {
        power = 0;
        applyPower();
    }
}
