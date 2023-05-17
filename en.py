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
    os.system("title Work accounting system")
    login = last_login()
    if login:
        out_message("Do you want to change the user?\n1 - Yes\nOtherwise just press Enter")
        change_login = input("")
        if change_login == "1":
            login = input("Enter username: ")
            write_last_login(login)

    if not login:
        login = input("Enter username: ")
        write_last_login(login)

    a = True
    while a:
    
        password = getpass.getpass("Enter password: ")
        if not await hotel_query.logging_user(login, password):
            return None
        
        out_message(f"Welcome, {login}")
        a = False
        return True
            

async def add_guest():
    a = True

    fullname = input("Guest full name: ")
    count = int(input("Number of people: "))

    while a:
        passport = input("Enter passport data in format (SSSS NNNNNNN): ")
        if passport == "..":
            return
        obj = passport.split(" ")
        if len(obj) == 2:
            if obj[0].isdigit() and obj[1].isdigit():
                a = False
            else:
                out_message("Incorrect passport data")
        else:
            out_message("Incorrect passport data")

    phone = input("Enter phone number: ")

    a = True

    while a:
        nutrition = input("Include catering services?(Yes/No)")
        if nutrition == "..":
            return
        if nutrition in ['Y', 'Yes']:
            tp = input("Choose the tariff (Breakfast/All inclusive): ")
            if tp.lower() in ['breakfast', 'all inclusive']:
                if tp.lower() == 'breakfast': nutrition = (await hotel_query.get())['nutrition_breakfast']
                else: nutrition = (await hotel_query.get())['nutrition_all']
                
                a = False
            
            elif tp == '..':
                return

            else:
                out_message("Invalid tariff")
        elif nutrition in ['N', 'No']:
            nutrition = 0
            a = False
        else:
            out_message("Please enter correctly (Yes/No)")


    a = True

    while a:
        parking = input("Include parking services?(Yes/No)")
        if parking == "..":
            return
        if parking in ['Y', 'Yes']:
            parking = (await hotel_query.get())['parking']
            a = False
        elif parking in ['N', 'No']:
            parking = 0
            a = False
        else:
            out_message("Please enter correctly (Yes/No)")

    await guest_query.insert(fullname, count, passport, phone, nutrition, parking)
    out_message("Guest added")


async def add_room():

    a = True

    while a:
        number = input("Enter the room number: ")
        if number == "..":
            return
        if number.isdigit():
            a = False

        else:
            out_message("Incorrect room number")

    a = True

    while a:
        count = input("Enter number of beds: ")
        if count == "..":
            return
        if count.isdigit():
            a = False

        else:
            out_message("Incorrect number of beds")

    a = True

    while a:
        status = input("Enter the room status (Working/Closed)")
        if status == "..":
            return
        if status.lower() in ['working', 'closed']:
            a = False
                                        
        else:
            out_message("Incorrect data entered")

    a = True

    while a:
        tp = input("Enter the room type (Economy/Standard/Standard +/Semiluxe/Luxe): ")
        if tp == "..":
            return
        if tp.lower() in ["economy", "standard", "standard +", "semiluxe", "luxe"]:
            a = False

        else:
            out_message("Incorrect data entered")

    a = True

    while a:
        cost = input("Enter the price per room: ")
        if cost == "..":
            return
        if cost.isdigit():
            a = False

        else:
            out_message("Incorrect price entered")

    await room_query.insert(number, count, status.lower(), tp.lower(), cost)
    out_message("Room added")


async def search_guest():

    a = True

    while a:

        out_message("Selection:\n1 - by ID\n2 - by full name")
        num = input("Select the action you want to search for the guest by: ")

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
                    out_message("Action not found")

        else:
            out_message("Invalid action number")

async def search_guest_by_id():
    a = True

    while a:
        guest_id = input("Enter guest ID: ")
        
        if guest_id.isdigit():
            guest = await guest_query.get(int(guest_id))
            a = False

        else:
            out_message("Invalid guest ID")

    if not guest:
        out_message("Results not found")
        return
    
    out_message(f"Search results (1)\n\nID: {guest.guest_id}\nFull name: {guest.fullname}")

async def search_guest_by_fullname():

    guest_fullname= input("Enter full name: ")
    guests = await guest_query.get_all_by_fullname(guest_fullname)

    if not guests:
        out_message("No results found")
        return
    
    result = "\n\n".join(f"Search results({len(guests)})\nID: {i.guest_id}\nFull name: {i.fullname}" for i in guests)
    out_message(result)


async def search_room():
    a = True
    
    while a:

        out_message("Selection:\n1 - by Number\n2 - by Status\n3 - by Type")
        num = input("Select an action to search for room: ")

        if num == "..":  # add a function exit command ".."
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
                    out_message("Action not found")

        else:
            out_message("Invalid action number")

async def search_room_by_number():
    a = True

    while a:
        room_num = input("Enter room number: ")
        
        if room_num.isdigit():
            room = await room_query.get_by_number(int(room_num))
            a = False

        else:
            out_message("Invalid room number")

    if not room:
        out_message("No results found")
        return
    
    out_message(f"Search Results(1)\n\nID: {room.room_id}\nStatus: {room.status}\nCost: {room.cost}")

async def search_room_by_status():
    
    room_status = input("Enter the status: ")
    rooms = await room_query.get_by_status(room_status)

    if not rooms:
        out_message("No results found")
        return
    
    result = "\n\n".join(f"Search Results({len(rooms)})\nID: {i.room_id}\nStatus: {i.status}\nCost: {i.cost}" for i in rooms)
    out_message(result)


async def search_room_by_type():
    
    room_type = input("Enter the type: ")
    rooms = await room_query.get_by_status(room_type.lower())

    if not rooms:
        out_message("No results found")
        return
    
    result = "\n\n".join(f"Search Results({len(rooms)})\nID: {i.room_id}\nStatus: {i.status}\nCost: {i.cost}" for i in rooms)
    out_message(result)


async def edit_guest():

    while True:

        out_message("Selection:\n1 - by ID\n2 - by Full name\n.. - exit function")
        num = input("Select an action to edit the guest: ")

        if num.isdigit():
            match int(num):

                case 1:
                    await edit_guest_by_id()
                    break

                case 2:
                    await edit_guest_by_fullname()
                    break

                case _:
                    out_message("Action not found")

        elif num == "..":
            return

async def edit_guest_by_id():

    while True:
        guest_id = input("Enter guest ID: ")

        if guest_id.isdigit():
            guest = await guest_query.get(int(guest_id))
            break

        elif guest_id == '..':
            return

        else:
            out_message("Invalid guest ID")



    while True:
        out_message("Actions:\n1 - Change full name\n2 - Change phone number\n3 - Change passport info\n.. - exit function")
        action = input("Select what you want to change: ")

        if action.isdigit():
            
            match int(action):

                case 1:
                    fullname = input("Enter full name: ")
                    await guest_query.update_fullname_by_id(guest.guest_id, fullname)
                    out_message("Guest's full name has been changed")

                case 2:
                    phone = input("Enter phone number: ")
                    await guest_query.update_phone_by_id(guest.guest_id, phone)
                    out_message("Guest's phone number has been changed")

                case 3:
                    passport = input("Enter passport info in format(SSSS NNNNNNNN): ")
                    await guest_query.update_passport_by_id(guest.guest_id, passport)
                    out_message("Guest's passport info has been changed")

                case _:
                    out_message("Action not found")

        elif action == '..':
            return

        else:
            out_message("Action not found")

async def edit_guest_by_fullname():

    while True:
        guest_fullname = input("Enter guest's full name: ")

        if guest_fullname == "..":
            return

        guest = await guest_query.get_by_fullname(guest_fullname)

        if guest is not None:
            break

        else:
            out_message("Guest not found")



    while True:
        out_message("Actions:\n1 - Edit full name\n2 - Edit phone number\n3 - Edit passport data\n.. - Exit function")
        action = input("Choose what you want to change: ")

        if action.isdigit():
            
            match int(action):

                case 1:
                    fullname = input("Enter full name: ")
                    await guest_query.update_fullname_by_fullname(guest.fullname, fullname)
                    out_message("Guest's full name has been updated")

                case 2:
                    phone = input("Enter phone number: ")
                    await guest_query.update_phone_by_fullname(guest.fullname, phone)
                    out_message("Guest's phone number has been updated")

                case 3:
                    passport = input("Enter passport data in format (SSSS NNNNNNN): ")
                    await guest_query.update_passport_by_fullname(guest.fullname, passport)
                    out_message("Guest's passport data has been updated")

                case _:
                    out_message("Action not found")

        elif action == "..":
            return

        else:
            out_message("Action not found")


async def add_resident():  
    a = True

    while a:
        guest_id = input("Enter guest ID: ")
        
        if guest_id == "..":
            return

        if guest_id.isdigit():
            guest = await guest_query.get(int(guest_id))
            if guest:
                guest_id = guest.guest_id
                a = False

            else:
                out_message("Guest not found for this ID")

        else:
            out_message("Invalid guest ID format")

    a = True

    while a:
        room_id = input("Enter room ID: ")
        if room_id == "..":
            return

        if room_id.isdigit():
            room = await room_query.get(int(room_id))
            if room:
                if room.count >= guest.count:
                    room_id = room.room_id
                    a = False

                else:
                    out_message(f"Room is not designed for this number of residents. Number of places: {room.count}, number of residents: {guest.count}")


            else:
                out_message("Room not found for this ID")

        else:
            out_message("Invalid room ID format")

    a = True

    while a:
        date_start = input("Enter check-in date in format (DD.MM.YYYY): ")
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
                        out_message("The room is busy for this period")
                        return

                else:
                    out_message("Date must consist of numbers. Format: DD.MM.YYYY")

            else:
                out_message("Incorrect date format. Format: DD.MM.YYYY")

        else:
            out_message("Incorrect date format. Format: DD.MM.YYYY")

    a = True

    while a:
        date_end = input("Enter check-out date in format (DD.MM.YYYY): ")
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
                        out_message("Check-out date cannot be less than/equal to check-in date")

                else:
                    out_message("Date must consist of numbers. Format: DD.MM.YYYY")

            else:
                out_message("Incorrect date format. Format: DD.MM.YYYY")

        else:
            out_message("Incorrect date format. Format: DD.MM.YYYY")

    await resident_query.insert(guest_id, room_id, date_start, date_end)
    delta: timedelta = date_end - date_start
    price = delta.days*room.cost - delta.days*room.cost*discount + delta.days*guest.parking + delta.days*guest.nutrition_breakfast + delta.days*guest.nutrition_all
    out_message(f"Record of residence added for guest with ID: {guest_id} in room with ID: {room_id}.")
    out_message(f"Total price: {price}")
    if discount > 0:
        out_message(f"Discount: {discount*100}%")


async def hotel_settings():
    
    a = True

    while a:
        out_message("Select action:\n1 - Change hotel name\n2 - Change breakfast cost\n3 - Change \"All inclusive\" cost\n4 - Change parking cost")
        num = input()

        if num.isdigit():
            
            match int(num):

                case 1:
                    name = input("Enter new hotel name: ")
                    if name == '..':
                        break
                
                    await hotel_query.update_name(name)
                    out_message("Hotel name has been updated")



                case 2:
                    while a:
                        price = input("Enter new breakfast cost: ")
                        if price == "..":
                            break

                        elif price.isdigit():
                            await hotel_query.update_nutrition_breakfast(price)
                            out_message("Cost of breakfast updated")
                            break
                        

                        else:
                            out_message("Invalid cost format")

                case 3:
                    while a:
                        price = input("Enter new \"All inclusive\" cost: ")
                        if price == "..":
                            break

                        elif price.isdigit():
                            await hotel_query.update_nutrition_all(price)
                            out_message("Cost of \"All inclusive\" updated")
                            break
                        

                        else:
                            out_message("Invalid cost format")

                case 4:
                    while a:
                        price = input("Enter new parking cost: ")
                        if price == "..":
                            break

                        elif price.isdigit():
                            await hotel_query.update_parking(price)
                            out_message("Parking cost updated")
                            break
                        

                        else:
                            out_message("Invalid cost format")

                case _:
                    out_message("Action not found")

        elif num == "..":
            return

        else:
            out_message("Incorrect action number")

async def search_rooms():
    
    a = True

    while a:
        today = datetime.today()
        free, busy = await room_query.get_free_room(today)

        out_message("Free rooms for today:\n" + '\n'.join(f"ID: {i.room_id}\nRoom number: {i.number}\nPrice: {i.cost}" for i in free), Fore.GREEN)
        out_message("Busy rooms for today:\n" + '\n'.join(f"ID: {i.room_id}\nRoom number: {i.number}\nPrice: {i.cost}" for i in busy), Fore.RED)
        a = False

async def search_resident():
    a = True

    while a:
        out_message("Choose an action:\n1 - by date\n2 - by room number")
        num = input()
        if num == "..":
            return

        elif num.isdigit():
            
            match int(num):

                case 1:
                    while a:
                        date = input("Enter date in format(DD.MM.YYYY): ")
                        if date == "..":
                            return

                        date_obj = date.split(".")
                        if len(date_obj) == 3:
                            if len(date_obj[0]) == 2 and len(date_obj[1]) == 2 and len(date_obj[2]) == 4:
                                if date_obj[0].isdigit() and date_obj[1].isdigit() and date_obj[2].isdigit():
                                    date = datetime(int(date_obj[2]), int(date_obj[1]), int(date_obj[0]))
                                    free, busy = await room_query.get_free_room(date)
                                    out_message("Free rooms: "+ "\n".join(f"ID: {i.room_id}\nRoom Number: {i.number}\nCost: {i.cost}" for i in free))
                                    break
                                

                                else:
                                    out_message("Date should consist of numbers. Format: DD.MM.YYYY")

                            else:
                                out_message("Incorrect date format. Format: DD.MM.YYYY")

                        else:
                            out_message("Incorrect date format. Format: DD.MM.YYYY")

                case 2:
                    num = input("Enter room number: ")
                    if num == "..":
                        return
                    
                    if num.isdigit():
                        r = await resident_query.get_by_room_number(num)
                        if not r:
                            out_message("Room not found")
                        
                        out_message(f"Room #{num}\nCheck-in | Check-out" + "\n".join(f"{i.date_start.strftime('%d.%m.%Y')} | {i.date_end.strftime('%d.%m.%Y')}" for i in r))

                    else:
                        out_message("Room number entered incorrectly")

                case _:
                    out_message("Action not found")

        else:
            out_message("Incorrect action entered")

def console_settings():
    
    out_message("Choose color schemes:\n1 - dark green background and black text\n2 - green background and white text\n3 - white background and black text\n4 - white background and dark blue text\n5 - dark blue background and white text")
    
    while True:
        schema = input("")

        if schema == '..':
            break

        elif schema.isdigit():
            
            match int(schema):

                case 1:
                    update_color_schema(1)
                    out_message("Color updated")
                    break

                case 2:
                    update_color_schema(2)
                    out_message("Color updated")
                    break

                case 3:
                    update_color_schema(3)
                    out_message("Color updated")
                    break

                case 4:
                    update_color_schema(4)
                    out_message("Color updated")
                    break

                case 5:
                    update_color_schema(5)
                    out_message("Color updated")
                    break

                case _:
                    print("Number not found")

        else:
            print("Action not found")

async def main():
    while True:
        if await logging():
            os.system(f"title {(await hotel_query.get())['name']}")
            os.system(f"cls")
            out_message(f"Hotel: {(await hotel_query.get())['name']}")
            out_message(f"Occupied rooms: {len(await resident_query.busy_rooms())}, free rooms: {len(await room_query.all_rooms()) - len(await resident_query.busy_rooms())}")
            out_message(f"Currently staying at the hotel: {await resident_query.get_resident()}")
            out_message("\n\n")

            while True:
                
                out_message("Choose command: \n\n1 - Add guest\n2 - Add room\n3 - Add resident record\n4 - Edit guest\n5 - Search guest\n6 - Search room\n7 - List of rooms\n8 - Search by residence\n9 - Hotel settings\n10 - Console color scheme settings")
                num = input("Enter number: ")
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
                            out_message("Action not found")

                else:
                    out_message("Action number should be a number")


