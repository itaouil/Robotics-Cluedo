#!/usr/bin/env python

# ROS, Python and OpenCV modules
from __future__ import division
import cv2
import rospy
import sys

# Vision classes
from vision import Detect

# Main
def main(args):

    # Initialise node
    rospy.init_node('detection', anonymous=True)

    detector = Detect()

    try:
        # Asking tf to find the transform of child_frame in parent_frame.
        rospy.spin()

    except KeyboardInterrupt as e:
        print('Error during main execution' + e)

    cv2.destroyAllWindows()

# Execute main
if __name__ == '__main__':
    main(sys.argv)
