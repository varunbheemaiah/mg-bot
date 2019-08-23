from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
import datetime

from app.logger import msg_logger, debug_logger
from app.todo import todo_handler
from app.animals import animal_handler
from app.fun import fun_handler
from app.poll import poll_extras_handler
from app.monopoly import mono_handler
from app.help import help_handler

animal_list = ["dog","bark","bork","cat","meow","pussy","panda","redpanda",
                "pika","pikachu","fox"]

fun_list = ["google","joke", "roast", "mock", "meme", "quote", "xkcd", "avatar", 
                "geek", "geekjoke", "dice", "coin", "flip", "choose","select",
                "unsplash", "wall", "wallpaper","die", "kill", "wink", "asktrump",
                "dadjoke", "belikebill", "yesno", "advice", "yomama"]

monopoly_list = ["balance", "beg", "daily", "search", "buy", "sell", "use", "steal", "shop", "market", "store", 
                "purchase", "inventory", "deposit", "withdraw",
                "lottery", "gamble", "share", "send", "rich", "loan", "bankrob"]

def start(bot, update):
    update.message.reply_text('Hi!')


def error(bot, update, msg_list):
    debug_logger.debug(str(update.message.chat_id) + " - " + update.message.from_user.username + " || " + str(msg_list))


def msg_parser(bot, update):
    msg = update.message.text.lower()
    msg_list = msg.split(" ")
    if msg_list[0] in ["mg","pls", "kini"]:

        if len(msg_list) == 1:
            update.message.reply_text("You didn't write any command. \nTry `pls help`")

        if msg_list[1] in animal_list:
            animal_handler(bot, update, msg_list)

        elif msg_list[1] in monopoly_list:
            mono_handler(bot,update,msg_list)

        elif msg_list[1] in fun_list:
            fun_handler(bot,update, msg_list)

        elif msg_list[1] in ["do","todo","tasks"]:
            todo_handler(bot, update, msg_list[1:])

        elif msg_list[1] in ["now", "time"]:
            update.message.reply_text(str(datetime.datetime.utcnow()))

        elif msg_list[1] in ["vote","poll"]:
            poll_extras_handler(bot, update, msg_list)

        elif msg_list[1] == "help":
            help_handler(bot,update,msg_list)
        else:
            debug_logger.debug(str(msg_list))

        msg_logger.info(str(update.message.chat_id) + "  | " + update.message.from_user.username + " : " + str(msg_list))

    elif msg_list[0] in ["hello","hi", "hey", "sup", "hii"]:
        update.message.reply_text("Hello there!")
        