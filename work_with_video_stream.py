import cv2
import os
from time import ctime
import numpy as np

from personal_data import camera_ip, login, password

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
    При обнаружении объекта рисует рамку вокруг объекта
    и вызывает функцию для сохранения изображения.
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

            save_detectid_objects(frame)

    return frame


def save_detectid_objects(frame):
    """
    Принимает изображение и сохраняет его в указаный каталог, в подкаталог
    с названием - текущая дата, присваивая изображению имя - текущее время.
    """
    root_directory_name = "detectid objects"  # Каталог для сохранения.
    subdirectory_name = f"{' '.join(ctime().split()[1:3])} {ctime().split()[-1]}"
    file_name = f"{ctime().split()[3]}.jpg"

    if not os.path.isdir(root_directory_name):
        os.mkdir(root_directory_name)
    if not os.path.isdir(f"{root_directory_name}/{subdirectory_name}"):
        os.mkdir(f"{root_directory_name}/{subdirectory_name}")

    cv2.imwrite(f"{root_directory_name}/{subdirectory_name}/{file_name}", frame)


def camera_1_reload():
    global camera_1
    camera_1.release()
    camera_1 = cv2.VideoCapture(settings_camera_1["full_address"])


def camera_2_reload():
    global camera_2
    camera_2.release()
    camera_2 = cv2.VideoCapture(settings_camera_2["full_address"])


def camera_3_reload():
    global camera_3
    camera_3.release()
    camera_3 = cv2.VideoCapture(settings_camera_3["full_address"])


def start_video_object_detection(camera, values_cam):
    """
    Захватывает из видеопотока кадр, вырезает из него нужную для поска объектов область
    и передаёт в другую функцию для поиска.
    Две последнии строчки для вывода видео на экран для отладки.
    """

    ret, frame = camera.read()
    if ret:
        frame = frame
        frame = frame[
            values_cam["height_start"]:values_cam["height_stop"],
            values_cam["width_start"]:values_cam["width_stop"]
        ]
    else:
        print("Ошибка чтения...", ctime())
        values_cam["reload"]()
        return

    frame = detect_object_on_frame(frame)

    # Вывод видео на экран для отладки.
    frame = cv2.resize(frame, (1920 // 2, 1080 // 2))
    cv2.imshow(values_cam["name"], frame)


settings_camera_1 = {
    "name": "cam_1",
    "full_address": f"rtsp://{login}:{password}@{camera_ip}/user={login}_password={password}_channel=1_stream=0",
    # Начальные и конечные значения высоты и ширины облясти поиска движения:
    "height_start": 400,  # Верхняя граница высоты кадра
    "height_stop": 1000,  # Нижняя граница высоты кадра
    "width_start": 600,  # Левая граница ширины кадра
    "width_stop": 1550,  # Правая граница ширины кадра
    "reload": camera_1_reload
}
settings_camera_2 = {
    "name": "cam_2",
    "full_address": f"rtsp://{login}:{password}@{camera_ip}/user={login}_password={password}_channel=2_stream=0",
    # Начальные и конечные значения высоты и ширины облясти поиска движения:
    "height_start": 100,  # Верхняя граница высоты кадра
    "height_stop": 1080,  # Нижняя граница высоты кадра
    "width_start": 330,  # Левая граница ширины кадра
    "width_stop": 1920,  # Правая граница ширины кадра
    "reload": camera_2_reload
}
settings_camera_3 = {
    "name": "cam_3",
    "full_address": f"rtsp://{login}:{password}@{camera_ip}/user={login}_password={password}_channel=3_stream=0",
    # Начальные и конечные значения высоты и ширины облясти поиска движения:
    "height_start": 0,  # Верхняя граница высоты кадра
    "height_stop": 1080,  # Нижняя граница высоты кадра
    "width_start": 0,  # Левая граница ширины кадра
    "width_stop": 1920,  # Правая граница ширины кадра
    "reload": camera_3_reload
}

camera_1 = cv2.VideoCapture(settings_camera_1["full_address"])
camera_2 = cv2.VideoCapture(settings_camera_2["full_address"])
camera_3 = cv2.VideoCapture(settings_camera_3["full_address"])
