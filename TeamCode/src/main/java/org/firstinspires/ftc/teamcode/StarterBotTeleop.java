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

package org.firstinspires.ftc.teamcode;

import dev.nextftc.robot.opmode.BulkReadHook;
import dev.nextftc.robot.opmode.NextOpMode;

public abstract class StarterBotTeleop extends NextOpMode {
    protected final Robot robot;
    private final int velocityStep;

    protected StarterBotTeleop(Robot robot, double driveScale, int velocityStep) {
        super(robot, BulkReadHook.INSTANCE);// change this to lynx hubs asap
        this.robot = robot;
        this.velocityStep = velocityStep; //25
        robot.initialize(hardwareMap, gamepad1, driveScale);
        telemetry.addData("Status", "Initialized");
        telemetry.update();
    }

    @Override
    public void periodic() {
        if (gamepad1.dpadRightWasPressed()) robot.shooter.adjustVelocity(velocityStep);
        if (gamepad1.dpadLeftWasPressed()) robot.shooter.adjustVelocity(-velocityStep);
        telemetry.addData("TargetVelocity", robot.shooter.getTargetVelocity());
        telemetry.addData("Shooter Velocity", robot.shooter.getVelocity());
        telemetry.update();
    }

    @Override
    public void end() {
        robot.stop();
    }
}
