#!/usr/bin/env python3
"""Compare migrated Java controls with the original StarterBot sources.

Usage: python3 tools/verify_starterbot_migration.py /path/to/StarterBot
Requires a JDK. FTC hardware and NextFTC default-command execution are simulated;
this checks retained hardware behavior and absence of the retired intake servos,
not Android runtime registration or real hardware.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROFILES = ["BioBuzzStarterbotTeleopMecanum", "BioBuzzStarterbotTeleopMecanum30", "biobuzz50speed"]
REPO = Path(__file__).resolve().parents[1]
SOURCE_PACKAGE = Path("TeamCode/src/main/java/org/firstinspires/ftc/teamcode")

STUBS = {
    "com/qualcomm/robotcore/hardware/DcMotorSimple.java": """
package com.qualcomm.robotcore.hardware;
public class DcMotorSimple {
    public enum Direction { FORWARD, REVERSE }
    public Direction direction = Direction.FORWARD;
    public void setDirection(Direction value) { direction = value; }
}
""",
    "com/qualcomm/robotcore/hardware/DcMotor.java": """
package com.qualcomm.robotcore.hardware;
public class DcMotor extends DcMotorSimple {
    public enum ZeroPowerBehavior { BRAKE, FLOAT }
    public enum RunMode { RUN_USING_ENCODER }
    public double power;
    public ZeroPowerBehavior zeroPowerBehavior;
    public RunMode mode;
    public void setPower(double value) { power = value; }
    public void setZeroPowerBehavior(ZeroPowerBehavior value) { zeroPowerBehavior = value; }
    public void setMode(RunMode value) { mode = value; }
}
""",
    "com/qualcomm/robotcore/hardware/DcMotorEx.java": """
package com.qualcomm.robotcore.hardware;
public class DcMotorEx extends DcMotor {
    public double measuredVelocity, requestedVelocity;
    public PIDFCoefficients pidf;
    public void setVelocity(double value) { requestedVelocity = value; }
    public double getVelocity() { return measuredVelocity; }
    public void setPIDFCoefficients(RunMode mode, PIDFCoefficients value) { pidf = value; }
}
""",
    "com/qualcomm/robotcore/hardware/PIDFCoefficients.java": """
package com.qualcomm.robotcore.hardware;
public class PIDFCoefficients {
    public final double p, i, d, f;
    public PIDFCoefficients(double p, double i, double d, double f) {
        this.p = p; this.i = i; this.d = d; this.f = f;
    }
}
""",
    "com/qualcomm/robotcore/hardware/CRServo.java": """
package com.qualcomm.robotcore.hardware;
public class CRServo extends DcMotorSimple {
    public double power;
    public void setPower(double value) { power = value; }
}
""",
    "com/qualcomm/robotcore/hardware/HardwareMap.java": """
package com.qualcomm.robotcore.hardware;
import java.util.LinkedHashMap;
import java.util.Map;
public class HardwareMap {
    public final Map<String, Object> devices = new LinkedHashMap<>();
    public <T> T get(Class<T> type, String name) {
        if (!devices.containsKey(name)) throw new AssertionError("Missing hardware: " + name);
        return type.cast(devices.get(name));
    }
}
""",
    "com/qualcomm/robotcore/hardware/Gamepad.java": """
package com.qualcomm.robotcore.hardware;
public class Gamepad {
    public float right_stick_y, right_stick_x, left_stick_x;
    public boolean circle, square, dpad_up, dpad_down, dpad_left, dpad_right;
    public boolean left_bumper, right_bumper;
    private boolean previousRight, previousLeft;
    public boolean dpadRightWasPressed() {
        boolean edge = dpad_right && !previousRight;
        previousRight = dpad_right;
        return edge;
    }
    public boolean dpadLeftWasPressed() {
        boolean edge = dpad_left && !previousLeft;
        previousLeft = dpad_left;
        return edge;
    }
}
""",
    "org/firstinspires/ftc/robotcore/external/Telemetry.java": """
package org.firstinspires.ftc.robotcore.external;
public class Telemetry {
    public void addData(String key, Object value) {}
    public void update() {}
}
""",
    "com/qualcomm/robotcore/eventloop/opmode/OpMode.java": """
package com.qualcomm.robotcore.eventloop.opmode;
import com.qualcomm.robotcore.hardware.*;
import org.firstinspires.ftc.robotcore.external.Telemetry;
public abstract class OpMode {
    public Gamepad gamepad1 = new Gamepad();
    public HardwareMap hardwareMap = new HardwareMap();
    public Telemetry telemetry = new Telemetry();
    public abstract void init();
    public void init_loop() {}
    public void start() {}
    public abstract void loop();
    public void stop() {}
    public double getRuntime() { return 0; }
}
""",
    "com/qualcomm/robotcore/eventloop/opmode/TeleOp.java": """
package com.qualcomm.robotcore.eventloop.opmode;
public @interface TeleOp { String name(); String group(); }
""",
    "com/pedropathing/ivy/Command.java": """
package com.pedropathing.ivy;
public interface Command { void execute(); }
""",
    "com/pedropathing/ivy/CommandBuilder.java": """
package com.pedropathing.ivy;
public class CommandBuilder implements Command {
    private final Runnable action;
    public CommandBuilder(Runnable action) { this.action = action; }
    public void execute() { action.run(); }
}
""",
    "dev/nextftc/robot/Mechanism.java": """
package dev.nextftc.robot;
import com.pedropathing.ivy.*;
public interface Mechanism {
    default CommandBuilder infinite(Runnable action) { return new CommandBuilder(action); }
    default Command getDefaultCommand() { return infinite(() -> {}); }
}
""",
    "dev/nextftc/robot/NextRobot.java": """
package dev.nextftc.robot;
import java.util.Set;
public interface NextRobot { Set<Mechanism> getMechanisms(); }
""",
    "dev/nextftc/robot/opmode/BulkReadHook.java": """
package dev.nextftc.robot.opmode;
public class BulkReadHook { public static final BulkReadHook INSTANCE = new BulkReadHook(); }
""",
    "dev/nextftc/robot/opmode/NextOpMode.java": """
package dev.nextftc.robot.opmode;
import com.qualcomm.robotcore.hardware.*;
import dev.nextftc.robot.NextRobot;
import org.firstinspires.ftc.robotcore.external.Telemetry;
public abstract class NextOpMode {
    public static HardwareMap activeHardwareMap;
    public static Gamepad activeGamepad;
    public final HardwareMap hardwareMap = activeHardwareMap;
    public final Gamepad gamepad1 = activeGamepad;
    public final Telemetry telemetry = new Telemetry();
    public NextOpMode(NextRobot robot, BulkReadHook hook) {}
    public void start() {}
    public void periodic() {}
    public void end() {}
}
""",
    "dev/nextftc/robot/opmode/NextTeleop.java": """
package dev.nextftc.robot.opmode;
import java.lang.annotation.*;
@Retention(RetentionPolicy.RUNTIME)
public @interface NextTeleop { String name(); String group(); }
""",
}

HARNESS = r"""
import java.util.*;
import com.qualcomm.robotcore.eventloop.opmode.OpMode;
import com.qualcomm.robotcore.hardware.*;
import com.pedropathing.ivy.Command;
import dev.nextftc.robot.opmode.*;
import org.firstinspires.ftc.teamcode.Robot;

public class MigrationRegression {
    static final String[] PROFILES = {"BioBuzzStarterbotTeleopMecanum", "BioBuzzStarterbotTeleopMecanum30", "biobuzz50speed"};
    static final String[] NAMES = {"mec drive teleop", "30% mec drive teleop", "50% mec drive teleop"};
    static final String[] MOTORS = {"leftFrontDrive", "rightFrontDrive", "leftBackDrive", "rightBackDrive", "intake", "launcher"};
    static final String[] SERVOS = {"windmillServo"};
    // Only the original source needs these devices; migrated hardware omits them.
    static final String[] RETIRED_SERVOS = {"left_intake_servo", "right_intake_servo"};
    static int frames;

    static HardwareMap hardware(boolean legacyIntakeServos) {
        HardwareMap map = new HardwareMap();
        for (String name : MOTORS) map.devices.put(name, new DcMotorEx());
        for (String name : SERVOS) map.devices.put(name, new CRServo());
        if (legacyIntakeServos) {
            for (String name : RETIRED_SERVOS) map.devices.put(name, new CRServo());
        }
        return map;
    }
    static void equal(Object expected, Object actual, String message) {
        if (!Objects.equals(expected, actual)) throw new AssertionError(message + ": " + expected + " != " + actual);
    }
    static void near(double expected, double actual, String message) {
        if (Math.abs(expected - actual) > 1e-12) throw new AssertionError(message + ": " + expected + " != " + actual);
    }
    static void compareHardware(HardwareMap expected, HardwareMap actual) {
        Set<String> retainedNames = new LinkedHashSet<>(expected.devices.keySet());
        retainedNames.removeAll(Arrays.asList(RETIRED_SERVOS));
        equal(retainedNames, actual.devices.keySet(), "retained hardware names; no intake servos");
        for (String name : MOTORS) {
            DcMotorEx old = expected.get(DcMotorEx.class, name), migrated = actual.get(DcMotorEx.class, name);
            near(old.power, migrated.power, name + " power");
            near(old.requestedVelocity, migrated.requestedVelocity, name + " velocity target");
            equal(old.direction, migrated.direction, name + " direction");
            equal(old.zeroPowerBehavior, migrated.zeroPowerBehavior, name + " brake");
            equal(old.mode, migrated.mode, name + " run mode");
            if (old.pidf != null) {
                near(old.pidf.p, migrated.pidf.p, "P"); near(old.pidf.i, migrated.pidf.i, "I");
                near(old.pidf.d, migrated.pidf.d, "D"); near(old.pidf.f, migrated.pidf.f, "F");
            }
        }
        for (String name : SERVOS) if (expected.devices.containsKey(name)) {
            CRServo old = expected.get(CRServo.class, name), migrated = actual.get(CRServo.class, name);
            near(old.power, migrated.power, name + " power");
            equal(old.direction, migrated.direction, name + " direction");
        }
    }
    static void input(Gamepad pad, int mask, float forward, float strafe, float rotate) {
        pad.circle = (mask & 1) != 0; pad.square = (mask & 2) != 0;
        pad.dpad_up = (mask & 4) != 0; pad.dpad_down = (mask & 8) != 0;
        pad.dpad_right = (mask & 16) != 0; pad.dpad_left = (mask & 32) != 0;
        pad.right_bumper = (mask & 64) != 0; pad.left_bumper = (mask & 128) != 0;
        pad.right_stick_y = forward; pad.right_stick_x = strafe; pad.left_stick_x = rotate;
    }
    static void frame(OpMode original, NextOpMode migrated, Robot robot, List<Command> commands,
                      int mask, float forward, float strafe, float rotate, double velocity) throws Exception {
        input(original.gamepad1, mask, forward, strafe, rotate);
        input(migrated.gamepad1, mask, forward, strafe, rotate);
        original.hardwareMap.get(DcMotorEx.class, "launcher").measuredVelocity = velocity;
        migrated.hardwareMap.get(DcMotorEx.class, "launcher").measuredVelocity = velocity;
        original.loop();
        migrated.periodic();
        for (Command command : commands) command.execute();
        compareHardware(original.hardwareMap, migrated.hardwareMap);
        near(original.getClass().getField("LAUNCHER_TARGET_VELOCITY").getInt(original), robot.shooter.getTargetVelocity(), "shooter target adjustment");
        near(original.getClass().getField("LAUNCHER_MIN_VELOCITY").getInt(original), robot.shooter.getMinimumVelocity(), "shooter readiness adjustment");
        frames++;
    }
    public static void main(String[] args) throws Exception {
        // Reuse one injected robot to exercise resets when switching profiles.
        Robot robot = new Robot();
        for (int cycle = 0; cycle < 2; cycle++) for (int profile = 0; profile < PROFILES.length; profile++) {
            OpMode original = (OpMode) Class.forName("legacy." + PROFILES[profile]).getConstructor().newInstance();
            original.hardwareMap = hardware(profile != 0);
            original.init();
            original.start();
            NextOpMode.activeHardwareMap = hardware(false);
            NextOpMode.activeGamepad = new Gamepad();
            Class<?> migratedClass = Class.forName("org.firstinspires.ftc.teamcode." + PROFILES[profile]);
            NextTeleop annotation = migratedClass.getAnnotation(NextTeleop.class);
            equal(NAMES[profile], annotation.name(), "Driver Station name");
            equal("StarterBot", annotation.group(), "Driver Station group");
            NextOpMode migrated = (NextOpMode) migratedClass.getConstructor(Robot.class).newInstance(robot);
            migrated.start();
            List<Command> commands = new ArrayList<>();
            robot.getMechanisms().forEach(mechanism -> commands.add(mechanism.getDefaultCommand()));
            compareHardware(original.hardwareMap, migrated.hardwareMap);
            // Release/hold sequences, simultaneous buttons, and exact ready thresholds.
            int[] masks = {0, 1, 0, 2, 0, 3, 1, 0, 4, 68, 64, 192, 8, 128, 0, 16, 16, 0, 32, 32, 0, 48, 0, 12};
            for (int mask : masks) frame(original, migrated, robot, commands, mask, 1, -1, 1, 1400);
            frame(original, migrated, robot, commands, 4, 0, 0, 0, 0);
            int threshold = robot.shooter.getMinimumVelocity();
            for (double velocity : new double[]{threshold - 1, threshold, threshold + 1})
                frame(original, migrated, robot, commands, 64, 0, 0, 0, velocity);
            Random random = new Random(20260930L + profile);
            for (int i = 0; i < 2000; i++) frame(original, migrated, robot, commands,
                random.nextInt(256), random.nextFloat() * 2 - 1, random.nextFloat() * 2 - 1,
                random.nextFloat() * 2 - 1, random.nextInt(2501));
            original.stop(); migrated.end();
            compareHardware(original.hardwareMap, migrated.hardwareMap);
            for (Object device : migrated.hardwareMap.devices.values()) {
                if (device instanceof DcMotorEx) {
                    near(0, ((DcMotorEx) device).power, "stop motor power");
                    near(0, ((DcMotorEx) device).requestedVelocity, "stop motor velocity");
                } else near(0, ((CRServo) device).power, "stop servo power");
            }
        }
        System.out.println("PASS: " + frames + " control frames match the original TeleOps for retained hardware across all 3 profiles, with no intake servos, including reinitialization and stop.");
    }
}
"""


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    source = Path(sys.argv[1]).resolve() / SOURCE_PACKAGE
    for tool in ("javac", "java"):
        if shutil.which(tool) is None:
            raise SystemExit(f"Missing JDK tool: {tool}")
    with tempfile.TemporaryDirectory(prefix="starterbot-regression-") as temp:
        root = Path(temp)
        for name, content in STUBS.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        for profile in PROFILES:
            path = root / "legacy" / f"{profile}.java"
            path.parent.mkdir(exist_ok=True)
            path.write_text((source / f"{profile}.java").read_text().replace(
                "package org.firstinspires.ftc.teamcode;", "package legacy;"))
        migrated = REPO / SOURCE_PACKAGE
        for path in list(migrated.glob("*.java")) + list((migrated / "mechanisms").glob("*.java")):
            destination = root / "org/firstinspires/ftc/teamcode" / path.relative_to(migrated)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
        (root / "MigrationRegression.java").write_text(HARNESS)
        classes = root / "classes"
        subprocess.run(["javac", "-d", str(classes), *map(str, root.rglob("*.java"))], check=True)
        subprocess.run(["java", "-cp", str(classes), "MigrationRegression"], check=True)


if __name__ == "__main__":
    main()
