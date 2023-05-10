import asyncio
import os
import getpass

from datetime import datetime

from config import DB_SETTINGS
from guest import GuestQuery
from hotel import HotelQuery, RoomQuery, ResidentQuery


guest_query = GuestQuery(**DB_SETTINGS)
hotel_query = HotelQuery(**DB_SETTINGS)
resident_query = ResidentQuery(**DB_SETTINGS)
room_query = RoomQuery(**DB_SETTINGS)


def last_login():
    try:
        with open("auth.log", mode="r") as file:
            r = file.read()

        return r
    
    except OSError:
        return None

def write_last_login(login: str):
    with open("auth.log", mode="w") as file:
        file.write(login)


async def logging():
    login = last_login()
    if not login:
        login = input("Введите имя пользователя: ")
        write_last_login(login)

    a = True
    while a:
        print("Вы хотите сменить пользователя?\n1 - Да\nИначе просто нажмите Enter")
        change_login = input("")
        if change_login == "1":
            login = input("Введите имя пользователя: ")
            write_last_login(login)
    
        password = getpass.getpass("Введите пароль: ")
        if not await hotel_query.logging_user(login, password):
            return None
        
        print(f"Добро пожаловать, {login}")
        a = False
        return True
            

async def add_guest():
    a = True

    fullname = input("Фамилия Имя Отчество гостя: ")
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
                print("Некорректные паспортные данные")
        else:
            print("Некорректные паспортные данные")

    phone = input("Введите номер телефона: ")

    a = True

    while a:
        nutrition = input("Включить услуги питания?(да/нет)")
        if nutrition == "..":
            return
        if nutrition in ['д', 'да']:
            tp = input("Выберете тариф (Завтрак/Все включено): ")
            if tp.lower() in ['завтрак', 'все включено']:
                if tp.lower() == 'завтрак': nutrition = (await hotel_query.get())['nutrition_breakfast']
                else: nutrition = (await hotel_query.get())['nutrition_all']
                
                a = False
            
            elif tp == '..':
                return

            else:
                print("Некорректный тариф")
        elif nutrition in ['н', 'нет']:
            nutrition = 0
            a = False
        else:
            print("Введите корректно(да/нет)")


    a = True

    while a:
        parking = input("Включить услуги парковки?(да/нет)")
        if parking == "..":
            return
        if parking in ['д', 'да']:
            parking = (await hotel_query.get())['parking']
            a = False
        elif parking in ['н', 'нет']:
            parking = 0
            a = False
        else:
            print("Введите корректно(да/нет)")

    await guest_query.insert(fullname, count, passport, phone, nutrition, parking)
    print("Гость добавлен")


async def add_room():

    a = True

    while a:
        number = input("Введите номер комнаты: ")
        if number == "..":
            return
        if number.isdigit():
            a = False

        else:
            print("Введен некорректный номер")

    a = True

    while a:
        count = input("Введите количество мест: ")
        if count == "..":
            return
        if count.isdigit():
            a = False

        else:
            print("Некорректно введено число мест")

    a = True

    while a:
        status = input("Введите статус комнаты (В работе/Закрыт)")
        if status == "..":
            return
        if status.lower() in ['в работе', 'закрыт']:
            a = False
                                        
        else:
            print("Введены некорректные данные")

    a = True

    while a:
        tp = input("Введите тип комнаты (Эконом/Стандарт/Стандарт +/Полулюкс/Люкс): ")
        if tp == "..":
            return
        if tp.lower() in ["эконом", "стандарт", "стандарт +", "полулюкс", "люкс"]:
            a = False

        else:
            print("Введены некорректные данные")

    a = True

    while a:
        cost = input("Введите цену за комнату: ")
        if cost == "..":
            return
        if cost.isdigit():
            a = False

        else:
            print("Введена некорректная цена")

    await room_query.insert(number, count, status.lower(), tp.lower(), cost)
    print("Комната добавлена")


async def search_guest():

    a = True

    while a:

        print("Выбор:\n1 - по ID\n2 - по ФИО")
        num = input("Выберите действие, по которому будете искать гостя: ")

        if num == "..":  # добавим выход из функции по команде ".."
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
                    print("Действие не найдено")

        else:
            print("Номер действия некорректный")

async def search_guest_by_id():
    a = True

    while a:
        guest_id = input("Введите ID гостя: ")
        
        if guest_id.isdigit():
            guest = await guest_query.get(int(guest_id))
            a = False

        else:
            print("Введен некорретный ID гостя")

    if not guest:
        print("Результаты не найдены")
        return
    
    print(f"Результаты поиска (1)\n\nID: {guest.guest_id}\nФИО: {guest.fullname}")

async def search_guest_by_fullname():

    guest_fullname= input("Введите ФИО: ")
    guests = await guest_query.get_all_by_fullname(guest_fullname)

    if not guests:
        print("Результаты не найдены")
        return
    
    result = "\n\n".join(f"Результаты поиска({len(guests)})\nID: {i.guest_id}\nФИО: {i.fullname}" for i in guests)
    print(result)


async def search_room():
    a = True
    
    while a:

        print("Выбор:\n1 - по Номеру\n2 - по Статусу\n3 - по Типу")
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
                    print("Действие не найдено")

        else:
            print("Номер действия некорректный")

async def search_room_by_number():
    a = True

    while a:
        room_num = input("Введите номер комнаты: ")
        
        if room_num.isdigit():
            room = await room_query.get_by_number(int(room_num))
            a = False

        else:
            print("Введен некорретный ID номера")

    if not room:
        print("Результаты не найдены")
        return
    
    print(f"Результаты поиска (1)\n\nID: {room.room_id}\nСтатус: {room.status}\nЦена: {room.cost}")

async def search_room_by_status():
    
    room_status = input("Введите статус: ")
    rooms = await room_query.get_by_status(room_status)

    if not rooms:
        print("Результаты не найдены")
        return
    
    result = "\n\n".join(f"Результаты поиска({len(rooms)})\nID: {i.room_id}\nСтатус: {i.status}\nЦена: {i.cost}" for i in rooms)
    print(result)


async def search_room_by_type():
    
    room_type = input("Введите тип: ")
    rooms = await room_query.get_by_status(room_type.lower())

    if not rooms:
        print("Результаты не найдены")
        return
    
    result = "\n\n".join(f"Результаты поиска({len(rooms)})\nID: {i.room_id}\nСтатус: {i.status}\nЦена: {i.cost}" for i in rooms)
    print(result)


async def edit_guest():

    while True:

        print("Выбор:\n1 - по ID\n2 - по ФИО\n.. - выход из функции")
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
                    print("Действие не найдено")

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
            print("ID гостя некорректно")



    while True:
        print("Действия:\n1 - Изменить ФИО\n2 - Изменить номер телефона\n3 - Изменить паспортные данные\n.. - выход из функции")
        action = input("Выберете, что собираетесь изменять: ")

        if action.isdigit():
            
            match int(action):

                case 1:
                    fullname = input("Введите ФИО: ")
                    await guest_query.update_fullname_by_id(guest.guest_id, fullname)
                    print("ФИО гостя изменено")

                case 2:
                    phone = input("Введите номер телефона: ")
                    await guest_query.update_phone_by_id(guest.guest_id, phone)
                    print("Номер телефона гостя изменен")

                case 3:
                    passport = input("Введите паспортные данные в формате(СССС НННННН): ")
                    await guest_query.update_passport_by_id(guest.guest_id, passport)
                    print("Паспортные данные гостя изменены")

                case _:
                    print("Действие не найдено")

        elif action == '..':
            return

        else:
            print("Действие не найдено")

async def edit_guest_by_fullname():

    while True:
        guest_fullname = input("Введите ФИО гостя: ")

        if guest_fullname == "..":
            return

        guest = await guest_query.get_by_fullname(guest_fullname)

        if guest is not None:
            break

        else:
            print("Гость не найден")



    while True:
        print("Действия:\n1 - Изменить ФИО\n2 - Изменить номер телефона\n3 - Изменить паспортные данные\n.. - выход из функции")
        action = input("Выберете, что собираетесь изменять: ")

        if action.isdigit():
            
            match int(action):

                case 1:
                    fullname = input("Введите ФИО: ")
                    await guest_query.update_fullname_by_fullname(guest.fullname, fullname)
                    print("ФИО гостя изменено")

                case 2:
                    phone = input("Введите номер телефона: ")
                    await guest_query.update_phone_by_fullname(guest.fullname, phone)
                    print("Номер телефона гостя изменен")

                case 3:
                    passport = input("Введите паспортные данные в формате(СССС НННННН): ")
                    await guest_query.update_passport_by_fullname(guest.fullname, passport)
                    print("Паспортные данные гостя изменены")

                case _:
                    print("Действие не найдено")

        elif action == "..":
            return

        else:
            print("Действие не найдено")


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
                print("Гость по данному ID не найден")

        else:
            print("Введен некорректно ID гостя")

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
                    print(f"Комната не рассчитана на такое количество проживающих. Число мест: {room.count}, число проживающих: {guest.count}")


            else:
                print("Комната по данному ID не найдена ")

        else:
            print("Введен некорректный ID комнаты")

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
                    if not resident_query.is_busy_by_date(date_start, room.room_id):
                        a = False

                    else:
                        print("Номер на этот период занят")
                        return

                else:
                    print("Дата должна состоять из чисел. Формат: ДД.ММ.ГГГГ")

            else:
                print("Введена некорректная дата. Формат: ДД.ММ.ГГГГ")

        else:
            print("Введена некорретная дата. Формат: ДД.ММ.ГГГГ")

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
                        print("Дата выезда не может быть меньше/равна дате заезда")

                else:
                    print("Дата должна состоять из чисел. Формат: ДД.ММ.ГГГГ")

            else:
                print("Введена некорректная дата. Формат: ДД.ММ.ГГГГ")

        else:
            print("Введена некорретная дата. Формат: ДД.ММ.ГГГГ")

    await resident_query.insert(guest_id, room_id, date_start, date_end)
    delta: datetime = date_end - date_start
    price = delta.day*room.cost + delta.day*guest.parking + delta.day*guest.nutrition_breakfast + delta.day*guest.nutrition_all
    print(f"Запись о проживании добавлена для гостя с ID: {guest_id} в комнату с ID: {room_id}.")
    print(f"Сумма: {price}")


async def hotel_settings():
    
    a = True

    while a:
        print("Выберите действие:\n1 - Изменить название\n2 - Изменить стоимость завтрка\n3 - Изменить стоимость \"Все включено\"\n4 - Изменить стоимость парковки")
        num = input()

        if num.isdigit():
            
            match int(num):

                case 1:
                    name = input("Введите новое название отеля")
                    if name == '..':
                        break
                
                    await hotel_query.update_name(name)
                    print("Название отеля изменено")



                case 2:
                    while a:
                        price = input("Введите новую стоимость завтрака: ")
                        if price == "..":
                            break

                        elif price.isdigit():
                            await hotel_query.update_nutrition_breakfast(price)
                            print("Стоимость питания \"Завтрак\" обновлена")
                            break
                        

                        else:
                            print("Стоимость введена некорректно")

                case 3:
                    while a:
                        price = input("Введите новую стоимость \"Все включено\": ")
                        if price == "..":
                            break

                        elif price.isdigit():
                            await hotel_query.update_nutrition_all(price)
                            print("Стоимость питания \"Все включено\" обновлена")
                            break
                        

                        else:
                            print("Стоимость введена некорректно")

                case 4:
                    while a:
                        price = input("Введите новую стоимость парковки: ")
                        if price == "..":
                            break

                        elif price.isdigit():
                            await hotel_query.update_parking(price)
                            print("Стоимость парковки обновлена")
                            break
                        

                        else:
                            print("Стоимость введена некорректно")

                case _:
                    print("Действие не найдено")

        elif num == "..":
            return

        else:
            print("Некорретно введен номер действия")

async def search_rooms():
    
    a = True

    while a:
        today = datetime.today()
        free, busy = await room_query.get_free_room(today)

        print("Свободные комнаты на сегодня:\n" + '\n'.join(f"ID: {i.room_id}\nНомер комнаты: {i.number}\nЦена: {i.cost}" for i in free))
        print("Занятые комнаты на сегодня:\n" + '\n'.join(f"ID: {i.room_id}\nНомер комнаты: {i.number}\nЦена: {i.cost}" for i in busy))

async def search_resident():
    a = True

    while a:
        print("Выребите действие:\n1 - по Дате\n2 - по Номеру комнаты")
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
                                    print("Свободные комнаты: "+ "\n".join(f"ID: {i.room_id}\nНомер комнаты: {i.number}\nЦена: {i.cost}" for i in free))
                                    break
                                

                                else:
                                    print("Дата должна состоять из чисел. Формат: ДД.ММ.ГГГГ")

                            else:
                                print("Введена некорректная дата. Формат: ДД.ММ.ГГГГ")

                        else:
                            print("Введена некорретная дата. Формат: ДД.ММ.ГГГГ")

                case 2:
                    num = input("Введите номер комнаты: ")
                    if num == "..":
                        return
                    
                    if num.isdigit():
                        r = await resident_query.get_by_room_number(num)
                        if not r:
                            print("Комнаты не найдены")
                        
                        print(f"Комната №{num}\nЗаезд | Выезд" + "\n".join(f"{i.date_start.strftime('%d.%m.%Y')} | {i.date_end.strftime('%d.%m.%Y')}" for i in r))

                    else:
                        print("Номер комнаты введен некорректно")

                case _:
                    print("Действие не найдено")

        else:
            print("Действие введено некорректно")


async def main():
    while True:
        if await logging():
            os.system(f"title {(await hotel_query.get())['name']}")
            os.system(f"cls")
            print(f"Отель: {(await hotel_query.get())['name']}")
            print(f"Занято комнат: {len(await resident_query.busy_rooms())}, свободно комнат: {len(await room_query.all_rooms()) - len(await resident_query.busy_rooms())}")
            print(f"На данный момент проживает в отеле: {await resident_query.get_resident()}")
            print("\n\n")

            while True:
                
                print("Выберите команду: \n\n1 - Добавить гостя\n2 - Добавить номер\n3 - Добавить запись о проживании\n4 - Изменить гостя\n5 - Найти гостя\n6 - Найти комнату\n7 - Список комнат\n8 - Поиск по проживанию\n9 - Настройки отеля")
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

                        case _:
                            print("Действие не найдено")

                else:
                    print("Номер действия должен быть числом")

        else:
            print("Логин/пароль неверный(-е)")



if __name__ == "__main__":
    asyncio.run(main())