#!/usr/bin/env python3

import time

import cv2
import numpy as np
import rospy

from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image


# Starting HSV ranges; lighting may require adjustment.
COLOR_RANGES = {
    "blue": [
        ((100, 100, 60), (130, 255, 255))
    ],
    "green": [
        ((35, 100, 60), (85, 255, 255))
    ],
    "red": [
        ((0, 100, 60), (10, 255, 255)),
        ((170, 100, 60), (179, 255, 255))
    ]
}


class ColorTracker:
    def __init__(self):
        self.bridge = CvBridge()

        self.image_topic = rospy.get_param(
            "~image_topic", "/usb_cam/image_raw"
        )
        self.color = rospy.get_param("~target_color", "blue").lower()
        self.enable_motion = rospy.get_param("~enable_motion", False)

        self.forward_speed = rospy.get_param("~forward_speed", 0.04)
        self.search_speed = rospy.get_param("~search_speed", 0.20)
        self.kp = rospy.get_param("~kp", 0.60)
        self.max_angular = rospy.get_param("~max_angular", 0.50)
        self.min_area = rospy.get_param("~min_area", 500.0)
        self.image_timeout = rospy.get_param("~image_timeout", 1.0)

        if self.color not in COLOR_RANGES:
            raise ValueError("target_color must be blue, green, or red")

        # Latest (target found, normalized horizontal error, receipt time).
        self.target_state = (False, 0.0, None)

        self.pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)

        self.image_sub = rospy.Subscriber(
            self.image_topic,
            Image,
            self.image_callback,
            queue_size=1,
            buff_size=2**22
        )

        rospy.loginfo(
            "Tracking %s on %s | motion enabled: %s",
            self.color,
            self.image_topic,
            self.enable_motion
        )

    def image_callback(self, msg):
        received_at = time.monotonic()

        try:
            frame = self.bridge.imgmsg_to_cv2(
                msg, desired_encoding="bgr8"
            )

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = np.zeros(hsv.shape[:2], dtype=np.uint8)

            for lower, upper in COLOR_RANGES[self.color]:
                color_mask = cv2.inRange(
                    hsv,
                    np.array(lower, dtype=np.uint8),
                    np.array(upper, dtype=np.uint8)
                )
                mask = cv2.bitwise_or(mask, color_mask)

            # Remove small specks and fill small holes.
            kernel = np.ones((3, 3), dtype=np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

            contours = cv2.findContours(
                mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )[-2]

            found = False
            error = 0.0

            if contours:
                largest = max(contours, key=cv2.contourArea)

                if cv2.contourArea(largest) >= self.min_area:
                    moments = cv2.moments(largest)

                    if moments["m00"] > 0.0:
                        cx = moments["m10"] / moments["m00"]
                        cy = moments["m01"] / moments["m00"]

                        height, width = frame.shape[:2]
                        center_x = width / 2.0

                        # Left: negative error. Right: positive error.
                        error = (cx - center_x) / center_x
                        found = True

            self.target_state = (found, error, received_at)

        except (CvBridgeError, cv2.error) as exc:
            # A processing failure must not trigger search motion.
            self.target_state = (False, 0.0, None)
            rospy.logerr_throttle(
                2.0, "Image processing failed: %s" % exc
            )

    def run(self):
        rate = rospy.Rate(10)

        try:
            while not rospy.is_shutdown():
                found, error, received_at = self.target_state
                requested = Twist()

                if received_at is None:
                    status = "WAITING FOR VALID IMAGE"

                elif time.monotonic() - received_at > self.image_timeout:
                    status = "STALE CAMERA: STOP"

                elif found:
                    status = "TRACKING"

                    requested.linear.x = self.forward_speed

                    # Target right -> turn right (negative angular.z).
                    angular = -self.kp * error
                    requested.angular.z = max(
                        -self.max_angular,
                        min(angular, self.max_angular)
                    )

                else:
                    status = "SEARCHING"
                    requested.linear.x = 0.0
                    requested.angular.z = self.search_speed

                # Test mode publishes zero velocity, but logs what
                # the controller would request.
                output = requested if self.enable_motion else Twist()
                self.pub.publish(output)

                rospy.loginfo_throttle(
                    1.0,
                    "%s | error=%+.2f | requested linear=%.2f "
                    "angular=%+.2f | motion=%s"
                    % (
                        status,
                        error,
                        requested.linear.x,
                        requested.angular.z,
                        self.enable_motion
                    )
                )

                rate.sleep()

        finally:
            # Best-effort stop request on exit.
            self.pub.publish(Twist())


if __name__ == "__main__":
    rospy.init_node("turtlebot3_color_tracker", anonymous=True)

    try:
        tracker = ColorTracker()
        tracker.run()
    except (rospy.ROSInterruptException, KeyboardInterrupt):
        pass