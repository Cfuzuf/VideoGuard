import cv2
import os
import numpy as np
import requests
from datetime import datetime
from time import time, sleep

from settings import CAMERA_IP, CAMERA_LOGIN, CAMERA_PASSWORD, TOKEN, CHANNEL_CHAT_ID


net = cv2.dnn.readNetFromDarknet("Resources/yolov4-tiny.cfg", "Resources/yolov4-tiny.weights")
layer_names = net.getLayerNames()
out_layers_indexes = net.getUnconnectedOutLayers()
out_layers = [layer_names[index - 1] for index in out_layers_indexes]

with open("Resources/coco.names.txt") as file:
    classes = file.read().split("\n")

classes_to_look_for = ["person"]


def detect_object_on_frame(frame):
    """
    Функция для поиска заданного объекта на изображении.
    Принимает на вход один кадр из видео.
    При обнаружении объекта рисует рамку вокруг объекта,
    вызывает функцию для сохранения изображения,
    вызывает функцию для отправки изображения в телеграм.
    Возвращает обработанное изображение.
    """
    height, width, _ = frame.shape
    blob = cv2.dnn.blobFromImage(frame, 1 / 255, (608, 608), (0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    outs = net.forward(out_layers)
    class_indexes, class_scores, boxes = ([] for i in range(3))

    for out in outs:
        for obj in out:
            scores = obj[5:]
            class_index = np.argmax(scores)
            class_score = scores[class_index]
            if class_score > 0.8:  # Вероятность совпадения. (Максимум 1.0)
                center_x = int(obj[0] * width)
                center_y = int(obj[1] * height)
                obj_width = int(obj[2] * width)
                obj_height = int(obj[3] * height)
                box = [center_x - obj_width // 2, center_y - obj_height // 2, obj_width, obj_height]
                boxes.append(box)
                class_indexes.append(class_index)
                class_scores.append(float(class_score))

    chosen_boxes = cv2.dnn.NMSBoxes(boxes, class_scores, 0.0, 0.4)
    for box_index in chosen_boxes:
        box = boxes[box_index]
        class_index = class_indexes[box_index]

        if classes[class_index] in classes_to_look_for:
            x, y, w, h = box
            frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)

            file_path = save_detected_objects(frame)
            send_detected_objects_to_telegram(file_path)

    return frame


def save_detected_objects(frame):
    """
    Принимает изображение и сохраняет его в указанный каталог, в подкаталог
    с названием - текущая дата, присваивая изображению имя - текущее время.
    Возвращает полный путь к сохранённому файлу.
    """
    # Создаём путь и имя файла для сохранения.
    directory_name = f"detected objects/{datetime.now().date()}"
    file_name = f"{datetime.now().time()}.jpg"
    full_path_and_name = f"{directory_name}/{file_name}"

    if not os.path.isdir(f"{directory_name}"):
        os.makedirs(f"{directory_name}")

    cv2.imwrite(full_path_and_name, frame)

    return full_path_and_name


def send_detected_objects_to_telegram(file_path, chat_id=CHANNEL_CHAT_ID):
    """
    Делает https запрос для отправки файла в телеграм.
    """
    file = {'photo': open(file_path, 'rb')}
    requests.post(
        url=f"https://api.telegram.org/bot{TOKEN}/sendPhoto?chat_id={chat_id}",
        files=file
    )


def camera_1_reload():
    """
    При обрыве соединения с камерой, или ошибки чтения видео кадра
    пересоздаёт соединение с камерой №1.
    """
    global camera_1
    camera_1.release()
    camera_1 = cv2.VideoCapture(camera_settings["camera_1"]["full_address"])


def camera_2_reload():
    """
    При обрыве соединения с камерой, или ошибки чтения видео кадра
    пересоздаёт соединение с камерой №2.
    """
    global camera_2
    camera_2.release()
    camera_2 = cv2.VideoCapture(camera_settings["camera_2"]["full_address"])


def camera_3_reload():
    """
    При обрыве соединения с камерой, или ошибки чтения видео кадра
    пересоздаёт соединение с камерой №3.
    """
    global camera_3
    camera_3.release()
    camera_3 = cv2.VideoCapture(camera_settings["camera_3"]["full_address"])


def start_video_object_detection(camera, cam_settings, show=False):
    """
    Захватывает из видео-потока кадр, вырезает из него нужную для поиска объектов область
    и передаёт в другую функцию для поиска.

    Две последние строчки для вывода видео на экран - для отладки.
    """

    ret, frame = camera.read()
    if ret:
        frame = frame[
            cam_settings["height_start"]:cam_settings["height_stop"],
            cam_settings["width_start"]:cam_settings["width_stop"]
        ]
    else:
        cam_settings["reload"]()
        return

    frame = detect_object_on_frame(frame)

    # Вывод видео на экран для отладки камер.
    if show:
        frame = cv2.resize(frame, (1920 // 2, 1080 // 2))
        cv2.imshow(cam_settings["name"], frame)


def get_all_cams_skreenshots(message):
    """
    Делает полноразмерные снимки со всех камер и отправляет их в телеграм запросившему пользователю.
    """
    ret, frame = camera_1.read()
    if ret:
        file_path = save_detected_objects(frame)
        send_detected_objects_to_telegram(file_path, chat_id=message.from_user.id)

    ret, frame = camera_2.read()
    if ret:
        file_path = save_detected_objects(frame)
        send_detected_objects_to_telegram(file_path, chat_id=message.from_user.id)

    ret, frame = camera_3.read()
    if ret:
        file_path = save_detected_objects(frame)
        send_detected_objects_to_telegram(file_path, chat_id=message.from_user.id)


camera_settings = {
    "camera_1": {
        "name": "cam_1",
        "full_address": f"rtsp://{CAMERA_LOGIN}:{CAMERA_PASSWORD}@{CAMERA_IP}/user={CAMERA_LOGIN}_password={CAMERA_PASSWORD}_channel=1_stream=0",
        # Начальные и конечные значения высоты и ширины области поиска движения:
        "height_start": 400,  # Верхняя граница высоты кадра
        "height_stop": 1000,  # Нижняя граница высоты кадра
        "width_start": 600,  # Левая граница ширины кадра
        "width_stop": 1550,  # Правая граница ширины кадра
        "reload": camera_1_reload
    },
    "camera_2": {
        "name": "cam_2",
        "full_address": f"rtsp://{CAMERA_LOGIN}:{CAMERA_PASSWORD}@{CAMERA_IP}/user={CAMERA_LOGIN}_password={CAMERA_PASSWORD}_channel=2_stream=0",
        # Начальные и конечные значения высоты и ширины области поиска движения:
        "height_start": 100,  # Верхняя граница высоты кадра
        "height_stop": 1080,  # Нижняя граница высоты кадра
        "width_start": 330,  # Левая граница ширины кадра
        "width_stop": 1920,  # Правая граница ширины кадра
        "reload": camera_2_reload
    },
    "camera_3": {
        "name": "cam_3",
        "full_address": f"rtsp://{CAMERA_LOGIN}:{CAMERA_PASSWORD}@{CAMERA_IP}/user={CAMERA_LOGIN}_password={CAMERA_PASSWORD}_channel=3_stream=0",
        # Начальные и конечные значения высоты и ширины области поиска движения:
        "height_start": 0,  # Верхняя граница высоты кадра
        "height_stop": 1080,  # Нижняя граница высоты кадра
        "width_start": 0,  # Левая граница ширины кадра
        "width_stop": 1920,  # Правая граница ширины кадра
        "reload": camera_3_reload
    }
}

camera_1 = cv2.VideoCapture(camera_settings["camera_1"]["full_address"])
camera_2 = cv2.VideoCapture(camera_settings["camera_2"]["full_address"])
camera_3 = cv2.VideoCapture(camera_settings["camera_3"]["full_address"])

if __name__ == "__main__":
    while True:
        start_time = time()

        start_video_object_detection(camera_1, camera_settings["camera_1"], show=True)
        start_video_object_detection(camera_2, camera_settings["camera_2"], show=True)
        start_video_object_detection(camera_3, camera_settings["camera_3"], show=True)

        if time() - start_time < 0.5:
            sleep(0.5 - (time() - start_time))

        if cv2.waitKey(1) == ord("q"):
            break

    cv2.destroyAllWindows()
