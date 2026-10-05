

package org.firstinspires.ftc.teamcode.mechanisms;

import com.pedropathing.ivy.Command;
import com.qualcomm.robotcore.hardware.CRServo;
import com.qualcomm.robotcore.hardware.DcMotor;
import com.qualcomm.robotcore.hardware.DcMotorEx;
import com.qualcomm.robotcore.hardware.DcMotorSimple;
import com.qualcomm.robotcore.hardware.Gamepad;
import com.qualcomm.robotcore.hardware.HardwareMap;
import com.qualcomm.robotcore.hardware.PIDFCoefficients;
import com.qualcomm.robotcore.util.SerialNumber;

import dev.nextftc.robot.Mechanism;

public class Shooter implements Mechanism {
    private DcMotorEx launcher;

    private Gamepad driver;
    private boolean enabled;
    private int targetVelocity;
    private int minimumVelocity;

    public void initialize(HardwareMap hardwareMap, Gamepad driver) {
        this.driver = driver;
        targetVelocity = 1400;
        minimumVelocity = 1300;
        launcher = hardwareMap.get(DcMotorEx.class, "launcher");

        launcher.setMode(DcMotor.RunMode.RUN_USING_ENCODER);
        launcher.setPIDFCoefficients(DcMotor.RunMode.RUN_USING_ENCODER,
                new PIDFCoefficients(40, 0, 0, 12.5));

        stop();
    }

    @Override
    public Command getDefaultCommand() {
        return infinite(() -> {
            if (driver.dpad_up) enabled = true;
            if (driver.dpad_down) enabled = false;
            launcher.setVelocity(enabled ? targetVelocity : 0);

        });
    }

    public boolean isReady() {
        return enabled && launcher.getVelocity() >= minimumVelocity;
    }

    public void adjustVelocity(int delta) {
        targetVelocity += delta;
        minimumVelocity += delta;
    }

    public int getTargetVelocity() {
        return targetVelocity;
    }

    public int getMinimumVelocity() {
        return minimumVelocity;
    }

    public double getVelocity() {
        return launcher.getVelocity();
    }

    public void stop() {
        enabled = false;
        launcher.setVelocity(0);
    }
}
