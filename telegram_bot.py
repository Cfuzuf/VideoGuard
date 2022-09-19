from time import time, sleep
import telebot

from personal_data import TOKEN, ALLOWED_USERS_ID
import work_with_video_stream


bot = telebot.TeleBot(token=TOKEN)
run_video_protection = False


@bot.message_handler(commands=["status"])
def get_status(message):
    if message.chat.id in ALLOWED_USERS_ID.values():
        if run_video_protection:
            bot.send_message(chat_id=message.chat.id,
                             text="Объект под надёжной защитой!")
        else:
            bot.send_message(chat_id=message.chat.id,
                             text="Объект остался без защиты...")
    else:
        bot.send_message(chat_id=message.chat.id,
                         text="Я тебя не знаю и слушаться не буду!!!")


@bot.message_handler(commands=["start"])
def start_video_protection(message):
    if message.chat.id in ALLOWED_USERS_ID.values():
        global run_video_protection
        if not run_video_protection:
            run_video_protection = True
            protection_activation(message)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text="Я тебя не знаю и слушаться не буду!!!")


@bot.message_handler(commands=["stop"])
def stop_video_protection(message):
    if message.chat.id in ALLOWED_USERS_ID.values():
        global run_video_protection
        if run_video_protection:
            run_video_protection = False
    else:
        bot.send_message(chat_id=message.chat.id,
                         text="Я тебя не знаю и слушаться не буду!!!")


def protection_activation(message):
    """
    В бесконечном цикле вызывает функцию запуска поиска объектов поочерёдно для каждой камеры.
    """

    bot.send_message(chat_id=message.chat.id,
                     text="Объект под надёжной защитой!")

    while run_video_protection:
        start_time = time()

        work_with_video_stream.start_video_object_detection(
            work_with_video_stream.camera_1,
            work_with_video_stream.camera_settings["camera_1"])
        work_with_video_stream.start_video_object_detection(
            work_with_video_stream.camera_2,
            work_with_video_stream.camera_settings["camera_2"])
        work_with_video_stream.start_video_object_detection(
            work_with_video_stream.camera_3,
            work_with_video_stream.camera_settings["camera_3"])

        if time() - start_time < 0.5:
            sleep(0.5 - (time() - start_time))

    bot.send_message(chat_id=message.chat.id,
                     text="Объект остался без защиты...")


def start_guard_bot():
    bot.send_message(chat_id=ALLOWED_USERS_ID["admin"],
                     text="Бот запущен...")

    bot.polling(non_stop=True)
