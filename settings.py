# Адресс камеры
camera_ip = "x.x.x.x"
# Каналы камер (при необходмиости добавить или убрать лишнии строки)
channel_1 = "channel=1"
channel_2 = "channel=2"
channel_3 = "channel=3"

# Логин и пароль для камеры
login = "xxxxx"
password = "xxxxx" 

# Полные пути с настройками (при необходмиости добавить или убрать лишнии строки)
full_address_cam_1 = f"rtsp://{login}:{password}@{camera_ip}/user={login}_password={password}_{channel_1}_stream=1"
full_address_cam_2 = f"rtsp://{login}:{password}@{camera_ip}/user={login}_password={password}_{channel_2}_stream=1"
full_address_cam_3 = f"rtsp://{login}:{password}@{camera_ip}/user={login}_password={password}_{channel_3}_stream=1"
