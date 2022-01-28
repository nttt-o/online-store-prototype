# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 11:52:25 2021

@author: nttt-o
"""

import common as inet_shop

inet_shop.load_all()

inet_shop.run_flow(
    inet_shop.WorkFlow.owner_flow,
    init_state="MENU",
    greetings="Интерфейс администратора интернет-магазина",
)

# Закомментированный ниже код использовался для первоначального заполнения
# базы данных 


# inet_shop.Item('Ершик', 100, 12.50)
# inet_shop.Item('Рыбка', 20, 100.00)
# inet_shop.Item('Заяц', 5, 100.00)
# inet_shop.Item('Собачка', 0, 1450.0)


# inet_shop.User('Осина Н.Д.', login='osina', pwd='12345')

# inet_shop.Order('osina')
# inet_shop.OrderDetail('1','Рыбка', 15, 30.00)
# inet_shop.OrderDetail('1','Заяц', 1, 70.00)

# inet_shop.OrderDetail('2','Ершик', 10, 12.50)
# inet_shop.Order('osina')