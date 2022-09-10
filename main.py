import work_with_video_stream


if __name__ == "__main__":
    while True:
        work_with_video_stream.start_video_object_detection(
            work_with_video_stream.camera_1,
            work_with_video_stream.settings_camera_1
        )
        work_with_video_stream.start_video_object_detection(
            work_with_video_stream.camera_2,
            work_with_video_stream.settings_camera_2
        )
        work_with_video_stream.start_video_object_detection(
            work_with_video_stream.camera_3,
            work_with_video_stream.settings_camera_3
        )

        if work_with_video_stream.cv2.waitKey(1) == ord("q"):
            break

    work_with_video_stream.camera_1.release()
    work_with_video_stream.camera_2.release()
    work_with_video_stream.camera_3.release()
    work_with_video_stream.cv2.destroyAllWindows()
