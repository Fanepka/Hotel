import asyncio
import os
import getpass

from datetime import datetime, timedelta

from config import DB_SETTINGS
from utils import get_discount, out_message, Fore, update_color_schema
from guest import GuestQuery
from hotel import HotelQuery, RoomQuery, ResidentQuery


guest_query = GuestQuery(**DB_SETTINGS)
hotel_query = HotelQuery(**DB_SETTINGS)
resident_query = ResidentQuery(**DB_SETTINGS)
room_query = RoomQuery(**DB_SETTINGS)


def last_login():
    try:
        with open("data/auth.log", mode="r") as file:
            r = file.read()

        return r
    
    except OSError:
        return None

def write_last_login(login: str):
    with open("data/auth.log", mode="w") as file:
        file.write(login)


async def logging():
    os.system("title Система обработки")
    login = last_login()
    if login:
        out_message("Вы хотите сменить пользователя?\n1 - Да\nИначе нажмите на Enter")
        change_login = input("")
        if change_login == "1":
            login = input("Введите пользователя: ")
            write_last_login(login)

    if not login:
        login = input("Введите пользователя: ")
        write_last_login(login)

    a = True
    while a:
    
        password = getpass.getpass("Введите пароль: ")
        if not await hotel_query.logging_user(login, password):
            return None
        
        out_message(f"Добро пожаловать, {login}")
        a = False
        return True

async def add_guest():
    a = True

    fullname = input("Введите ФИО: ")
    count = int(input("Количество людей: "))

    while a:
        passport = input("Введите паспортные данные в формате (СССС НННННН): ")
        if passport == "..":
            return
        obj = passport.split(" ")
        if len(obj) == 2:
            if obj[0].isdigit() and obj[1].isdigit():
                a = False
            else:
                out_message("Неверно введены паспортные данные")
        else:
            out_message("Неверно введены паспортные данные")

    phone = input("Введите номер телефона: ")

    a = True

    while a:
        nutrition = input("Добавлять еду?(Да/Нет)")
        if nutrition == "..":
            return
        if nutrition.lower() in ['д', 'да']:
            tp = input("Выберете тариф (Завтрак/Все включено): ")
            if tp.lower() in ['завтрак', 'все включено']:
                if tp.lower() == 'завтрак': nutrition = (await hotel_query.get())['nutrition_breakfast']
                else: nutrition = (await hotel_query.get())['nutrition_all']
                
                a = False
            
            elif tp == '..':
                return

            else:
                out_message("Неверный тариф")
        elif nutrition in ['н', 'нет']:
            nutrition = 0
            a = False
        else:
            out_message("Введите корректно (Да/Нет)")


    a = True

    while a:
        parking = input("Добавить парковку(Да/Нет)?")
        if parking == "..":
            return
        if parking.lower() in ['д' 'да']:
            parking = (await hotel_query.get())['parking']
            a = False
        elif parking.lower() in ['н', 'нет']:
            parking = 0
            a = False
        else:
            out_message("Введите корректно (да/нет)")

    await guest_query.insert(fullname, count, passport, phone, nutrition, parking)
    out_message("Гость добавлен")


async def add_room():

    a = True

    while a:
        number = input("Введите номер комнаты: ")
        if number == "..":
            return
        if number.isdigit():
            a = False

        else:
            out_message("Неверно введен номер комнаты")

    a = True

    while a:
        count = input("Введите количество кроватей: ")
        if count == "..":
            return
        if count.isdigit():
            a = False

        else:
            out_message("Неверно введено количество кроватей")

    a = True

    while a:
        status = input("Введите статус комнаты (В работе/Закрыт):")
        if status == "..":
            return
        if status.lower() in ['в работе', 'закрыт']:
            a = False
                                        
        else:
            out_message("Неверно введены данные")

    a = True

    while a:
        tp = input("Введите тип комнаты (Эконом/Стандарт/Стандарт+/Полулюкс/Люкс): ")
        if tp == "..":
            return
        if tp.lower() in ["эконом", "стандарт", "стандарт+", "полулюкс", "люкс"]:
            a = False

        else:
            out_message("Неверно введены данные")

    a = True

    while a:
        cost = input("Введите цену за номер: ")
        if cost == "..":
            return
        if cost.isdigit():
            a = False

        else:
            out_message("Неверно введена цена")

    await room_query.insert(number, count, status.lower(), tp.lower(), cost)
    out_message("Комната добавлена")


async def search_guest():

    a = True

    while a:

        out_message("Действия:\n1 - По ID\n2 - По ФИО")
        num = input("Выберете действие, по которому будете искать гостя: ")

        if num == "..":  # add a way to exit the function with the command ".."
            return

        if num.isdigit():
            match int(num):

                case 1:
                    await search_guest_by_id()
                    break

                case 2:
                    await search_guest_by_fullname()
                    break

                case _:
                    out_message("Действие не найдено")

        else:
            out_message("Неверный номер действия")

async def search_guest_by_id():
    a = True

    while a:
        guest_id = input("Введеите ID гостя: ")
        
        if guest_id.isdigit():
            guest = await guest_query.get(int(guest_id))
            a = False

        else:
            out_message("Неверный ID гостя")

    if not guest:
        out_message("Результаты не найден")
        return
    
    out_message(f"Список гостей (1)\n\nID: {guest.guest_id}\nФИО: {guest.fullname}")

async def search_guest_by_fullname():

    guest_fullname= input("Введите ФИО: ")
    guests = await guest_query.get_all_by_fullname(guest_fullname)

    if not guests:
        out_message("Результаты не найдены")
        return
    
    result = "\n\n".join(f"Результаты поиска({len(guests)})\nID: {i.guest_id}\nФИО: {i.fullname}" for i in guests)
    out_message(result)


async def search_room():
    a = True
    
    while a:

        out_message("Выбор:\n1 - по Номеру\n2 - по Статусу\n3 - по Типу")
        num = input("Выберете действие, по которому будете искать номер: ")

        if num == "..":  # добавим выход из функции по команде ".."
            return

        if num.isdigit():
            match int(num):

                case 1:
                    await search_room_by_number()
                    break

                case 2:
                    await search_room_by_status()
                    break

                case 3:
                    await search_room_by_type()
                    break

                case _:
                    out_message("Действие не найдено")

        else:
            out_message("Номер действия некорректный")

async def search_room_by_number():
    a = True

    while a:
        room_num = input("Введите номер комнаты: ")
        
        if room_num.isdigit():
            room = await room_query.get_by_number(int(room_num))
            a = False

        else:
            out_message("Введен некорретный ID номера")

    if not room:
        out_message("Результаты не найдены")
        return
    
    out_message(f"Результаты поиска (1)\n\nID: {room.room_id}\nСтатус: {room.status}\nЦена: {room.cost}")

async def search_room_by_status():
    
    room_status = input("Введите статус: ")
    rooms = await room_query.get_by_status(room_status)

    if not rooms:
        out_message("Результаты не найдены")
        return
    
    result = "\n\n".join(f"Результаты поиска({len(rooms)})\nID: {i.room_id}\nСтатус: {i.status}\nЦена: {i.cost}" for i in rooms)
    out_message(result)


async def search_room_by_type():
    
    room_type = input("Введите тип: ")
    rooms = await room_query.get_by_status(room_type.lower())

    if not rooms:
        out_message("Результаты не найдены")
        return
    
    result = "\n\n".join(f"Результаты поиска({len(rooms)})\nID: {i.room_id}\nСтатус: {i.status}\nЦена: {i.cost}" for i in rooms)
    out_message(result)


async def edit_guest():

    while True:

        out_message("Выбор:\n1 - по ID\n2 - по ФИО\n.. - выход из функции")
        num = input("Выберете действие, по которому будете изменять гостя: ")

        if num.isdigit():
            match int(num):

                case 1:
                    await edit_guest_by_id()
                    break

                case 2:
                    await edit_guest_by_fullname()
                    break

                case _:
                    out_message("Действие не найдено")

        elif num == "..":
            return

async def edit_guest_by_id():

    while True:
        guest_id = input("Введите ID гостя: ")

        if guest_id.isdigit():
            guest = await guest_query.get(int(guest_id))
            break

        elif guest_id == '..':
            return

        else:
            out_message("ID гостя некорректно")



    while True:
        out_message("Действия:\n1 - Изменить ФИО\n2 - Изменить номер телефона\n3 - Изменить паспортные данные\n.. - выход из функции")
        action = input("Выберете, что собираетесь изменять: ")

        if action.isdigit():
            
            match int(action):

                case 1:
                    fullname = input("Введите ФИО: ")
                    await guest_query.update_fullname_by_id(guest.guest_id, fullname)
                    out_message("ФИО гостя изменено")

                case 2:
                    phone = input("Введите номер телефона: ")
                    await guest_query.update_phone_by_id(guest.guest_id, phone)
                    out_message("Номер телефона гостя изменен")

                case 3:
                    passport = input("Введите паспортные данные в формате(СССС НННННН): ")
                    await guest_query.update_passport_by_id(guest.guest_id, passport)
                    out_message("Паспортные данные гостя изменены")

                case _:
                    out_message("Действие не найдено")

        elif action == '..':
            return

        else:
            out_message("Действие не найдено")

async def edit_guest_by_fullname():

    while True:
        guest_fullname = input("Введите ФИО гостя: ")

        if guest_fullname == "..":
            return

        guest = await guest_query.get_by_fullname(guest_fullname)

        if guest is not None:
            break

        else:
            out_message("Гость не найден")



    while True:
        out_message("Действия:\n1 - Изменить ФИО\n2 - Изменить номер телефона\n3 - Изменить паспортные данные\n.. - выход из функции")
        action = input("Выберете, что собираетесь изменять: ")

        if action.isdigit():
            
            match int(action):

                case 1:
                    fullname = input("Введите ФИО: ")
                    await guest_query.update_fullname_by_fullname(guest.fullname, fullname)
                    out_message("ФИО гостя изменено")

                case 2:
                    phone = input("Введите номер телефона: ")
                    await guest_query.update_phone_by_fullname(guest.fullname, phone)
                    out_message("Номер телефона гостя изменен")

                case 3:
                    passport = input("Введите паспортные данные в формате(СССС НННННН): ")
                    await guest_query.update_passport_by_fullname(guest.fullname, passport)
                    out_message("Паспортные данные гостя изменены")

                case _:
                    out_message("Действие не найдено")

        elif action == "..":
            return

        else:
            out_message("Действие не найдено")


async def add_resident():  
    a = True

    while a:
        guest_id = input("Введите ID гостя: ")
        
        if guest_id == "..":
            return

        if guest_id.isdigit():
            guest = await guest_query.get(int(guest_id))
            if guest:
                guest_id = guest.guest_id
                a = False

            else:
                out_message("Гость по данному ID не найден")

        else:
            out_message("Введен некорректно ID гостя")

    a = True

    while a:
        room_id = input("Введите ID комнаты: ")
        if room_id == "..":
            return

        if room_id.isdigit():
            room = await room_query.get(int(room_id))
            if room:
                if room.count >= guest.count:
                    room_id = room.room_id
                    a = False

                else:
                    out_message(f"Комната не рассчитана на такое количество проживающих. Число мест: {room.count}, число проживающих: {guest.count}")


            else:
                out_message("Комната по данному ID не найдена ")

        else:
            out_message("Введен некорректный ID комнаты")

    a = True

    while a:
        date_start = input("Введите дату заезда в формате(ДД.ММ.ГГГГ): ")
        if date_start == "..":
            return

        date_start_obj = date_start.split(".")
        if len(date_start_obj) == 3:
            if len(date_start_obj[0]) == 2 and len(date_start_obj[1]) == 2 and len(date_start_obj[2]) == 4:
                if date_start_obj[0].isdigit() and date_start_obj[1].isdigit() and date_start_obj[2].isdigit():
                    date_start = datetime(int(date_start_obj[2]), int(date_start_obj[1]), int(date_start_obj[0]))
                    if not await resident_query.is_busy_by_date(date_start, room.room_id):
                        discount = get_discount(date_start.day, date_start.month)
                        a = False

                    else:
                        out_message("Номер на этот период занят")
                        return

                else:
                    out_message("Дата должна состоять из чисел. Формат: ДД.ММ.ГГГГ")

            else:
                out_message("Введена некорректная дата. Формат: ДД.ММ.ГГГГ")

        else:
            out_message("Введена некорретная дата. Формат: ДД.ММ.ГГГГ")

    a = True

    while a:
        date_end = input("Введите дату выезда в формате(ДД.ММ.ГГГГ): ")
        if date_end == "..":
            return

        date_end_obj = date_end.split(".")
        if len(date_end_obj) == 3:
            if len(date_end_obj[0]) == 2 and len(date_end_obj[1]) == 2 and len(date_end_obj[2]) == 4:
                if date_end_obj[0].isdigit() and date_end_obj[1].isdigit() and date_end_obj[2].isdigit():
                    date_end = datetime(int(date_end_obj[2]), int(date_end_obj[1]), int(date_end_obj[0]))
                    if date_start < date_end:
                        a = False
                    
                    else:
                        out_message("Дата выезда не может быть меньше/равна дате заезда")

                else:
                    out_message("Дата должна состоять из чисел. Формат: ДД.ММ.ГГГГ")

            else:
                out_message("Введена некорректная дата. Формат: ДД.ММ.ГГГГ")

        else:
            out_message("Введена некорретная дата. Формат: ДД.ММ.ГГГГ")

    await resident_query.insert(guest_id, room_id, date_start, date_end)
    delta: timedelta = date_end - date_start
    price = delta.days*room.cost - delta.days*room.cost*discount + delta.days*guest.parking + delta.days*guest.nutrition_breakfast + delta.days*guest.nutrition_all
    out_message(f"Запись о проживании добавлена для гостя с ID: {guest_id} в комнату с ID: {room_id}.")
    out_message(f"Сумма: {price}")
    if discount > 0:
        out_message(f"Скидка: {discount*100}%")


async def hotel_settings():
    
    a = True

    while a:
        out_message("Выберите действие:\n1 - Изменить название\n2 - Изменить стоимость завтрака\n3 - Изменить стоимость \"Все включено\"\n4 - Изменить стоимость парковки")
        num = input()

        if num.isdigit():
            
            match int(num):

                case 1:
                    name = input("Введите новое название отеля: ")
                    if name == '..':
                        break
                
                    await hotel_query.update_name(name)
                    out_message("Название отеля изменено")



                case 2:
                    while a:
                        price = input("Введите новую стоимость завтрака: ")
                        if price == "..":
                            break

                        elif price.isdigit():
                            await hotel_query.update_nutrition_breakfast(price)
                            out_message("Стоимость питания \"Завтрак\" обновлена")
                            break
                        

                        else:
                            out_message("Стоимость введена некорректно")

                case 3:
                    while a:
                        price = input("Введите новую стоимость \"Все включено\": ")
                        if price == "..":
                            break

                        elif price.isdigit():
                            await hotel_query.update_nutrition_all(price)
                            out_message("Стоимость питания \"Все включено\" обновлена")
                            break
                        

                        else:
                            out_message("Стоимость введена некорректно")

                case 4:
                    while a:
                        price = input("Введите новую стоимость парковки: ")
                        if price == "..":
                            break

                        elif price.isdigit():
                            await hotel_query.update_parking(price)
                            out_message("Стоимость парковки обновлена")
                            break
                        

                        else:
                            out_message("Стоимость введена некорректно")

                case _:
                    out_message("Действие не найдено")

        elif num == "..":
            return

        else:
            out_message("Некорретно введен номер действия")

async def search_rooms():
    
    a = True

    while a:
        today = datetime.today()
        free, busy = await room_query.get_free_room(today)

        out_message("Свободные комнаты на сегодня:\n" + '\n'.join(f"ID: {i.room_id}\nНомер комнаты: {i.number}\nЦена: {i.cost}" for i in free), Fore.GREEN)
        out_message("Занятые комнаты на сегодня:\n" + '\n'.join(f"ID: {i.room_id}\nНомер комнаты: {i.number}\nЦена: {i.cost}" for i in busy), Fore.RED)
        a = False

async def search_resident():
    a = True

    while a:
        out_message("Выребите действие:\n1 - по Дате\n2 - по Номеру комнаты")
        num = input()
        if num == "..":
            return

        elif num.isdigit():
            
            match int(num):

                case 1:
                    while a:
                        date = input("Введите дату в формате(ДД.ММ.ГГГГ): ")
                        if date == "..":
                            return

                        date_obj = date.split(".")
                        if len(date_obj) == 3:
                            if len(date_obj[0]) == 2 and len(date_obj[1]) == 2 and len(date_obj[2]) == 4:
                                if date_obj[0].isdigit() and date_obj[1].isdigit() and date_obj[2].isdigit():
                                    date = datetime(int(date_obj[2]), int(date_obj[1]), int(date_obj[0]))
                                    free, busy = await room_query.get_free_room(date)
                                    out_message("Свободные комнаты: "+ "\n".join(f"ID: {i.room_id}\nНомер комнаты: {i.number}\nЦена: {i.cost}" for i in free))
                                    break
                                

                                else:
                                    out_message("Дата должна состоять из чисел. Формат: ДД.ММ.ГГГГ")

                            else:
                                out_message("Введена некорректная дата. Формат: ДД.ММ.ГГГГ")

                        else:
                            out_message("Введена некорретная дата. Формат: ДД.ММ.ГГГГ")

                case 2:
                    num = input("Введите номер комнаты: ")
                    if num == "..":
                        return
                    
                    if num.isdigit():
                        r = await resident_query.get_by_room_number(num)
                        if not r:
                            out_message("Комнаты не найдены")
                        
                        out_message(f"Комната №{num}\nЗаезд | Выезд" + "\n".join(f"{i.date_start.strftime('%d.%m.%Y')} | {i.date_end.strftime('%d.%m.%Y')}" for i in r))

                    else:
                        out_message("Номер комнаты введен некорректно")

                case _:
                    out_message("Действие не найдено")

        else:
            out_message("Действие введено некорректно")

def console_settings():
    
    out_message("Выберете цветовые схемы:\n1 - темно-зеленый фон и черный текст\n2 - зеленый фон и белый текст\n3 - белый фон и черный текст\n4 - белый фон и темно-синий текст\n5 - темно-синий фон и белый текст")
    
    while True:
        schema = input("")

        if schema == '..':
            break

        elif schema.isdigit():
            
            match int(schema):

                case 1:
                    update_color_schema(1)
                    out_message("Цвет обновлен")
                    break

                case 2:
                    update_color_schema(2)
                    out_message("Цвет обновлен")
                    break

                case 3:
                    update_color_schema(3)
                    out_message("Цвет обновлен")
                    break

                case 4:
                    update_color_schema(4)
                    out_message("Цвет обновлен")
                    break

                case 5:
                    update_color_schema(5)
                    out_message("Цвет обновлен")
                    break

                case _:
                    print("Номер не найден")

        else:
            print("Действие не найдено")


async def main():
    while True:
        if await logging():
            os.system(f"title {(await hotel_query.get())['name']}")
            os.system(f"cls")
            out_message(f"Отель: {(await hotel_query.get())['name']}")
            out_message(f"Занято комнат: {len(await resident_query.busy_rooms())}, свободно комнат: {len(await room_query.all_rooms()) - len(await resident_query.busy_rooms())}")
            out_message(f"На данный момент проживает в отеле: {await resident_query.get_resident()}")
            out_message("\n\n")

            while True:
                
                out_message("Выберите команду: \n\n1 - Добавить гостя\n2 - Добавить номер\n3 - Добавить запись о проживании\n4 - Изменить гостя\n5 - Найти гостя\n6 - Найти комнату\n7 - Список комнат\n8 - Поиск по проживанию\n9 - Настройки отеля\n10 - Настройка цветовой схемы консоли")
                num = input("Введите номер: ")
                if num.isdigit():

                    match int(num):

                        case 1:
                            await add_guest()

                        case 2:
                            await add_room()

                        case 3:
                            await add_resident()

                        case 4:
                            await edit_guest()

                        case 5:
                            await search_guest()

                        case 6:
                            await search_room()

                        case 7:
                            await search_rooms()

                        case 8:
                            await search_resident()

                        case 9:
                            await hotel_settings()

                        case 10:
                            console_settings()

                        case _:
                            out_message("Действие не найдено")

                else:
                    out_message("Номер действия должен быть числом")

        else:
            out_message("Логин/пароль неверный(-е)")