#!/usr/bin/env python3

import math
import select
import sys
import termios
import time
import tty

import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


SAFETY_DISTANCE = 0.30                  # meters
FRONT_HALF_ANGLE = math.radians(15)      # +/- 15 degrees
REAR_HALF_ANGLE = math.radians(15)       # +/- 15 degrees
SCAN_TIMEOUT = 1.0                      # seconds

# Latest (front distance, rear distance, scan reception time).
scan_state = (None, None, None)


def scan_callback(msg):
    """Find the nearest valid distances in front and behind."""
    global scan_state

    front_ranges = []
    rear_ranges = []

    for i, distance in enumerate(msg.ranges):
        # Reject infinity, NaN, and zero/negative readings.
        if not math.isfinite(distance) or distance <= 0.0:
            continue

        # Reject readings outside the reported measurement range.
        if not msg.range_min <= distance <= msg.range_max:
            continue

        angle = msg.angle_min + i * msg.angle_increment

        # Normalize the angle to [-pi, pi].
        angle = math.atan2(math.sin(angle), math.cos(angle))

        # Front sector centered on 0 degrees.
        if abs(angle) <= FRONT_HALF_ANGLE:
            front_ranges.append(distance)

        # Rear sector centered on +/- 180 degrees.
        if math.pi - abs(angle) <= REAR_HALF_ANGLE:
            rear_ranges.append(distance)

    front_distance = min(front_ranges) if front_ranges else None
    rear_distance = min(rear_ranges) if rear_ranges else None

    # Update both distances and their reception time together.
    scan_state = (
        front_distance,
        rear_distance,
        time.monotonic()
    )


def get_key():
    """Read one available key without blocking."""
    ready, _, _ = select.select([sys.stdin], [], [], 0.0)

    if ready:
        return sys.stdin.read(1).lower()

    return ""


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def format_distance(distance):
    if distance is None:
        return "unknown"

    return f"{distance:.2f} m"


def move():
    rospy.init_node("turtlebot3_keyboard_safety", anonymous=True)

    pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)

    scan_sub = rospy.Subscriber(
        "/scan",
        LaserScan,
        scan_callback,
        queue_size=1
    )

    rate = rospy.Rate(10)

    linear_velocity = 0.0
    angular_velocity = 0.0

    linear_step = 0.02       # m/s per keypress
    angular_step = 0.1       # rad/s per keypress

    max_linear = 0.15        # m/s
    max_angular = 0.8        # rad/s

    settings = termios.tcgetattr(sys.stdin)
    previous_reason = None

    print(
        "TurtleBot keyboard control with front/rear LiDAR safety\n"
        "\n"
        "W: increase forward velocity\n"
        "S: decrease forward velocity / reverse\n"
        "A: increase left-turn velocity\n"
        "D: increase right-turn velocity\n"
        "SPACE or X: stop translation and rotation\n"
        "Q or Ctrl+C: stop and quit\n"
        "\n"
        "Safety rules:\n"
        "  Front obstacle below 0.30 m: block forward and reverse\n"
        "  Rear obstacle below 0.30 m: block reverse only\n"
        "  Missing/stale scans: block all linear movement\n"
        "  Unknown front clearance: block all linear movement\n"
        "  Unknown rear clearance: block reverse\n"
        "\n"
        "Rotation is not blocked by these safety rules.\n"
        "After a safety stop, press W/S again to move.\n"
        "Releasing a key does not stop the robot."
    )

    try:
        tty.setcbreak(sys.stdin.fileno())

        while not rospy.is_shutdown():
            key = get_key()

            if key == "w":
                linear_velocity += linear_step

            elif key == "s":
                linear_velocity -= linear_step

            elif key == "a":
                angular_velocity += angular_step

            elif key == "d":
                angular_velocity -= angular_step

            elif key in (" ", "x"):
                linear_velocity = 0.0
                angular_velocity = 0.0

            elif key == "q":
                break

            linear_velocity = clamp(
                linear_velocity,
                -max_linear,
                max_linear
            )

            angular_velocity = clamp(
                angular_velocity,
                -max_angular,
                max_angular
            )

            # Read one consistent snapshot of the latest scan.
            front_distance, rear_distance, received_at = scan_state

            if received_at is None:
                reason = "Waiting for LiDAR data"

            elif time.monotonic() - received_at > SCAN_TIMEOUT:
                reason = "LiDAR data is stale"

            elif front_distance is None:
                reason = "No valid front LiDAR measurements"

            elif front_distance < SAFETY_DISTANCE:
                # Preserve the lab's front-stop rule in both directions.
                reason = "Front obstacle within 0.30 m"

            elif linear_velocity < 0.0:
                # Rear clearance is required when reversing.
                if rear_distance is None:
                    reason = "No valid rear LiDAR measurements"

                elif rear_distance < SAFETY_DISTANCE:
                    reason = "Rear obstacle within 0.30 m"

                else:
                    reason = ""

            else:
                reason = ""

            # Clear the stored linear command when blocked.
            # This prevents automatic resumption after a safety stop.
            if reason:
                linear_velocity = 0.0

            if reason != previous_reason:
                if reason:
                    print(f"\nSAFETY STOP: {reason}")
                else:
                    print(
                        "\nNo linear safety block "
                        "for the current command."
                    )

                previous_reason = reason

            vel_msg = Twist()
            vel_msg.linear.x = linear_velocity
            vel_msg.angular.z = angular_velocity

            pub.publish(vel_msg)

            if key:
                print(
                    f"Linear: {linear_velocity:+.2f} m/s | "
                    f"Angular: {angular_velocity:+.2f} rad/s | "
                    f"Front: {format_distance(front_distance)} | "
                    f"Rear: {format_distance(rear_distance)}"
                )

            rate.sleep()

    except (rospy.ROSInterruptException, KeyboardInterrupt):
        pass

    finally:
        try:
            # Best-effort stop request on exit.
            pub.publish(Twist())
        finally:
            termios.tcsetattr(
                sys.stdin,
                termios.TCSADRAIN,
                settings
            )


if __name__ == "__main__":
    move()