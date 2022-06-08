from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


main_menu = InlineKeyboardMarkup(row_width=2)
list_look_button = InlineKeyboardButton("Просмотреть списки", callback_data='ListLook')
list_add_button = InlineKeyboardButton("Создать список", callback_data='ListAdd')
main_menu.add(list_look_button, list_add_button)

list_add_menu = InlineKeyboardMarkup(row_width=1)
back_button_add_menu = InlineKeyboardButton("Назад", callback_data="ListAdding")
list_add_menu.add(back_button_add_menu)


def list_look_menu(lists):
    menu = InlineKeyboardMarkup(row_width=1)
    for list in lists:
        list_id = 'ListChosen_' + str(list[0])
        button = InlineKeyboardButton(str(list[1]), callback_data=list_id)
        menu.insert(button)
    back_button = InlineKeyboardButton("Назад", callback_data='ListChosen_Back')
    menu.insert(back_button)
    return menu


def show_products(products):
    menu = InlineKeyboardMarkup(row_width=1)
    for product in products:
        if not product[3]:
            product_id = 'ListEditing_' + str(product[0])
            button = InlineKeyboardButton(str(product[1]), callback_data=product_id)
            menu.insert(button)
    back_button = InlineKeyboardButton("Назад", callback_data='ListEditing_Back')
    menu.insert(back_button)
    return menu
