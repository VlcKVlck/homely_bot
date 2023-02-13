import random

import pymongo
import gridfs
import requests
from classes import Tool
from classes import User
from telegram import Update
from classes.Tool import Tool

from telegram.ext import Updater

my_client = pymongo.MongoClient("mongodb://localhost:27017")

homely_DB = my_client['homely']
user_cl = homely_DB['users']
tool_cl = homely_DB['tools']
image_cl = homely_DB['images']

fs = gridfs.GridFS(homely_DB)
fs_bucket = gridfs.GridFSBucket(homely_DB)


def add_tool(update: Update, tool_name, category, phone, user: User):
    image = update.message.photo[-1]
    image_data = image.get_file()

    image_url = image_data.file_path
    image_file = requests.get(image_url)
    name = random.randint(0, 1000)
    image_ref = fs.put(image_file.content, filename=f'{name}.jpg')

    tool = Tool (user.user_id, tool_name, category, image_ref, phone)
    print (tool, "added")
    tool_cl.insert_one(tool.__dict__)
    # print(user_cl.find({"user_id": user.user_id}))
    if not user_cl.find_one({"user_id": user.user_id}):
        user_cl.insert_one(user.__dict__)


def send_image(tool_name: str, chat_id: str):
    curr_tool: Tool = tool_cl.find_one({"name": tool_name})
    print (curr_tool, "img")
    return curr_tool['image_ref']

def send_phone(tool_name: str, chat_id: str):
    curr_tool: Tool = tool_cl.find_one({"name": tool_name})
    print (curr_tool, "phone")
    return curr_tool['phone']

# def remove_tool(tool: Tool):
#     tool_cl.delete_one(tool.__dict__)

def get_list_by_category (category):
    return( list(tool_cl.find({'category': category}).limit(5)))

# def borrow_tool(tool: Tool):
#     if tool_cl[tool.name].availability:
#         tool_cl[tool.name].set_availability(False)
#     pass
#
# def return_tool(tool: Tool):
#     tool_cl[tool.name].set_availability(True)