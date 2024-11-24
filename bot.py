import json
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

# Замените 'YOUR_TOKEN' на токен вашего бота
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
FILEPATH = os.getenv('FILEPATH')


def add_user(user_data: dict) -> None:
    with open(FILEPATH, "r") as jsonFile:
        data = json.load(jsonFile)

    data[str(user_data["user_id"])] = user_data

    with open(FILEPATH, "w") as jsonFile:
        json.dump(data, jsonFile)


def save_user(update: Update) -> None:
    user = update.message.from_user
    user_data = {
        'user_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'date_joined': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    add_user(user_data)

def save_photo(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = user.id

    photo_file = update.message.photo[-1].get_file()
    photo_path = f'photos/{user_id}/{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.jpg'
    os.makedirs(os.path.dirname(photo_path), exist_ok=True)
    photo_file.download(photo_path)

    update.message.reply_text('Ваше фото успешно сохранено.')


def start(update: Update, context: CallbackContext) -> None:
    save_user(update)
    keyboard = [
        [KeyboardButton("Выбрать товар", callback_data='choose_product')],
        # Добавьте другие товары, если необходимо
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    update.message.reply_text(
        "Приветствую! Стандартная гарантия на наши изделия составляет 1 месяц. "
        "Чтобы увеличить гарантию, выберите Ваш товар и следуйте инструкции.\n\n"
        "Нажмите на кнопку для выбора товара.", reply_markup=reply_markup
    )


def choose_product(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Фонарь аккумуляторный PathlightPRO", callback_data='product_1')],
        # Добавьте другие товары, если необходимо
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Пожалуйста, выберите ваш товар:', reply_markup=reply_markup)


def warranty_options(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Гарантия 1 год", callback_data='warranty_1')],
        [InlineKeyboardButton("Увеличенная гарантия 2 года", callback_data='warranty_2')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Выберите вариант гарантии для вашего товара:",
        reply_markup=reply_markup
    )


def handle_warranty_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    if query.data == 'warranty_1':
        query.edit_message_text(
            text="Для получения гарантии 1 год, пожалуйста, сбросьте фото покупки из личного кабинета, чтобы было видно дату покупки."
        )
    elif query.data == 'warranty_2':
        query.edit_message_text(
            text="Для получения увеличенной гарантии 2 года, пожалуйста, сбросьте фото покупки и напишите положительный отзыв. "
                 "Затем пришлите скриншот отзыва. Инструкция:\n\n"
                 "1. Перейдите в профиль на WB.\n"
                 "2. Вкладка 'Отзывы и вопросы'.\n"
                 "3. Выберите 'Отзывы' и сделайте скриншот."
        )


def warranty_questions(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Если у вас есть вопросы по гарантии, пожалуйста, напишите их здесь, и мы ответим вам в ближайшее время."
    )



def handle_messages(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Ваше сообщение получено. Мы обработаем его в ближайшее время."
    )


def main() -> None:
    print('started')

    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("choose_product", choose_product))
    dispatcher.add_handler(CommandHandler("warranty_questions", warranty_questions))
    dispatcher.add_handler(CallbackQueryHandler(warranty_options, pattern='^product_'))
    dispatcher.add_handler(CallbackQueryHandler(handle_warranty_selection, pattern='^warranty_'))
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.regex('Выбрать товар'), choose_product))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_messages))
    dispatcher.add_handler(MessageHandler(Filters.photo, save_photo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
