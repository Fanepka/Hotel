import json
from colorama import Fore, Back, init


init()


def open_json(name: str):
    with open(name, mode='r') as js:
        file = json.load(js)

    return file

def write_json(name: str, data: list):
    with open(name, mode='w') as fl:
        json.dump(data, fl, ensure_ascii=False, indent= 4)



def out_message(message: str, color: str = None):
    file = open_json("data/config.json")
    back = file[0]['background-color']
    text = file[0]['text-color']

    if not color:
        print(back + text + message + Back.RESET)

    else:
        print(Back.RESET + color + message + Back.RESET)

def update_color_schema(number: int):
    fl = open_json('data/config.json')

    match number:

        case 1:
            fl[0]['background-color'] = Back.GREEN
            fl[0]['text-color'] = Fore.BLACK
            write_json('data/config.json', fl)

        case 2:
            fl[0]['background-color'] = Back.GREEN
            fl[0]['text-color'] = Fore.WHITE
            write_json('data/config.json', fl)

        case 3:
            fl[0]['background-color'] = Back.WHITE
            fl[0]['text-color'] = Fore.BLACK
            write_json('data/config.json', fl)

        case 4:
            fl[0]['background-color'] = Back.WHITE
            fl[0]['text-color'] = Fore.BLUE
            write_json('data/config.json', fl)

        case 5:
            fl[0]['background-color'] = Back.BLUE
            fl[0]['text-color'] = Fore.WHITE
            write_json('data/config.json', fl)


def get_discount(day: int, month: int):
    discount = 0

    if month in [12, 1, 2]:
        discount = 0.15

    if month == 12 and day >= 30 and day <= 31:
        discount = -0.3

    if month == 1 and day <= 7:
        discount = -0.3

    if month == 2 and day >= 22 and day <= 24:
        discount = -0.3

    if month == 3 and day >= 7 and day <= 9:
        discount = -0.3

    if month == 4 and day >= 30 or month == 5 and day <= 10:
        discount = -0.3

    return discount

#print(get_discount(30, 12))