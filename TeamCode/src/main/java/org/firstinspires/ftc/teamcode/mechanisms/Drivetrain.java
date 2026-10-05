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
import com.qualcomm.robotcore.hardware.DcMotorSimple;
import com.qualcomm.robotcore.hardware.Gamepad;
import com.qualcomm.robotcore.hardware.HardwareMap;
import dev.nextftc.robot.Mechanism;

public class Drivetrain implements Mechanism {
    private DcMotor leftFront;
    private DcMotor rightFront;
    private DcMotor leftBack;
    private DcMotor rightBack;
    private Gamepad driver;
    private double driveScale;

    public void initialize(HardwareMap hardwareMap, Gamepad driver, double driveScale) {
        this.driver = driver;
        this.driveScale = driveScale;
        leftFront = hardwareMap.get(DcMotor.class, "leftFrontDrive");
        rightFront = hardwareMap.get(DcMotor.class, "rightFrontDrive");
        leftBack = hardwareMap.get(DcMotor.class, "leftBackDrive");
        rightBack = hardwareMap.get(DcMotor.class, "rightBackDrive");

        leftFront.setDirection(DcMotor.Direction.FORWARD);
        rightFront.setDirection(DcMotor.Direction.REVERSE);
        leftBack.setDirection(DcMotor.Direction.REVERSE);
        rightBack.setDirection(DcMotor.Direction.FORWARD);
        leftFront.setZeroPowerBehavior(DcMotor.ZeroPowerBehavior.BRAKE);
        rightFront.setZeroPowerBehavior(DcMotor.ZeroPowerBehavior.BRAKE);
        leftBack.setZeroPowerBehavior(DcMotor.ZeroPowerBehavior.BRAKE);
        rightBack.setZeroPowerBehavior(DcMotor.ZeroPowerBehavior.BRAKE);
        stop();
    }

    @Override
    public Command getDefaultCommand() {
        return infinite(() -> drive(-driver.right_stick_y,
                driver.right_stick_x, driver.left_stick_x));
    }

    public void drive(double forward, double strafe, double rotate) {
        double lf = forward + strafe + rotate;
        double rf = forward - strafe - rotate;
        double lb = forward - strafe + rotate;
        double rb = forward + strafe - rotate;
        double maximum = Math.max(1.0, Math.max(Math.max(Math.abs(lf), Math.abs(rf)),
                Math.max(Math.abs(lb), Math.abs(rb))));
        leftFront.setPower(lf / maximum * driveScale);
        rightFront.setPower(rf / maximum * driveScale);
        leftBack.setPower(lb / maximum * driveScale);
        rightBack.setPower(rb / maximum * driveScale);
    }

    public void stop() {
        leftFront.setPower(0);
        rightFront.setPower(0);
        leftBack.setPower(0);
        rightBack.setPower(0);
    }
}
