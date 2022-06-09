import logging
from aiogram import Bot, Dispatcher, executor, types
from db import BotDB
import markups as nav
import os
from dotenv import load_dotenv
from emoji import Emoji

# TODO при регистрации Помимо проверки наличия юзера проверять наличие номера телефона
# TODO удалить список
# TODO шеринг списков
# TODO эмодзи
# TODO эдит месседж вместо удаления
# TODO многострочное сообщение при добавлении в список - разбивать на отдельные продукты и сувать в БД

BOT_DB = BotDB('kupiplz.db')
load_dotenv()
TOKEN = os.getenv('TOKEN')
BOT = Bot(token=TOKEN)
DP = Dispatcher(BOT)

logging.basicConfig(level=logging.INFO)


@DP.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.chat.type == 'private':
        user_id = message.from_user.id
        await BOT.delete_message(message.chat.id, message.message_id)
        if not BOT_DB.user_exists(user_id): # TODO вот сюда проверку ИЛИ нет номера телефона
            msg = await BOT.send_message(user_id, "Для начала работы нужно предоставить свой номер телефона.\n"+Emoji.ARROW_DOWN.value +" Нажмите кнопку внизу"+Emoji.ARROW_DOWN.value, reply_markup=nav.get_contact_menu)
            BOT_DB.add_user(user_id, 0)
            BOT_DB.set_current_state(BOT_DB.get_user_id(user_id), "registration", msg.message_id)
        else:
            await BOT.send_message(user_id, "Добро пожаловать!\n"+Emoji.HOME.value+" Главное меню", reply_markup=nav.main_menu)


@DP.message_handler(content_types=['contact'])
async def registration(message):
    user_id = message.from_user.id
    if message.contact.user_id == user_id:
        await BOT.delete_message(message.chat.id, BOT_DB.get_current_state_msg(BOT_DB.get_user_id(user_id)))
        await BOT.delete_message(message.chat.id, message.message_id)
        BOT_DB.add_user(user_id, message.contact.phone_number)
        BOT_DB.clear_states(BOT_DB.get_user_id(user_id))
        BOT_DB.clear_current_list(BOT_DB.get_user_id(user_id))
        await BOT.send_message(user_id, "Добро пожаловать!\n"+Emoji.HOME.value+" Главное меню", reply_markup=nav.main_menu)
    else:
        await BOT.send_message(user_id, "Для начала работы нужно предоставить СВОЙ номер телефона", reply_markup=nav.get_contact_menu)


    # if message.chat.type == 'private':
    #     user_id = message.from_user.id
    #     if not BOT_DB.user_exists(user_id):
    #         BOT_DB.add_user(user_id)
    #     BOT_DB.clear_states(BOT_DB.get_user_id(user_id))
    #     BOT_DB.clear_current_list(BOT_DB.get_user_id(user_id))
    #     await BOT.delete_message(message.chat.id, message.message_id)
    #     await BOT.send_message(user_id, 'Добро пожаловать!\nГлавное меню', reply_markup=nav.main_menu)
    #     await BOT.send_message(user_id, Emoji.SIMPLE_MAN_SKIN_1.value+"Пример. Доделать!")



@DP.message_handler()
async def bot_message(message: types.Message):
    if message.chat.type == 'private':
        user_id = message.from_user.id
        text = message.text
        chat_id = message.chat.id
        message_id = message.message_id
        if BOT_DB.current_state_exist(BOT_DB.get_user_id(user_id)):
            if BOT_DB.get_current_state(BOT_DB.get_user_id(user_id)) == "AddingList":
                list_name = text
                BOT_DB.add_list(list_name, BOT_DB.get_user_id(user_id))
                list_id = BOT_DB.get_last_list_id()
                BOT_DB.set_current_list(BOT_DB.get_user_id(user_id), list_id)
                await BOT.delete_message(chat_id, BOT_DB.get_current_state_msg(BOT_DB.get_user_id(user_id)))
                BOT_DB.set_current_state(BOT_DB.get_user_id(user_id), "AddingProducts", 0)
                await BOT.delete_message(chat_id, message_id)
                msg = await BOT.send_message(user_id, "Список:" + list_name, reply_markup=nav.list_add_menu)
                BOT_DB.set_current_state(BOT_DB.get_user_id(user_id), "AddingProducts", msg.message_id)
            elif BOT_DB.get_current_state(BOT_DB.get_user_id(user_id)) == "AddingProducts":
                if BOT_DB.get_current_state_msg(BOT_DB.get_user_id(user_id)) != 0:
                    await BOT.delete_message(chat_id, BOT_DB.get_current_state_msg(BOT_DB.get_user_id(user_id)))
                list_id = BOT_DB.get_current_list(BOT_DB.get_user_id(user_id))
                list_name = BOT_DB.get_list_name_by_id(list_id)
                BOT_DB.add_product(list_id, text)
                products = BOT_DB.get_products(list_id)
                text = create_products_message_text(list_name, products)
                await BOT.delete_message(chat_id, message_id)
                msg = await BOT.send_message(user_id, text, reply_markup=nav.show_products(products), parse_mode="HTML")
                BOT_DB.set_current_state(BOT_DB.get_user_id(user_id), "AddingProducts", msg.message_id)
            else:
                await BOT.delete_message(chat_id, message_id)
        else:
            await BOT.delete_message(chat_id, message_id)


@DP.callback_query_handler(text="ListLook")
async def list_look(message: types.Message):
    user_id = message.from_user.id
    await BOT.delete_message(user_id, message.message.message_id)
    lists = BOT_DB.get_lists(BOT_DB.get_user_id(user_id))
    await BOT.send_message(user_id, "Ваши списки", reply_markup=nav.list_look_menu(lists))


@DP.callback_query_handler(text="ListAdd")
async def list_add(message: types.Message):
    user_id = message.from_user.id
    await BOT.delete_message(user_id, message.message.message_id)
    BOT_DB.set_current_state(BOT_DB.get_user_id(user_id), "AddingList", 0)
    msg = await BOT.send_message(user_id, "Введите имя списка:", reply_markup=nav.list_add_menu)
    BOT_DB.set_current_state(BOT_DB.get_user_id(user_id), "AddingList", msg.message_id)


@DP.callback_query_handler()
async def callback_inline(call):
    list_chosen = "ListChosen"
    list_adding = "ListAdding"
    list_editing = "ListEditing"
    if list_chosen in call.data:
        await chosen_list_handler(call)
    if list_adding in call.data:
        await adding_list_handler(call)
    if list_editing in call.data:
        await editing_list_handler(call)


async def editing_list_handler(call):
    if call.data == 'ListEditing_Back':
        BOT_DB.clear_states(BOT_DB.get_user_id(call.from_user.id))
        BOT_DB.clear_current_list(BOT_DB.get_user_id(call.from_user.id))
        await BOT.delete_message(call.message.chat.id, call.message.message_id)
        lists = BOT_DB.get_lists(BOT_DB.get_user_id(call.from_user.id))
        await BOT.send_message(call.message.chat.id, "Ваши списки:", reply_markup=nav.list_look_menu(lists))
    else:
        user_id = call.from_user.id
        product_id = int(call.data[12:])
        await BOT.delete_message(call.message.chat.id, call.message.message_id)
        BOT_DB.set_product_bought(product_id)
        list_id = BOT_DB.get_current_list(BOT_DB.get_user_id(user_id))
        products = BOT_DB.get_products(list_id)
        list_name = BOT_DB.get_list_name_by_id(list_id)
        text = create_products_message_text(list_name, products)
        msg = await BOT.send_message(user_id, text, reply_markup=nav.show_products(products), parse_mode="HTML")
        BOT_DB.set_current_state(BOT_DB.get_user_id(user_id), "AddingProducts", msg.message_id)


async def adding_list_handler(call):
    BOT_DB.clear_states(BOT_DB.get_user_id(call.from_user.id))
    BOT_DB.clear_current_list(BOT_DB.get_user_id(call.from_user.id))
    await BOT.delete_message(call.message.chat.id, call.message.message_id)
    lists = BOT_DB.get_lists(BOT_DB.get_user_id(call.from_user.id))
    await BOT.send_message(call.message.chat.id, "Ваши списки:", reply_markup=nav.list_look_menu(lists))


async def chosen_list_handler(call):
    user_id = call.from_user.id
    message_id = call.message.message_id
    if call.data == 'ListChosen_Back':
        BOT_DB.clear_states(BOT_DB.get_user_id(user_id))
        BOT_DB.clear_current_list(BOT_DB.get_user_id(user_id))
        await BOT.delete_message(call.message.chat.id, message_id)
        await BOT.send_message(call.message.chat.id, Emoji.HOME.value+" Главное меню", reply_markup=nav.main_menu)
        # await BOT.edit_message_text("Главное меню", call.message.chat.id, message_id, reply_markup=nav.main_menu)
    else:
        list_id = int(call.data[11:])
        await BOT.delete_message(call.message.chat.id, message_id)
        BOT_DB.set_current_list(BOT_DB.get_user_id(user_id), list_id)
        BOT_DB.set_current_state(BOT_DB.get_user_id(user_id), "AddingProducts", message_id)
        list_name = BOT_DB.get_list_name_by_id(list_id)
        products = BOT_DB.get_products(list_id)
        text = create_products_message_text(list_name, products)
        msg = await BOT.send_message(user_id, text, reply_markup=nav.show_products(products), parse_mode="HTML")
        BOT_DB.set_current_state(BOT_DB.get_user_id(user_id), "AddingProducts", msg.message_id)


def create_products_message_text(list_name, products):
    text = "<b>" + str(list_name) + "</b>\n\n"
    for product in products:
        if product[3]:
            text = text + "<s>"+str(product[1])+"</s>\n"
        else:
            text = text + str(product[1]) + "\n"
    return text


if __name__ == "__main__":
    executor.start_polling(DP, skip_updates=True)
