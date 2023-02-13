import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ForceReply, KeyboardButton
from telegram.ext import CommandHandler, CallbackContext, Updater, MessageHandler, Filters, CallbackQueryHandler, \
    ConversationHandler

import bot_settings

import homelyDB_API
from classes.Tool import Tool
from classes import User

# from classes.User import User

logging.basicConfig(
    format='[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

updater = Updater(token=bot_settings.TOKEN, use_context=True)
dispatcher = updater.dispatcher


# LANDING CODE
EXPECT_NAME, EXPECT_PHONE, EXPECT_NAME_BUTTON_CLICK, EXPECT_CATEGORY, \
EXPECT_CATEGORY_BUTTON_CLICK, EXPECT_IMG, EXPECT_IMG_BUTTON_CLICK, CALL_CATEGORY = range(8)


def start(update: Update, context: CallbackContext):
    print(update.to_json())
    chat_id = update.effective_chat.id
    logger.info(f"> Start chat #{chat_id}")
    context.bot.send_message(chat_id=chat_id, text="👋 Welcome! What would you like to do? You can /landtool or /borrowtool " )


def phone_number_handler(update: Update, context: CallbackContext):
    ''' This gets executed on button click '''
    update.message.reply_text("This is exciting! We're thrilled you are part of this sharing community!")
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f'First, please provide your phone number. Type in exactly 12 digits, no'
                                  f'spaces or other symbols. For example, 972541234567 ')
    return EXPECT_PHONE


def set_name_handler(update: Update, context: CallbackContext):
    phone_number = update.message.text
    update.message.reply_text(f"Number saved. We will use {phone_number} when a borrower wants to contact you. "
                              "they will send you a Telegram message.")

    update.message.reply_text('Now, tell us more about your item. What is it called? '
                              'For example: Phillips Screwdriver Drill')

    return EXPECT_NAME


def name_input_by_user(update: Update, context: CallbackContext):
    ''' The user's reply to the name prompt comes here  '''
    name = update.message.text
    context.user_data['name'] = name
    update.message.reply_text(f'Your tool is saved as {name[:100]}')
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Power Tools", callback_data='powertools')],
                                 [InlineKeyboardButton("Furniture",
                                                       callback_data='furniture')],
                                 [InlineKeyboardButton("Kitchen Appliances",
                                                       callback_data='appliances')],
                                 [InlineKeyboardButton("For kids",
                                                       callback_data='kids')],
                                 [InlineKeyboardButton("Electronics",
                                                       callback_data='electronics')],
                                 ])
    update.message.reply_text('Select the category of your item?', reply_markup=keyboard)

    return EXPECT_CATEGORY_BUTTON_CLICK


def category_button_click_handler(update: Update, context: CallbackContext):
    ''' This gets executed on button click '''
    category = update.callback_query.data
    context.user_data['category'] = category
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f'You item is saved under {category}')

    context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Now, upload an image of your item')
    return EXPECT_IMG

def img_input_by_user(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    file_id = update.message.photo[-1].file_id
    new_file = context.bot.get_file(file_id)
    new_file.download(f'image_{file_id[:5]}.jpg')
    print(f'image_{file_id[:5]}.jpg')
    user_id = int(update.message.from_user.id)
    user_name = str(update.message.from_user.first_name)
    print(context.user_data)
    tool_name = context.user_data['name']
    category = context.user_data['category']
    tool = Tool(user_id, tool_name)
    user = User.BOTUser(user_id, user_name)
    logger.info(f'User: {user.user_id} {user.user_name}, Tool: {tool.user_id} {tool.name}')
    homelyDB_API.add_tool(update, tool_name, category, user)
    ## SEND IFNO TO DB
    update.message.reply_text("Got your image!")
    update.message.reply_text("Your tool has been added and now available for borrowing. \n Thanks for being such a"
                              "great neighbor, neighbor! You can add another item "
                              "using /landtool or borrow from your neighbors using /borrowtool")
    context.user_data.get('name')
    context.user_data.get('category')
    gif_url='https://media.giphy.com/media/xTiN0CNHgoRf1Ha7CM/giphy.gif'
    context.bot.send_animation(chat_id=chat_id, animation=gif_url)
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Conversation cancelled by user. Bye. Send /landtool or /borrowtool to start again')
    return ConversationHandler.END


##LANDING HANDLERS##

_handlers = {}

_handlers['start_handler'] = CommandHandler('start', start)

_handlers['land_conversation_handler'] = ConversationHandler(
    entry_points=[CommandHandler('landtool', phone_number_handler)],
    fallbacks=[CommandHandler('cancel', cancel)],
    states={
        EXPECT_PHONE: [CommandHandler('cancel', cancel), MessageHandler(Filters.text, set_name_handler)],
        EXPECT_NAME: [CommandHandler('cancel', cancel), MessageHandler(Filters.text, name_input_by_user)],
        EXPECT_CATEGORY_BUTTON_CLICK: [CallbackQueryHandler(category_button_click_handler)],
        EXPECT_IMG: [MessageHandler(Filters.photo, img_input_by_user)],
    }

    # per_message=True,
)


##BORROWIG CODE
EXPECT_CATEGORY_SELECT_BUTTON_CLICK, EXPECT_ITEM_SELECTION = range(2)

def select_category_by_user(update: Update, context: CallbackContext):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Power Tools", callback_data='powertools')],
                                     [InlineKeyboardButton("Furniture",
                                                           callback_data='furniture')],
                                     [InlineKeyboardButton("Kitchen Appliances",
                                                           callback_data='appliances')],
                                     [InlineKeyboardButton("For kids",
                                                           callback_data='kids')],
                                     [InlineKeyboardButton("Electronics",
                                                           callback_data='electronics')],
                                     ])
    update.message.reply_text('Select the category of the item you are looking for:', reply_markup=keyboard)

    return EXPECT_CATEGORY_SELECT_BUTTON_CLICK


def category_button_click_handler(update: Update, context: CallbackContext):
    ''' This gets executed on button click '''
    category = update.callback_query.data
    context.user_data['category'] = category
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f'Fetching items under {category}')
    ##get 5 items from DB
    # for item in items:
    keyboard = ReplyKeyboardMarkup([[KeyboardButton("Screwdriver Phillips", callback_data='item1')],
                                     [KeyboardButton("Hammer",
                                                           callback_data='item2')],
                                     [KeyboardButton("Screwdriver Samsung",
                                                           callback_data='item3')],
                                     [KeyboardButton("Impact Drill",
                                                           callback_data='item4')],
                                     [KeyboardButton("Electric Saw",
                                                           callback_data='item5')],
                                     ])
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='These are the top five items currently available. '
                                  'Select an item to borrow it', reply_markup=keyboard)
    return EXPECT_ITEM_SELECTION


def get_item_info(update: Update, context: CallbackContext):
    item = update.callback_query.data
    #getinfo from DB
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Here is the photo of your item:')

    # photo = get from DB
    # context.bot.send_photo(chat_id=update.effective_chat.id,
    #                        photo=photo['file'])
    return ConversationHandler.END

_handlers['borrow_conversation_handler'] = ConversationHandler(
    entry_points=[CommandHandler('borrowtool', select_category_by_user)],
    fallbacks=[CommandHandler('cancel', cancel)],
    states={
        EXPECT_CATEGORY_SELECT_BUTTON_CLICK: [CallbackQueryHandler(category_button_click_handler)],
        EXPECT_ITEM_SELECTION: [CallbackQueryHandler(get_item_info)],
    }

    # per_message=True,
)

for name, _handler in _handlers.items():
    print(f'Adding handler {name}')
    dispatcher.add_handler(_handler)

logger.info("* Start polling...")
updater.start_polling()  # Starts polling in a background thread.
updater.idle()  # Wait until Ctrl+C is pressed
logger.info("* Bye!")
