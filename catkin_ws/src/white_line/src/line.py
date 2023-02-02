#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import sys
import numpy as np
import cv2
from matplotlib.pyplot import imshow

from std_msgs.msg import Int16MultiArray, Float32


def action(speed, angle):
    max_speed = rospy.get_param("max_speed", default=1.0)
    max_angle = rospy.get_param("max_angle", default=1.0)
    pub_speed = rospy.Publisher("/SpeedCommand", Float32, queue_size=1)
    pub_angle = rospy.Publisher("/AngleCommand", Float32, queue_size=1)
    pub_speed.publish(speed / 2 * max_speed)
    pub_angle.publish(angle * max_angle)


def callback(msg):
    scan = msg.data
    image = np.array(scan, dtype="uint8").reshape((480, 640, 4))
    gray = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
    thresh_img = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)[1]
    contours, hierarchy = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Calculating contour area
    contoursSize = []
    non_null_contours = []
    count_deleted_contours = 0
    for c in contours:
        area = max(7, cv2.contourArea(c))
        if area:
            non_null_contours.append(c)
            contoursSize.append(area)
        else:
            count_deleted_contours += 1
    print("deleted {} null contourss of {}".format(count_deleted_contours, len(contours)))

    # # Calculating the distribution
    # distribution = []
    # for i in range(min(contoursSize), max(contoursSize)+1):
    #     distribution.append(contoursSize.count(i))
    #
    # length = len(distribution)
    # mid = length * 1 / 2
    # size = length / 2
    # finish = int(mid + size / 2)
    # start = int(mid - size / 2)
    # print(contoursSize)
    # print(distribution)
    # print(start, mid, finish)
    #
    # validContours = []
    # for i in range(len(contoursSize)):
    #     if finish > contoursSize[i] > start:
    #         validContours.append(non_null_contours[i])

    # creating black image and drawing the selected contours
    img_contours = np.zeros(image.shape)
    cv2.drawContours(img_contours, non_null_contours, -1, (0, 255, 0), 1)

    # counting line position
    right_count = np.count_nonzero(img_contours[:, 320:])
    left_count = np.count_nonzero(img_contours[:, :320])

    # finding the highest white line position
    for line in range(len(img_contours[:, 1])):
        if np.count_nonzero(img_contours[line, :]):
            cv2.line(img_contours, (0, line), (640, line), (127, 0, 0), 1)
            break

    # find the furthest point of the contour from the middle
    maxi = (0, 0, 0)
    for contour in non_null_contours:
        for point in contour:
            dist = (320-point[0, 0])**2 + (480 - point[0, 1])**2
            if dist > maxi[0]:
                maxi = (dist, point[0, 0], point[0, 1])

    cv2.circle(img_contours, (maxi[1], maxi[2]), 8, (0, 0, 255), 2)

    # draw middle line and counts
    cv2.line(img_contours, (320, 0), (320, 480), (255, 0, 255), 1)
    cv2.putText(img_contours, str(left_count), (120, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,255), 2, cv2.LINE_AA)
    cv2.putText(img_contours, str(right_count), (520, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,255), 2, cv2.LINE_AA)

    # re-draw the contours on top
    cv2.drawContours(img_contours, non_null_contours, -1, (0, 255, 0), 1)
    cv2.imshow("image", img_contours)
    cv2.waitKey(0)

    action(0.6, 0.66 * maxi[1] / 640 - 0.75)


def listener(s):
    topic = rospy.get_param("image_datas", default="/ImageScan")
    rospy.Subscriber(topic, Int16MultiArray, s)
    rospy.spin()


if __name__ == '__main__':
    print("Starting")
    rospy.init_node('white_line', anonymous=True)

    try:
        listener(callback)
    except (rospy.ROSInterruptException, KeyboardInterrupt):
        print("error")
        sys.quit()

    print("over")
