# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 11:51:11 2021

@author: nttt-o
"""

import common as web_shop

web_shop.load_all()

web_shop.run_flow(
    web_shop.WorkFlow.client_flow,
    init_state="UNAUTHORIZED",
    greetings="Добро пожаловать в интернет-магазин!",
)
