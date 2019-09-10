"""
Shopping list class for sholibo the shopping list bot.

therealpeterpython - 47575127+therealpeterpython@users.noreply.github.com
2019
"""

from datetime import datetime
import json


class ShoppingList:
    def __init__(self):
        self._items = list()
        self._times = list()
        #self._chat_id = chat_id
        
    def __str__(self):
        out = list()
        out.append(list(zip(self._items, self._times)))
        #out.append(self._chat_id)
        return str(out)

        
    def empty(self):
        return not self._items
        
    def get_items(self):
        return self._items

    def get_times(self):
        return self._times

    #def get_chat_id(self):
    #    return self._chat_id
     
    def add_item(self, item):
        self._items.append(item)
        self._times.append(datetime.now())
        
    def add_items(self, items):
        time = datetime.now()
        self._items.extend(items)
        self._times.extend([time for _ in range(len(items))])
        
    def remove_item(self, pos):
        del self._items[pos]    
        del self._times[pos]
        
    def remove_all(self):
        self._items = list()
        self._times = list()
                
    def pprint_basic(self):
        pstr = ""
        for n, item in enumerate(self._items):
            pstr += "({}) {}\n".format(n, item)
        return pstr
        
    def pprint_full(self):
        pstr = ""
        for n, (item, date) in enumerate(zip(self._items, self._times)):
            pstr += "({}) {} [{}])\n".format(n, item, date.strftime("%d-%m-%Y %H:%M"))
        return pstr
