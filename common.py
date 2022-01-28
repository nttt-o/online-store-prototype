# -*- coding: utf-8 -*-
"""
Created on Fri May 28 11:34:37 2021

@author: nttt-o
"""
import pickle
import os.path
from datetime import datetime

global_context = {}
# это контекcт состояния workflow
# например:
# - после авторизации:  global_context = {'user' = <login>}
# - при редактировании пользователем заказа:
#   global_context = {'user' = <login>, 'order' = <номер редакт. заказа>}


def print_table(
    cls, table_filter, header="", footer=""
):
    # - первый столбец равен UID для всех объектов
    # table_filter = {
    #  <field> : (<compare_operation> , <value>)
    # }
    # учитываем global_context (добавляем его в table_filter)
    for field, val in global_context.items():
        table_filter[field] = ("=", val)

    # печать шапки таблицы
    table_width = sum(width[1] for width in cls.print_col)
    line = "-" * (table_width + len(cls.print_col) + 1)
    print("\n", header, sep="")
    print(line)
    for col, width in cls.print_col:
        print(f"|{col:{width}}", end="")
    else:
        print("|\n", line, sep="")

    # печать строк таблицы
    count = 0
    for key, row in cls.cached_data.items():
        do = True
        for field, (condition, val) in table_filter.items():
            if field in row:  # .keys():
                if condition == "=":
                    if row[field] != val:
                        do = False
                        break
                elif condition == ">":
                    if row[field] <= val:
                        do = False
                        break
                elif condition == "in":
                    if not row[field] in val:
                        do = False
                        break
        if do:
            count += 1
            print(f"|{key:{cls.print_col[0][1]}}", end="")
            for col, width in cls.print_col[1:]:
                print(f"|{row[col]:{width}}", end="")
            else:
                print("|")
    print(line)
    print(f"Итого позиций: {count}")
    if footer != "":
        print(footer)
    return True


def check_input(prompt, **constraints):

    # ввод данных с проверкой

    print("\n", Message.HINT_EMPTY_STRING, sep="", end="")
    while True:
        s = input(global_context_prompt() + prompt + " >").strip()
        if s == "":
            return ""
        error = ""
        for c, val in constraints.items():
            if (c == "identificator" and val is True) and not s.isidentifier():
                error += "- введенное значение должно быть идентификатором (начинаться с буквы и т.д.)\n"
            elif (c == "int_positive" and val is True) and (not s.isnumeric() or int(s) == 0):
                error += "- введенное значение должно быть положительным числом\n"
            elif (c == "int_not_negative" and val is True) and (not s.isnumeric()):
                error += "- введенное значение не должно быть отрицательным числом\n"
            elif (c == "price_type" and val is True) and \
                not (s.replace(".", "").isnumeric() and
                     (len(s.split(".")) == 1 or (len(s.split(".")) == 2 and len(s.split(".")[-1]) <= 2))):
                error += "- введенное значение должно быть в формате <рубли>.<коп>\n"
            elif c == "max_int_value" and (not s.isnumeric() or int(s) > val):
                error += f"- введенное значение должно быть не больше {val}\n"
            elif c == "max_len" and len(s) > val:
                error += f"- длина вводимой строки не должна превышать {val} символов\n"
        if error == "":
            return s
        else:
            print("ОШИБКА ВВОДА:")
            print(error)


class WF:  # Width of Fields
    NAME = 35
    LOGIN = 15
    PWD = 20
    TOVAR = 15
    PRICE = 9
    QNT = 10
    POSITION = 8
    NUM = 5
    DATE = 11
    STATUS = 15
    USER = 20


class OrderStatus:
    CREATED = "СОЗДАН"
    PAID = "ОПЛАЧЕН"
    SENT = "ОТПРАВЛЕН"
    DELIVERED = "ДОСТАВЛЕН"
    STATUS_FLOW = [CREATED, PAID, SENT, DELIVERED, None]


class Message:
    BYE = "Мы рады, что вы обратились к нам. Приходите еще!"
    STOP = "Работа в системе завершена"
    HINT_EMPTY_STRING = "... для выхода из режима ввода данных введите пустую строку..."


class DataObject:
    file = ""  # файл с данными
    cached_data = {}  # считанные из файла данные кэшируются и хранятся как
    # словарь с возможностью доступа по ключу (UID)
    # cached_data = {
    #  <UID> : {'field_name': <value>, 'field_name' : <value>, ...
    # }

    print_col = []  # столбцы для печати таблицы
    # print_col = [
    #   (<column_name>, <column_width>), ...
    # ]

    @classmethod
    def load_data(cls):
        if os.path.isfile(cls.file):
            with open(cls.file, "rb") as f:
                cls.cached_data = pickle.load(f)
        else:
            cls.cached_data = {}

    def write(self):
        """ Запись объекта в cached_data (пишутся только нужные атрибуты) и в файл """
        obj_attributes = {}
        for attr in dir(self):
            # отбор требуемых атрибутов объекта:
            # не скрытые, не функции, не наследуемые от DataObject, не UID
            if (
                not attr.startswith("__")
                and not callable(getattr(self, attr))
                and attr not in dir(DataObject)
                and attr != "uid"
            ):
                obj_attributes[attr] = getattr(self, attr)
        self.cached_data[self.uid] = obj_attributes
        with open(self.file, "wb") as f:
            pickle.dump(self.cached_data, f)

    @classmethod
    def write_cache(cls):
        """  Запись cached_data в файл  """
        with open(cls.file, "wb") as f:
            pickle.dump(cls.cached_data, f)


class User(DataObject):
    file = "Users.db"
    cached_data = {}

    print_col = [("login", WF.LOGIN),  # UID
                 ("name", WF.NAME)
                 ]

    def __init__(self, name, login, pwd):
        self.uid = login
        self.name = name
        self.pwd = pwd
        self.write()


class Item(DataObject):
    file = "Items.db"
    cached_data = {}

    print_col = [("tovar", WF.TOVAR),  # UID
                 ("instock", WF.QNT),
                 ("price", WF.PRICE)
                 ]

    def __init__(self, name, instock, price):
        self.uid = name
        self.instock = instock
        self.price = price
        self.write()


class Order(DataObject):
    file = "Orders.db"
    cached_data = {}

    print_col = [
        ("num", WF.NUM),  # UID
        ("date", WF.DATE),
        ("status", WF.STATUS),
        ("user", WF.USER),
    ]

    def __init__(self, user):
        self.uid = str(int(max(self.cached_data.keys(), default="0")) + 1)  # UID
        self.date = datetime.today().strftime("%d/%m/%y")
        self.status = OrderStatus.CREATED
        self.user = user
        self.write()


class OrderDetail(DataObject):
    file = "OrderDetail.db"
    cached_data = {}

    print_col = [
        ("position", WF.POSITION),
        ("tovar", WF.TOVAR),
        ("quantity", WF.QNT),
        ("price", WF.PRICE),
    ]

    def __init__(self, order, tovar, quantity, price):
        self.uid = (
            order
            + "."
            + str((int(max(self.cached_data.keys(),
                           key=lambda uid: int(uid.split(".")[1])
                           if uid.split(".")[0] == order else 0,
                           default=order + ".0").split(".")[1]) + 1))
        )  # UID
        self.order = order
        self.tovar = tovar
        self.price = price
        self.quantity = quantity
        self.write()


def load_all():
    #  Первоначальная загрузка всех данных
    for cls in [Order, Item, User, OrderDetail]:
        cls.load_data()


def print_msg(msg):
    print(msg)
    return True


def print_operations(flow, state):
    print("\nДля выбора операции нажмите:")
    for k, v in flow[state].items():
        print(f"[{k}]", "-", v[0])


def global_context_prompt():
    prompt = ""
    for key in ["user", "order"]:
        if key in global_context:  # .keys():
            if key == "order":
                prompt += "Заказ "
            prompt += str(global_context[key]) + "/"
    return prompt


def print_auth():
    while True:
        login = check_input("Введите логин")
        if login == "":
            return False
        elif login not in User.cached_data:  # .keys():
            print("Ваш логин не найден")
        else:
            break
    while True:
        password = check_input("Введите пароль")
        if password == "":
            return False
        elif User.cached_data[login]["pwd"] != password:
            print("Пароль не верен. Повторите ввод.")
        else:
            break
    global_context["user"] = login
    return True


def print_reg():
    while True:
        name = check_input("Введите свое имя", max_len=WF.NAME)
        if name == "":
            return False
        else:
            break
    while True:
        login = check_input("Придумайте логин", identificator=True, max_len=WF.LOGIN)
        if login == "":
            return False
        else:
            break
    while True:
        password = check_input("Придумайте пароль", max_len=WF.PWD)
        if password == "":
            return False
        else:
            break
    User(name, login, password)
    global_context["user"] = login
    return True


def create_order():
    order = Order(global_context["user"]).uid
    global_context["order"] = order
    print(f"\nПОЗДРАВЛЯЕМ! Вы создали новый заказ под номером {order}")
    return True


def delete_order():
    print_table(Order, {"status": ("=", OrderStatus.CREATED)}, "Перечень заказов, доступных для удаления")
    order = check_input("Введите номер удаляемого заказа")
    if (
        order in Order.cached_data
        and Order.cached_data[order]["user"] == global_context["user"]
    ):
        if Order.cached_data[order]["status"] == OrderStatus.CREATED:
            Order.cached_data.pop(order)
            Order.write_cache()

            for key in list(OrderDetail.cached_data.keys()):
                if key.startswith(order + '.'):
                    OrderDetail.cached_data.pop(key)
            OrderDetail.write_cache()

            print(f"Заказ {order} удален")
            return True
        else:
            print(f"Заказ {order} нельзя удалить, т.к. он {Order.cached_data[order]['status']}")
            return False
    else:
        print(f"Номер заказа {order} не существует")
        return False


def edit_order():
    print_table(
        Order,
        {"status": ("=", OrderStatus.CREATED)},
        "Перечень заказов, доступных для редактирования",
    )
    order = check_input("Введите номер заказа для редактирования")
    if (
        order in Order.cached_data
        and Order.cached_data[order]["user"] == global_context["user"]
    ):
        if Order.cached_data[order]["status"] == OrderStatus.CREATED:
            global_context["order"] = order
            print_table(OrderDetail, {}, f"Состав заказа {global_context['order']}")
            return True
        else:
            print(
                f"Заказ {order} нельзя редактировать, т.к. он {Order.cached_data[order]['status']}"
            )
            return False
    else:
        print(f"Номер заказа {order} не существует")
        return False


def update_order_price(order):
    changes = ""
    for uid, row in OrderDetail.cached_data.items():
        if row["order"] == order:
            tovar = row["tovar"]
            price = row["price"]
            new_price = Item.cached_data[tovar]["price"]
            if price != new_price:
                changes += (
                    f"На товар {tovar} изменилась цена с {price} на {new_price}\n"
                )
                OrderDetail.cached_data[uid]["price"] = new_price
    OrderDetail.write_cache()
    return changes


def view_order():
    order = check_input("Введите номер заказа для просмотра")
    if (
        order in Order.cached_data
        and Order.cached_data[order]["user"] == global_context["user"]
    ):
        global_context["order"] = order
        # обновляем цену товара в OrderDetail на момент оплаты
        changes = update_order_price(order)
        print_table(OrderDetail, {}, f"Состав заказа {global_context['order']}")
        if changes != "":
            print("ВНИМАНИЕ!", changes, "Цены в заказе обновлены!", sep="\n")
        move_to_next_workflow_state = Order.cached_data[order]['status'] == OrderStatus.CREATED
        return move_to_next_workflow_state
    else:
        print(f"Номер заказа {order} не существует")
        return False


def change_order_status():
    its_client = "user" in global_context
    if its_client:
        print_table(Order, {"status": ("=", OrderStatus.CREATED)},"Перечень заказов для оплаты")
    else:
        print_table(Order, {"status": ("in", [OrderStatus.PAID, OrderStatus.SENT])}, "Перечень заказов для изменения статуса")
    order = check_input("Введите номер заказа")
    if order in Order.cached_data:
        status = Order.cached_data[order]["status"]
        if its_client:
            next_status = OrderStatus.PAID
        else:
            next_status = OrderStatus.STATUS_FLOW[OrderStatus.STATUS_FLOW.index(status) + 1]
        if (
            status == OrderStatus.CREATED
            and Order.cached_data[order]["user"] == global_context.get("user", "")
            and len(list(filter(lambda row: True if row["order"] == order else False, OrderDetail.cached_data.values()))) > 0) \
            or (status in [OrderStatus.PAID, OrderStatus.SENT] and not its_client):
            if next_status == OrderStatus.PAID:
                # обновление цены товара в OrderDetail на момент оплаты
                changes = update_order_price(order)
                if changes != "":
                    print("ВНИМАНИЕ!", changes, "Цены в заказе обновлены!", sep="\n")
                # проверка наличия товара
                for uid, row in OrderDetail.cached_data.items():
                    if row["order"] == order:
                        tovar = row["tovar"]
                        if row["quantity"] > Item.cached_data[tovar]["instock"]:
                            print(f"Товара {tovar} недостаточно на складе. Отредактируйте заказ.")
                            return False
                # редактирование наличия
                for uid, row in OrderDetail.cached_data.items():
                    if row["order"] == order:
                        tovar = row["tovar"]
                        Item.cached_data[tovar]["instock"] -= row["quantity"]
                Item.write_cache()
            Order.cached_data[order]["status"] = next_status
            Order.write_cache()
            print(f"Заказ {order} переведен в статус {next_status}")
            return True
        else:
            print(f"Вам запрещено переводить заказ {order} в cтатус {next_status}")
            return False
    else:
        print(f"Заказ {order} не найден")
        return False


def remove_order_context():
    global_context.pop("order")
    return True


def add_position():
    print_table(Item, {"instock": (">", 0)}, "Товары в наличии", "Успейте купить!")
    while True:
        tovar = check_input("Добавление товара:\nВведите наименование товара", max_len=WF.TOVAR).lower().title()
        if tovar == "":
            return False
        if tovar not in Item.cached_data:  # .keys()
            print("Такой товар не найден. Повторите ввод")
        elif len(list(filter(lambda row: True
                             if row["tovar"] == tovar and row["order"] == global_context["order"]
                             else False, OrderDetail.cached_data.values()))
                 ) > 0:
            print("Товары не могут дублироваться в заказе. Повторите ввод")
        else:
            break
    instock = Item.cached_data[tovar]["instock"]
    while True:
        quantity = check_input(
            f"Введите количество товара (не более {instock})",
            int_positive=True,
            max_int_value=instock)
        if quantity == "":
            return False
        else:
            break
    quantity = int(quantity)
    OrderDetail(global_context["order"], tovar,
                quantity, Item.cached_data[tovar]["price"])
    OrderDetail.write_cache()
    return True


def delete_position():
    print_table(OrderDetail, {}, f"Состав заказа {global_context['order']}")
    while True:
        position = check_input("Введите код удаляемой позиции", max_len=WF.POSITION)
        if position == "":
            return False
        if position not in OrderDetail.cached_data:  # .keys()
            print("Позиция заказа не найдена. Повторите ввод.")
        else:
            break
    print(f"Позиция заказа с кодом {position} удалена")
    OrderDetail.cached_data.pop(position)
    OrderDetail.write_cache()
    return True


def edit_position():
    print_table(OrderDetail, {}, f"Состав заказа {global_context['order']}")
    while True:
        position = check_input("Введите номер позиции", max_len=WF.POSITION)
        if position == "":
            return False
        if position not in OrderDetail.cached_data:  # .keys()
            print("Позиция заказа не найдена. Повторите ввод.")
        else:
            break
    tovar = OrderDetail.cached_data[position]["tovar"]
    instock = Item.cached_data[tovar]["instock"]
    while True:
        quantity = check_input(
            f"Введите новое количество товара (не более {instock})",
            int_positive=True,
            max_int_value=instock)
        if quantity == "":
            return False
        else:
            break
    quantity = int(quantity)
    OrderDetail.cached_data[position]["quantity"] = quantity
    new_price = Item.cached_data[tovar]["price"]
    if OrderDetail.cached_data[position]["price"] != new_price:
        print(f"Позиция заказа с кодом {position}: новое значение цены {new_price}")
        OrderDetail.cached_data[position]["price"] = new_price
    OrderDetail.write_cache()
    print(f"Позиция заказа с кодом {position}: изменено кол-во")
    return True


def edit_item(field):
    while True:
        tovar = check_input(
            f"Изменение {field}:\nВведите наименование товара", max_len=WF.TOVAR
        ).lower().title()
        if tovar == "":
            return False
        if tovar not in Item.cached_data:  # .keys()
            print("Товар не найден. Повторите ввод.")
        else:
            break
    if field == "instock":
        new_value = check_input(
            "Введите новое значение кол-ва на складе", int_not_negative=True, max_len=WF.QNT
        )
        if new_value == "":
            return False
        Item.cached_data[tovar][field] = int(new_value)
    elif field == "price":
        new_value = check_input(
            "Введите новое значение цены", price_type=True, max_len=WF.PRICE
        )
        if new_value == "":
            return False
        Item.cached_data[tovar][field] = float(new_value)
    Item.write_cache()
    print_table(Item, {}, "Товары:")
    print(f"Товар {tovar}: {field} установлено значение {new_value}")
    return True


class WorkFlow:
    WF_FUNC_AND_ARGS = slice(1, 3)
    WF_NEXT_STATE = 3

    client_flow = {
        # <текущее состояние>: {
        # <команда> : [<имя операции>, <исполняющая функция>, [<аргументы функции>], <новое состояние>]
        # }
        # Переход в новое состояние осуществляется, только если исполняющая функция возвращает "True"
        "UNAUTHORIZED": {
            "Т": ["Посмотреть товары", print_table, [Item, {}, "Товары интернет-магазина:", "Все товары отличного качества!"], "UNAUTHORIZED"],
            "Р": ["Зарегистрироваться", print_reg, [], "AUTHORIZED"],
            "А": ["Авторизоваться", print_auth, [], "AUTHORIZED"],
            ".": ["Выйти из системы", print_msg, [Message.BYE], "STOP"]
            },
        "AUTHORIZED": {
            "Т": ["Посмотреть все товары", print_table, [Item, {}, "Товары интернет-магазина:", "Все товары отличного качества!"], "AUTHORIZED"],
            "Н": ["Посмотреть товары в наличии", print_table, [Item, {"instock": (">", 0)}, "Товары в наличии:", "Товары заканчиваются. Успейте купить!"], "AUTHORIZED"],
            "З": ["Посмотреть список заказов для выполнения операций с ними", print_table, [Order, {}, "Список ваших заказов:", "Почему так мало? Оформите еще заказ!"], "VIEW_ORDER_LIST"],
            "НЗ": ["Создать новый заказ", create_order, [], "EDIT_ORDER"],
            ".": ["Выйти из системы", print_msg, [Message.BYE], "STOP"]
            },
        "EDIT_ORDER": {
            "+": ["Добавить товар", add_position, [], "EDIT_ORDER"],
            "-": ["Удалить товар", delete_position, [], "EDIT_ORDER"],
            "И": ["Изменить кол-во товара", edit_position, [], "EDIT_ORDER"],
            "Х": ["Выйти из режима редактирования заказа", remove_order_context, [], "VIEW_ORDER_LIST"],
            ".": ["Выйти из системы", print_msg, [Message.BYE], "STOP"]
            },
        "VIEW_ORDER_LIST": {
            "П": ["Просмотреть заказ", view_order, [], "EDIT_ORDER"],
            "З": ["Редактировать заказ", edit_order, [], "EDIT_ORDER"],
            "О": ["Подвердить и оплатить заказ", change_order_status, [], "AUTHORIZED"],
            "У": ["Удалить заказ", delete_order, [], "AUTHORIZED"],
            "НЗ": ["Создать новый заказ", create_order, [], "EDIT_ORDER"],
            "Х": ["Выйти из режима просмотра cписка заказов", lambda: True, [], "AUTHORIZED"],
            ".": ["Выйти из системы", print_msg, [Message.BYE], "STOP"]
            },
        }

    owner_flow = {
        "MENU": {
            "Т": ["Просмотреть каталог товаров для выполнения операций с ними", print_table, [Item, {}, "Товары:", ""], "ITEMS"],
            "З": ["Просмотреть оплаченные заказы", print_table, [Order, {"status": ("=", OrderStatus.PAID)}, "Оплаченные заказы"], "ORDERS"],
            "О": ["Просмотреть отправленные заказы", print_table,[Order, {"status": ("=", OrderStatus.SENT)}, "Отправленные заказы"], "ORDERS"],
            ".": ["Выйти из системы", print_msg, [Message.STOP], "STOP"]
            },
        "ITEMS": {
            "Ц": ["Изменить цену отдельного товара", edit_item, ["price"], "ITEMS"],
            "К": ["Изменить количество отдельного товара", edit_item, ["instock"], "ITEMS"],
            "Х": ["Выйти из режима просмотра каталога товаров", lambda: True, [], "MENU"],
            ".": ["Выйти из системы", print_msg, [Message.STOP], "STOP"],
            },
        "ORDERS": {
            "С": [f"Изменить статус заказа на 'следующий' по цепочке {OrderStatus.PAID}->{OrderStatus.SENT}->{OrderStatus.DELIVERED}", change_order_status, [], "ORDERS"],
            "Х": ["Выйти из режима просмотра заказов", lambda: True, [], "MENU"],
            ".": ["Выйти из системы", print_msg, [Message.STOP], "STOP"],
            },
    }


def run_flow(flow: dict, init_state: str, greetings: str):
    global global_context

    state = init_state  # начальное состояние
    global_context = {}  # начальный контекст workflow
    print(greetings)  # печать приветствия

    while state != "STOP":
        print_operations(flow, state)  # печать списка доступных операций
        operation = input(global_context_prompt() + "Выберите операцию > ").upper()
        if operation in flow[state]:
            func, args = flow[state][operation][WorkFlow.WF_FUNC_AND_ARGS]
            if func(*args):  # исполнение функции, реализующей операцию
                state = flow[state][operation][WorkFlow.WF_NEXT_STATE]
                # переход в новое состояние
        else:
            print("Ввод некорректен")
