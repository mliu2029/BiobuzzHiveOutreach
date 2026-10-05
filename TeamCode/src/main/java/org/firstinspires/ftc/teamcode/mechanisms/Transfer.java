package org.firstinspires.ftc.teamcode.mechanisms;

import com.pedropathing.ivy.Command;
import com.qualcomm.robotcore.hardware.DcMotor;
import com.qualcomm.robotcore.hardware.DcMotorEx;
import com.qualcomm.robotcore.hardware.Gamepad;
import com.qualcomm.robotcore.hardware.HardwareMap;

import dev.nextftc.robot.Mechanism;

public class Transfer implements Mechanism {
    private DcMotorEx transfer;
    private DcMotorEx leftTransfer;

    private Gamepad driver;

    public void initialize(HardwareMap hardwareMap, Gamepad driver) {
        this.driver = driver;
        transfer = hardwareMap.get(DcMotorEx.class, "transfer");
        leftTransfer=hardwareMap.get(DcMotorEx.class,"transfer2");
        transfer.setZeroPowerBehavior(DcMotor.ZeroPowerBehavior.BRAKE);
        leftTransfer.setZeroPowerBehavior(DcMotor.ZeroPowerBehavior.BRAKE);

        stop();
    }

    @Override
    public Command getDefaultCommand() {
        return infinite(() -> {
            if (driver.left_bumper) {
                setPower(-1);
            } else if (driver.right_bumper) {
                setPower(1);
            } else {
                stop();
            }
        });
    }

    private void setPower(double power) {
       transfer.setPower(power);
       leftTransfer.setPower(power);
    }

    public void stop() {
        setPower(0);
    }
}
