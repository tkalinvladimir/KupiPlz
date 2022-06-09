import sqlite3


class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    # ----------------- USER --------------
    def user_exists(self, user_id):
        # Проверяем, есть ли юзер в базе
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_user_id(self, user_id):
        # Достаем id юзера в базе по его user_id
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def add_user(self, user_id, phone):
        # Добавляем юзера в базу
        self.cursor.execute("INSERT INTO `users` (`user_id`, `phone`) VALUES (?, ?)", (user_id, phone,))
        return self.conn.commit()

    # -----------------      CURR STATES AND LISTS   --------------
    def set_current_state(self, user_id, state, msg_id):
        # Добавляем признак что пользователь хочет создать список
        self.cursor.execute("INSERT INTO `user_curr_states` (`user_id`, `state`, `msg_id`) VALUES (?, ?, ?)",
                            (user_id, state, msg_id,))
        return self.conn.commit()

    def set_current_list(self, user_id, list_id):
        # Добавляем текущий список юзеру для редактирования
        self.cursor.execute("INSERT INTO `user_curr_list` (`user_id`, `list_id`) VALUES (?, ?)", (user_id, list_id,))
        return self.conn.commit()

    def clear_current_list(self, user_id):
        # """Очищаем текущий лист"""
        self.cursor.execute("DELETE FROM `user_curr_list` WHERE `user_id`=?", (user_id,))
        return self.conn.commit()

    def get_current_list(self, user_id):
        # Получаем текущий список
        result = self.cursor.execute("SELECT `list_id` FROM `user_curr_list` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def current_state_exist(self, user_id):
        result = self.cursor.execute("SELECT `state` FROM `user_curr_states` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_current_state(self, user_id):
        # Получаем текущий стейт юзера
        result = self.cursor.execute("SELECT `state` FROM `user_curr_states` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def get_current_state_msg(self, user_id):
        # Получаем текущий стейт юзера
        result = self.cursor.execute("SELECT `msg_id` FROM `user_curr_states` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def clear_states(self, user_id):
        # Очищаем стейты юзера
        self.cursor.execute("DELETE FROM `user_curr_states` WHERE `user_id`=?", (user_id,))
        return self.conn.commit()

    # -----------------  LISTS  --------------
    def add_list(self, name, user_id):
        # Добавляем новый список"
        self.cursor.execute("INSERT into `lists` (`name`, `user_id`) VALUES (?, ?)", (name, user_id,))
        return self.conn.commit()

    def get_last_list_id(self):
        # Получаем айдишник созданного списка
        result = self.cursor.execute("SELECT `id` FROM `lists` ORDER BY `id` DESC LIMIT 1 ")
        return result.fetchone()[0]

    def get_lists(self, user_id):
        # Получаем список списков
        result = self.cursor.execute("SELECT * FROM `lists` WHERE `user_id` = ?", (user_id,))
        return result.fetchall()

    def get_list_name_by_id(self, list_id):
        # Получаем список списков
        result = self.cursor.execute("SELECT * FROM `lists` WHERE `id` = ?", (list_id,))
        return result.fetchone()[1]

    # -----------------  PRODUCTS --------------
    def add_product(self, list_id, name):
        # Добавление товара
        self.cursor.execute("INSERT into `products` ( `list_id`, `name`, `bought`) VALUES (?, ?, ?)",
                            (list_id, name, False,))
        return self.conn.commit()

    def get_products(self, list_id):
        # Получение товаров
        result = self.cursor.execute("SELECT * FROM `products` WHERE `list_id` = ?", (list_id,))
        return result.fetchall()

    def set_product_bought(self, product_id):
        # Пометим товар как купленный
        self.cursor.execute("UPDATE `products` SET `bought` = true WHERE `id` = ?", (product_id,))
        return self.conn.commit()