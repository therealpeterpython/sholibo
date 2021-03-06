"""
The python bot.
It gets the commands from the chats and processes them. As data structure is uses the
ShoppingList class. To get the images it imports google_images_download. If you
encounter any problems please visit my fork
https://github.com/therealpeterpython/google-images-download.

therealpeterpython - 47575127+therealpeterpython@users.noreply.github.com
2019
"""

import telegram
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler
import logging
from google_images_download import google_images_download

from sholis import ShoppingList
import pickle
import os


config = {"path_lists": "./shopping_lists", "path_images":"./images", "path_token":"./token"}


# Download an image
def download_images(query):
    print("download_images")
    arguments = {"keywords": query,
                 "limit":1,
                 "thumbnail_only": True,
                 "output_directory":config["path_images"]
                 }
    response = google_images_download.googleimagesdownload()
    try:
        path = response.download(arguments)[0][query][0]
        return path
    except FileNotFoundError:
        pass


# Load or create a shopping list
def load(bot, chat_id):
    print("load chat_id: {}".format(chat_id))
    load_path = os.path.join(config["path_lists"], str(chat_id))
    if not os.path.isfile(load_path):   # create or load?
        slist = ShoppingList()
        save(chat_id, slist)
        msg = "I've created a new shopping list for you!"
        bot.send_message(chat_id=chat_id, text=msg)
    else:
        with open(load_path, "rb") as fp:
            slist = pickle.load(fp)
    return slist


# Save a shopping list
def save(chat_id, slist):
    print("save chat_id: {}".format(chat_id))
    os.makedirs(config["path_lists"], exist_ok=True)
    save_path = os.path.join(config["path_lists"], str(chat_id))
    with open(save_path, "wb") as fp:
        pickle.dump(slist, fp)


# Start the bot
def start(bot, update):
    print("start chat_id: {}".format(update.message.chat_id))
    help(bot, update)


# Add on or more comma or newline seperated items
def add_item(bot, update):
    print("add_item chat_id: {}".format(update.message.chat_id))
    chat_id = update.message.chat_id
    text = update.message.text
    try:
        items = text[text.index(" ")+1:]
    except ValueError:
        msg = "There was no item to add!"
        bot.send_message(chat_id=chat_id, text=msg)
        return
    items = [item.strip() for item in items.replace("\n", ",").split(",") if item.strip()]  # convert newline to comma and split
    if not items:
        msg = "There was no item to add!"
        bot.send_message(chat_id=chat_id, text=msg)
        return
    slist = load(bot, chat_id)
    slist.add_items(items)
    save(chat_id, slist)

    msg = "I've added the items for you!"
    bot.send_message(chat_id=chat_id, text=msg)


# Remove one or more items
def remove_items(bot, update, args):
    print("remove_items chat_id: {}".format(update.message.chat_id))
    chat_id = update.message.chat_id
    slist = load(bot, chat_id)
    try:
        positions = [int(index) for l in args for index in l.split(",") if index]  # split at commas and cast to int
        print(positions)
    except ValueError:
        msg = "Please use the item ids!"
        bot.send_message(chat_id=chat_id, text=msg)
        return
    slist.remove_items(positions)
    save(chat_id, slist)

    if not len(args):
        msg = "Nothing to delete!"
    else:
        msg = "I've removed that for you!"
    bot.send_message(chat_id=chat_id, text=msg)


# Remove all items
def remove_all(bot, update, args):
    print("remove_all chat_id: {}".format(update.message.chat_id))
    chat_id = update.message.chat_id
    if len(args) == 1 and args[0] == "clear":
        slist = load(bot, chat_id)
        slist.remove_all()
        save(chat_id, slist)
        msg = "I've cleared the list for you!"
        bot.send_message(chat_id=chat_id, text=msg)
    else:
        msg = "If you want to clear the entire list, enter the command and the word 'clear'!"
        bot.send_message(chat_id=chat_id, text=msg)


# Show the list
def view_list(bot, update):
    print("view_list chat_id: {}".format(update.message.chat_id))
    chat_id = update.message.chat_id
    slist = load(bot, chat_id)
    if not slist.empty():
        bot.send_message(chat_id=chat_id, text=slist.pprint_basic(), disable_web_page_preview=True)
    else:
        bot.send_message(chat_id=chat_id, text="There are no elements in your list!")


# Show the list with timestamps
def view_times(bot, update):
    print("view_times chat_id: {}".format(update.message.chat_id))
    chat_id = update.message.chat_id
    slist = load(bot, chat_id)
    if not slist.empty():
        bot.send_message(chat_id=chat_id, text=slist.pprint_full(), disable_web_page_preview=True)
    else:
        bot.send_message(chat_id=chat_id, text="There are no elements in your list!")


# Download an image
def image(bot, update, args):
    print("image chat_id: {}".format(update.message.chat_id))
    chat_id = update.message.chat_id
    items = load(bot, chat_id).get_items()
    for arg in args:
        try:
            arg = items[int(arg)]
        except ValueError:
            pass

        try:
            path = download_images(arg)
            if path:
                bot.send_message(chat_id=chat_id, text=arg, disable_web_page_preview=True)
                bot.send_photo(chat_id=chat_id, photo=open(path, 'rb'))
            else:
                bot.send_message(chat_id=chat_id, text="Cant find an image for '{}' you  :(".format(arg))
        except UnicodeDecodeError:
                bot.send_message(chat_id=chat_id, text="Umlauts for images are not supported yet!")
                raise


def all_images(bot, update):
    print("all_images chat_id: {}".format(update.message.chat_id))
    chat_id = update.message.chat_id
    items = load(bot, chat_id).get_items()
    image(bot, update, list(range(len(items))))


# Writes the help
def help(bot, update):
    print("help chat_id: {}".format(update.message.chat_id))
    help_msg = 'I am your shopping list bot: Sholibo!\n'
    help_msg += 'There are six commands to control me:\n'

    help_msg += '(1) With /add <name> you can add multiple comma or newline seperated items to your list,\n'
    help_msg += '(2) With /list you get an enumeration of your items,\n'
    help_msg += '(3) With /remove <number> you can remove items of your list,\n'
    help_msg += '(4) With /clear clear you delete the full list (be carefull),\n'
    help_msg += '(5) With /whatis <number> you get an image of the product,\n'
    help_msg += '(6) With /help you get this help again.\n\n'

    help_msg += 'Have fun shopping!'
    bot.send_message(chat_id=update.message.chat_id, text=help_msg)


# Main, register all the handels and start the polling
def main():
    # Logging the warnings and errors
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # Get the bot token
    with open(config["path_token"], "r") as fp:
        token = fp.read()

    # Get the updater, dispatcher and bot
    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    # Add handler
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('add', add_item))
    dispatcher.add_handler(CommandHandler('list', view_list))
    dispatcher.add_handler(CommandHandler('times', view_times))
    dispatcher.add_handler(CommandHandler('remove', remove_items, pass_args=True))
    dispatcher.add_handler(CommandHandler('clear', remove_all, pass_args=True))
    dispatcher.add_handler(CommandHandler('whatis', image, pass_args=True))
    dispatcher.add_handler(CommandHandler('whatiseverything', all_images))
    dispatcher.add_handler(CommandHandler('help', help))

    print("I am ready!  :)")

    # Get the updates
    updater.start_polling()
    updater.idle()

    print("Bye bye")


if __name__ == "__main__": main()
