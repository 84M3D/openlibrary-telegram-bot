import telebot
from telebot.types import InlineKeyboardButton,InlineKeyboardMarkup
from dotenv import load_dotenv
import os
from library_api import LibraryAPI
from csv_exporter import CSVExporter
import re

year_patterns = [
    r'^\s*\d{4}\s*-\s*\d{4}\s*$',  
    r'^\s*\d{4}\s*-\s*\*\s*$',  
    r'^\s*\*\s*-\s*\d{4}\s*$',  
    ]

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
    
    for pattern in year_patterns:
        if re.match(pattern, user_input):
            break
    else:
        return None, None, False 
    
    if '-' in user_input:
        parts = user_input.split('-')
        start = parts[0].strip()
        end = parts[1].strip()
        
        start_year = int(start) if start and start != '*' else None
        end_year = int(end) if end and end != '*' else None
        
        if start_year and end_year and start_year > end_year:
            return None, None, False
        
        if start_year and (start_year < 1000 or start_year > 2100):
            return None, None, False 
                
        if end_year and (end_year < 1000 or end_year > 2100):
            return None, None, False
            
        return start_year, end_year, True

    
@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    user_state[chat_id] = {}
    bot.send_message(chat_id, "درود! برای جستجوی کتاب لطفاً ابتدا keyword مورد نظر را وارد کنید:")

@bot.message_handler(commands=["cancel"])
def cancel_command(message):
    chat_id = message.chat.id
    if chat_id in user_state:
        bot.send_message(chat_id, "❌ عملیات کنسل شد.")
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, "برای شروع مجدد /start را ارسال کنید.")

@bot.message_handler(func=lambda m: m.chat.id in user_state and "keyword" not in user_state[m.chat.id])
def handle_keyword(message):
    chat_id = message.chat.id
    user_state[chat_id]["keyword"] = message.text.strip()
    bot.send_message(chat_id, "می‌خواهید فیلتر بر اساس سال اعمال شود؟", reply_markup=ask_year_filtering())

@bot.callback_query_handler(func= lambda call: call.data == "no_yearFiltering")
def no_yearFiltering(call):
    chat_id = call.message.chat.id
    user_state[chat_id]["year_from"] = None
    user_state[chat_id]["year_to"] = None
    bot.send_message(chat_id, "نوع مرتب‌سازی را انتخاب کنید:", reply_markup=build_sort_markup())

@bot.callback_query_handler(func= lambda call: call.data == "yes_yearFiltering")
def yes_yearFiltering(call):
    bot.send_message(call.message.chat.id,"لطفا یکی از گزینه های زیر را انتخاب کنید:",reply_markup=build_year_markup())

@bot.callback_query_handler(func=lambda call: call.data.startswith("year_"))
def handle_year_selection(call):
    chat_id = call.message.chat.id
    
    if call.data == "year_pre2000":
        user_state[chat_id]["year_from"] = None
        user_state[chat_id]["year_to"] = 2000
    elif call.data == "year_post2000":
        user_state[chat_id]["year_from"] = 2000
        user_state[chat_id]["year_to"] = None
    elif call.data == "year_post2020":
        user_state[chat_id]["year_from"] = 2020
        user_state[chat_id]["year_to"] = None
    elif call.data == "year_custom":

        bot.send_message(call.message.chat.id,
        "بازه سال را وارد کنید.\n\n"
        "فرمت:\n"
        "- شروع-پایان (مثال: 2000-2020)\n"
        "- فقط شروع (مثال: 2000-*) → از سال 2000 به بعد\n"
        "- فقط پایان (مثال: *-1950) → تا سال 1950\n"
        )
        bot.register_next_step_handler(call,callback=handle_custom_year_input)
    
    bot.send_message(chat_id, "نوع مرتب‌سازی را انتخاب کنید:", 
                     reply_markup=build_sort_markup())
    

def handle_custom_year_input(message):
    chat_id = message.chat.id
    
    # تحلیل ورودی
    year_from, year_to, is_valid = parse_year_range(message.text)
    
    if not is_valid:
        error_msg = bot.send_message(
            chat_id,
            "❌ **فرمت وارد شده نامعتبر است!**\n\n"
            "لطفاً یکی از فرمت‌های زیر را وارد کنید:\n"
            "• `2000-2020`\n"
            "• `2000-*`\n"
            "• `*-2020`\n\n"
        )
        bot.register_next_step_handler(error_msg, handle_custom_year_input)
        return
    
    user_state[chat_id]["year_from"] = year_from
    user_state[chat_id]["year_to"] = year_to
    
    bot.send_message(chat_id, "✅ **سال با موفقیت تنظیم شد**")
    bot.send_message(chat_id, "نوع مرتب‌سازی را انتخاب کنید:", reply_markup=build_sort_markup())

@bot.callback_query_handler(func= lambda call: call.data.startswith("sort_"))
def handle_sort_selection(call):
    chat_id = call.message.chat.id
    sort_type = call.data.replace("sort_", "")

    if sort_type == "relevance":
        user_state[chat_id]["sort"] = None
    else:
        user_state[chat_id]["sort"] = sort_type

    bot.send_message(chat_id, "تعداد کتاب را انتخاب کنید:", reply_markup=build_limit_markup())

@bot.callback_query_handler(func= lambda call : call.data.startswith("limit_"))
def handle_limit_selection(call):
    chat_id = call.message.chat.id
    limit = int(call.data.replace("limit_", ""))
    user_state[chat_id]["limit"] = limit
    bot.send_message(chat_id, "در حال جمع‌آوری داده‌ها…")
    final_step(chat_id)


def final_step(chat_id):

    api = LibraryAPI(
            keyword=user_state.get(chat_id).get("keyword"),
            year_from=user_state.get(chat_id).get("year_from"),
            year_to=user_state.get(chat_id).get("year_to"),
            limit=user_state.get(chat_id).get("limit"),
            sort=user_state.get(chat_id).get("sort")
        )
    
    books = api.fetch_books()

    if not books:  
        bot.send_message(chat_id, "هیچ کتابی با معیارهای شما یافت نشد.")
        user_state.pop(chat_id, None)
        return
    
    safe_keyword = re.sub(r'[^\w\-_\. ]', '_', user_state[chat_id]['keyword'])
    
    filename = f"{safe_keyword}.csv"
    CSVExporter(filename,books)

    with open(filename, "rb") as f:
            bot.send_document(chat_id, f)

    user_state.pop(chat_id, None)

    os.remove(filename)


bot.infinity_polling()