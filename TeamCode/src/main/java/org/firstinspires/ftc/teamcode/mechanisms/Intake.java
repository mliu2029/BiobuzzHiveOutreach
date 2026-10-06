

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
