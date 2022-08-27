import cv2

import settings


camera_1 = cv2.VideoCapture(settings.full_address_cam_1)
camera_2 = cv2.VideoCapture(settings.full_address_cam_2)
camera_3 = cv2.VideoCapture(settings.full_address_cam_3)

while True:
    _, frame_1 = camera_1.read()
    _, frame_2 = camera_2.read()
    _, frame_3 = camera_3.read()

    cv2.imshow("Cam_1", frame_1)
    cv2.imshow("Cam_2", frame_2)
    cv2.imshow("Cam_3", frame_3)

    if cv2.waitKey(1) == ord("q"):
        break

camera_1.release()
camera_2.release()
camera_3.release()
cv2.destroyAllWindows()
