import telebot
from telebot.types import InlineKeyboardButton,InlineKeyboardMarkup
from dotenv import load_dotenv
import os
from library_api import LibraryAPI
from csv_exporter import CSVExporter

load_dotenv()

token = os.getenv('API_KEY')

bot = telebot.TeleBot(token)

user_state = {}

sort_options = ["relevance", "new", "old", "trending", "rating", "editions", "random"]

limit_options = [10, 20, 50]

def build_year_markup():
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = [
        InlineKeyboardButton("قبل از 2000", callback_data="year_pre2000"),
        InlineKeyboardButton("بعد از 2000", callback_data="year_post2000"),
        InlineKeyboardButton("بعد از 2020", callback_data="year_post2020"),
        InlineKeyboardButton("وارد کردن دستی", callback_data="year_custom")
    ]
    markup.add(*buttons)
    return markup

def ask_year_filtering():
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("خیر",callback_data="no_yearFiltering"),
        InlineKeyboardButton("بله",callback_data="yes_yearFiltering")
    ]
    markup.add(*buttons)
    return markup

def build_sort_markup(selected=None):
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []
    for option in sort_options:
        text = f"{option} {'✅' if option==selected else ''}"
        buttons.append(InlineKeyboardButton(text, callback_data=f"sort_{option}"))
    markup.add(*buttons)
    return markup

def build_limit_markup(selected=None):
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []
    for option in limit_options:
        text = f"{option} {'✅' if option==selected else ''}"
        buttons.append(InlineKeyboardButton(text, callback_data=f"limit_{option}"))
    markup.add(*buttons)
    return markup

def parse_year_range(user_input):
    user_input = user_input.strip()
    if not user_input:
        return None, None
    if "-" in user_input:
        start, end = user_input.split("-")
        start = start if start != "*" else None
        end = end if end != "*" else None
        return int(start) if start else None, int(end) if end else None
    else:
        return int(user_input), None
    
@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    user_state[chat_id] = {}
    bot.send_message(chat_id, "درود! برای جستجوی کتاب لطفاً ابتدا keyword مورد نظر را وارد کنید:")

@bot.message_handler(func=lambda m: m.chat.id in user_state and "keyword" not in user_state[m.chat.id])
def handle_keyword(message):
    chat_id = message.chat.id
    user_state[chat_id]["keyword"] = message.text.strip()
    bot.send_message(chat_id, "می‌خواهید فیلتر بر اساس سال اعمال شود؟", reply_markup=ask_year_filtering())

@bot.callback_query_handler(func= lambda call: call.text == "no_yearFiltering")
def no_yearFiltering(call):
    chat_id = call.chat.id
    user_state[chat_id]["year_from"] = None
    user_state[chat_id]["year_to"] = None

@bot.callback_query_handler(func= lambda call: call.text == "yes_yearFiltering")
def no_yearFiltering(call):
    bot.send_message(call.chat.id,"لطفا یکی از گزینه های زیر را انتخاب کنید:",reply_markup=build_year_markup())

@bot.callback_query_handler(func= lambda call: call.text == "year_pre2000")
def no_yearFiltering(call):
    chat_id = call.chat.id
    user_state[chat_id]["year_from"] = None
    user_state[chat_id]["year_to"] = 2000

@bot.callback_query_handler(func= lambda call: call.text == "year_post2000")
def no_yearFiltering(call):
    chat_id = call.chat.id
    user_state[chat_id]["year_from"] = 2000
    user_state[chat_id]["year_to"] = None

@bot.callback_query_handler(func= lambda call: call.text == "year_post2020")
def no_yearFiltering(call):
    chat_id = call.chat.id
    user_state[chat_id]["year_from"] = 2020
    user_state[chat_id]["year_to"] = None

@bot.callback_query_handler(func= lambda call: call.text == "year_custom")
def no_yearFiltering(call):
    bot.send_message(call.chat.id,
        "بازه سال را وارد کنید.\n\n"
        "فرمت:\n"
        "- شروع-پایان (مثال: 2000-2020)\n"
        "- فقط شروع (مثال: 2000-*) → از سال 2000 به بعد\n"
        "- فقط پایان (مثال: *-1950) → تا سال 1950\n"
    )
    bot.register_next_step_handler(call,callback=optional_year_formater)

def optional_year_formater(message):
    chat_id = message.chat.id
    user_state[chat_id]["year_from"], user_state[chat_id]["year_to"] = parse_year_range(message.text)
    bot.send_message(chat_id,"نوع مرتب‌سازی را انتخاب کنید:",reply_markup=build_sort_markup())

@bot.callback_query_handler(funck= lambda call : call.text == "sort_relevance")
def sort_relevance(call):
    chat_id = call.chat.id
    user_state[chat_id]["sort"] = None
    bot.send_message(chat_id,"تعداد کتاب را انتخاب کنید:", reply_markup=build_limit_markup())

@bot.callback_query_handler(funck= lambda call : call.text == "sort_new")
def sort_new(call):
    chat_id = call.chat.id
    user_state[chat_id]["sort"] = "new"
    bot.send_message(chat_id,"تعداد کتاب را انتخاب کنید:", reply_markup=build_limit_markup())

@bot.callback_query_handler(funck= lambda call : call.text == "sort_old")
def sort_relevance(call):
    chat_id = call.chat.id
    user_state[chat_id]["sort"] = "old"
    bot.send_message(chat_id,"تعداد کتاب را انتخاب کنید:", reply_markup=build_limit_markup())

@bot.callback_query_handler(funck= lambda call : call.text == "sort_trending")
def sort_relevance(call):
    chat_id = call.chat.id
    user_state[chat_id]["sort"] = "trending"
    bot.send_message(chat_id,"تعداد کتاب را انتخاب کنید:", reply_markup=build_limit_markup())

@bot.callback_query_handler(funck= lambda call : call.text == "sort_rating")
def sort_relevance(call):
    chat_id = call.chat.id
    user_state[chat_id]["sort"] = "rating"
    bot.send_message(chat_id,"تعداد کتاب را انتخاب کنید:", reply_markup=build_limit_markup())

@bot.callback_query_handler(funck= lambda call : call.text == "sort_editions")
def sort_relevance(call):
    chat_id = call.chat.id
    user_state[chat_id]["sort"] = "editions"
    bot.send_message(chat_id,"تعداد کتاب را انتخاب کنید:", reply_markup=build_limit_markup())

@bot.callback_query_handler(funck= lambda call : call.text == "sort_random")
def sort_relevance(call):
    chat_id = call.chat.id
    user_state[chat_id]["sort"] = "random"
    bot.send_message(chat_id,"تعداد کتاب را انتخاب کنید:", reply_markup=build_limit_markup())

@bot.callback_query_handler(func= lambda call : call.text == "limit_10")
def limit_ten(call):
    chat_id = call.chat.id
    user_state[chat_id]["limit"] = 10
    bot.send_message(chat_id, "در حال جمع‌آوری داده‌ها…")
    final_step(chat_id)


@bot.callback_query_handler(func= lambda call : call.text == "limit_20")
def limit_twenty(call):
    chat_id = call.chat.id
    user_state[chat_id]["limit"] = 20
    bot.send_message(chat_id, "در حال جمع‌آوری داده‌ها…")
    final_step(chat_id)


@bot.callback_query_handler(func= lambda call : call.text == "limit_50")
def limit_fifty(call):
    chat_id = call.chat.id
    user_state[chat_id]["limit"] = 50
    bot.send_message(chat_id, "در حال جمع‌آوری داده‌ها…")
    final_step(chat_id)


def final_step(chat_id):

    api = LibraryAPI(
            keyword=user_state.get(chat_id).get["keyword"],
            year_from=user_state.get(chat_id).get("year_from"),
            year_to=user_state.get(chat_id).get("year_to"),
            limit=user_state.get(chat_id).get("limit"),
            sort=user_state.get(chat_id).get("sort")
        )
    books = api.fetch_books()
    filename = f"{user_state[chat_id]['keyword']}.csv"
    CSVExporter(filename,books)

    with open(filename, "rb") as f:
            bot.send_document(chat_id, f)

    user_state.pop(chat_id, None)

    os.remove(filename)


bot.infinity_polling()