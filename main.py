from time import sleep, time

import work_with_video_stream


def protection_activation():
    while True:
        start_time = time()

        work_with_video_stream.start_video_object_detection(
            work_with_video_stream.camera_1,
            work_with_video_stream.camera_settings["camera_1"]
        )

        work_with_video_stream.start_video_object_detection(
            work_with_video_stream.camera_2,
            work_with_video_stream.camera_settings["camera_2"]
        )

        work_with_video_stream.start_video_object_detection(
            work_with_video_stream.camera_3,
            work_with_video_stream.camera_settings["camera_3"]
        )

        if time() - start_time < 0.5:
            sleep(0.5 - (time() - start_time))

        if work_with_video_stream.cv2.waitKey(1) == ord("q"):
            break

    work_with_video_stream.camera_1.release()
    work_with_video_stream.camera_2.release()
    work_with_video_stream.camera_3.release()
    work_with_video_stream.cv2.destroyAllWindows()


if __name__ == "__main__":
    protection_activation()
