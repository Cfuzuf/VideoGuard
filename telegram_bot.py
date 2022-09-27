from time import time, sleep
import telebot

from settings import TOKEN, ADMIN_CHAT_ID, ALLOWED_USERS_ID
import work_with_video_stream


bot = telebot.TeleBot(token=TOKEN)
run_video_protection = False

# Создание кнопок управления.
button_start = telebot.types.KeyboardButton("Включить защиту.")
button_stop = telebot.types.KeyboardButton("Выключить защиту.")
button_status = telebot.types.KeyboardButton("Статус.")
button_send_mi_photo = telebot.types.KeyboardButton("Доложить обстановку.")

reply_keyboard_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
reply_keyboard_markup.add(button_start, button_stop, button_status, button_send_mi_photo)


def get_status(message):
    if run_video_protection:
        bot.send_message(chat_id=message.from_user.id,
                         text="Объект под надёжной защитой!")
    else:
        bot.send_message(chat_id=message.from_user.id,
                         text="Объект остался без защиты...")


def start_video_protection(message):
    """
    Меняет флаг состояния защиты и запускает функцию защиты.
    """
    global run_video_protection
    if not run_video_protection:
        run_video_protection = True
        bot.send_message(chat_id=message.from_user.id,
                         text="Объект под надёжной защитой!",
                         reply_markup=reply_keyboard_markup)
        protection_activation()


def stop_video_protection(message):
    """
    Меняет флаг состояния защиты для остановки выполнения функции защиты.
    """
    global run_video_protection, reply_keyboard_markup
    if run_video_protection:
        run_video_protection = False
        bot.send_message(chat_id=message.from_user.id,
                         text="Объект остался без защиты...",
                         reply_markup=reply_keyboard_markup)


def protection_activation():
    """
    В бесконечном цикле вызывает функцию запуска поиска объектов поочерёдно для каждой камеры.
    Меняет кнопки согласно обстановке.
    """

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

        if time() - start_time < 1:
            sleep(1 - (time() - start_time))


commands_handlers = {
    "Включить защиту.": start_video_protection,
    "Выключить защиту.": stop_video_protection,
    "Статус.": get_status,
    "Доложить обстановку.": work_with_video_stream.get_all_cams_skreenshots
}


@bot.message_handler(commands=["start"])
def show_buttons(message):
    bot.send_message(chat_id=message.from_user.id,
                     text="Что прикажешь?",
                     reply_markup=reply_keyboard_markup)


@bot.message_handler(content_types=["text"])
def message_handler(message):
    if message.from_user.id == ADMIN_CHAT_ID or message.from_user.id in ALLOWED_USERS_ID:
        commands_handlers[message.text](message)
    else:
        bot.send_message(chat_id=message.from_user.id,
                         text="Я тебя не знаю и слушаться не буду!!!")


def start_guard_bot():
    bot.send_message(chat_id=ADMIN_CHAT_ID,
                     text="Бот запущен...",
                     reply_markup=reply_keyboard_markup)

    bot.infinity_polling()
