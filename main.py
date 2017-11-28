#!/usr/bin/env python

"""
    Main.
"""

# Modules
from __future__ import division
import rospy
import sys

# Ar-marker message data type
from sensor_msgs.msg import Image
from sensor_msgs.msg import LaserScan
from ar_track_alvar_msgs.msg import AlvarMarkers

# Modules
from modules import Navigation, Position, Recognition, GoToPose

class RoboticsCluedo:

    def __init__(self):
        """ Class constructor """

        # Detections array
        self.detections = []

        # Flag
        self.process = True
        self.initialised = False

        # Ar-marker and Scan data
        self.img_raw = None
        self.ar_data = None
        self.scan_data = None

        # Object instances
        self.gtp = GoToPose()
        self.pst = Position()
        self.nvg = Navigation()
        self.rcg = Recognition()

        # Marker & Image subscribers
        self.sub = rospy.Subscriber('scan', LaserScan, self.set_scan_data)
        self.ar_tracker = rospy.Subscriber('ar_pose_marker', AlvarMarkers, self.set_ar_data)
        # self.ar_tracker = rospy.Subscriber('ar_pose_marker', AlvarMarkers, self.debug)
        self.image_raw = rospy.Subscriber('camera/rgb/image_raw', Image, self.set_raw_image)

    def run(self):
        """
            The routine instructs the robot to position
            itself in a precise location in the map and
            starts the logic afterwards.

            Arguments:
                param1: The x coordinate in the map
                param2: The y coordinate in the map
        """
        # TODO: run GoToPose method
        rospy.loginfo("Robot reached the initial position")

        # Allow logic to be run
        self.initialised = True

        # Start logic
        self.logic()

    def debug(self, data):
        print(data)

    def logic(self):
        """
            Robot's logic handling decisions for when to navigate
            and when to run the computer vision modules, such
            as detection and recognition.

            Arguments:
                param1: The incoming data of the ar-marker
        """

        if self.initialised:

            while len(self.detections) < 2:

                # Get latest data
                data = self.get_ar_data()
                print("Latest data")

                # Run vision logic
                if bool(data) and self.process:

                    while not self.rcg.is_recognised():

                        print("Recog flag: ", self.rcg.is_recognised())

                        # Position in front of the AR
                        if not self.pst.ar_in_position():
                            rospy.loginfo("AR positioning...")
                            self.pst.toAR()

                        # Center in front of the image
                        elif self.pst.ar_in_position and not self.pst.img_centered:
                            rospy.loginfo("Image centering...")
                            self.pst.center_image(self.get_raw_image())

                        # Recognise image
                        elif self.pst.ar_in_position and self.pst.img_centered:
                            rospy.loginfo("Recognition...")
                            # Store recognised image
                            out = self.rcg.recognise(self.get_raw_image())
                            if out not in self.detections:
                                self.detections.append(out)

                            # Start new search
                            self.process = False
                            self.rcg.reset_rec_flag()
                            self.pst.reset_ar_flag()
                            self.pst.reset_center_flag()
                            break

                elif bool(data) and not self.process:
                    rospy.loginfo("Starting new search...")
                    self.nvg.rotate(90)
                    self.process = True

                else:
                    print("Navigation..")
                    rospy.loginfo("Robot is scanning the room")
                    self.nvg.navigate(self.get_scan_data())

                rospy.sleep(1)

            rospy.loginfo("Mission accomplished !")

    def set_raw_image(self, data):
        """
            Sets the incoming camera
            data to a global variable.

            Arguments:
                param1: Raw image data
        """
        self.img_raw = data

    def set_scan_data(self, data):
        """
            Sets the incoming LaserScan
            data to a global variable.

            Arguments:
                param1: Ar-marker data
        """
        self.scan_data = data

    def set_ar_data(self, data):
        """
            Sets the incoming ar-marker
            data to a global variable.

            Arguments:
                param1: Ar-marker data
        """
        self.ar_data = data

    def get_raw_image(self):
        """
            Returns the latest set
            image data.

            Returns:
                Last set image data (self.img_raw)
        """
        return self.img_raw

    def get_scan_data(self):
        """
            Returns the latest set
            ar-marker data.

            Returns:
                Last set ar-marker data
        """
        return self.scan_data.ranges

    def get_ar_data(self):
        """
            Returns the latest set
            ar-marker data.

            Returns:
                Last set ar-marker data
        """
        return self.ar_data.markers

def main(args):

    # Initialise node
    rospy.init_node('robotics_cluedo', anonymous=True)

    try:

        # Application instance
        rc = RoboticsCluedo()

        # Warm-up sensors
        rospy.sleep(3)

        # Run the logic
        rc.run()

        # Spin it baby !
        rospy.spin()

    except KeyboardInterrupt as e:
        print('Error during main execution' + e)

# Execute main
if __name__ == '__main__':
    main(sys.argv)
