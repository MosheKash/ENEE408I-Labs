#!/usr/bin/env python3

import sys
import select
import termios
import tty

import rospy
from geometry_msgs.msg import Twist


def get_key():
    """Return a key if one is available; otherwise return an empty string."""
    ready, _, _ = select.select([sys.stdin], [], [], 0.0)

    if ready:
        return sys.stdin.read(1).lower()

    return ""


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def move():
    rospy.init_node("turtlebot3_keyboard_control", anonymous=True)

    pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
    rate = rospy.Rate(10)

    linear_velocity = 0.0
    angular_velocity = 0.0

    linear_step = 0.02       # m/s per keypress
    angular_step = 0.1       # rad/s per keypress

    # Conservative limits chosen for this example.
    max_linear = 0.15       # m/s
    max_angular = 0.8       # rad/s

    settings = termios.tcgetattr(sys.stdin)

    print(
        "TurtleBot keyboard control\n"
        "W: increase forward velocity\n"
        "S: decrease forward velocity / reverse\n"
        "A: increase left-turn velocity\n"
        "D: increase right-turn velocity\n"
        "SPACE or X: stop\n"
        "Q or Ctrl+C: stop and quit\n"
        "Click this terminal before pressing keys."
    )

    try:
        # Read individual keys without requiring Enter.
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
                linear_velocity, -max_linear, max_linear
            )
            angular_velocity = clamp(
                angular_velocity, -max_angular, max_angular
            )

            vel_msg = Twist()
            vel_msg.linear.x = linear_velocity
            vel_msg.angular.z = angular_velocity

            pub.publish(vel_msg)

            if key:
                print(
                    f"Linear: {linear_velocity:+.2f} m/s | "
                    f"Angular: {angular_velocity:+.2f} rad/s"
                )

            rate.sleep()

    except (rospy.ROSInterruptException, KeyboardInterrupt):
        pass

    finally:
        try:
            # Request a complete stop before exiting.
            pub.publish(Twist())
        finally:
            # Restore the terminal even if publishing fails.
            termios.tcsetattr(
                sys.stdin, termios.TCSADRAIN, settings
            )


if __name__ == "__main__":
    move()