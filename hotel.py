from mysql import MySQL
from dataclasses import dataclass
from datetime import datetime
from guest import Guest
from typing import List


class HotelQuery(MySQL):


    async def get(self):
        self.cursor("SELECT * FROM Settings")
        return await self.fetchone()
    
    async def update_name(self, name: str):
        self.cursor("UPDATE Settings SET name = %s", (name, ))
        await self.commit()

    async def update_nutrition_breakfast(self, price: int):
        self.cursor("UPDATE Settings SET nutrition_breakfast = %s", (price, ))
        await self.commit()

    async def update_nutrition_all(self, price: int):
        self.cursor("UPDATE Settings SET nutrition_all = %s", (price, ))
        await self.commit()

    async def update_parking(self, price: int):
        self.cursor("UPDATE Settings SET parking = %s", (price, ))
        await self.commit()

    async def logging_user(self, user: str, password: str):
        self.cursor("SELECT * FROM Users WHERE name = %s AND password = %s", (user, password))
        r = await self.fetchone()

        if not r:
            return None
        
        return r
           



class RoomQuery(MySQL):
    

    async def insert(self, number: int, count: int, status: str, types: str, cost: float):
        self.cursor("INSERT INTO Room(number, count, status, types, cost) VALUES(%s, %s, %s, %s, %s)", 
                    (number, count, status, types, cost))
        
        await self.commit()

    async def get(self, room_id: int):
        self.cursor("SELECT * FROM Room WHERE room_id = %s", (room_id, ))
        r = await self.fetchone()
        if not r:
            return None
        
        return Room(**r)
    
    
    async def get_by_number(self, number: int):
        self.cursor("SELECT * FROM Room WHERE number = %s", (number, ))
        r = await self.fetchone()
        if not r:
            return None
        
        return Room(**r)
    
    async def all_rooms(self) -> "Room":
        self.cursor("SELECT * FROM Room")
        r = await self.fetchall()
        
        return [Room(**i) for i in r]
    
    async def get_by_status(self, status: str):
        self.cursor("SELECT * FROM Room WHERE status = %s", (status, ))
        r = await self.fetchall()
        if not r:
            return None
        
        return [Room(**i) for i in r]

    async def get_by_type(self, types: str):
        self.cursor("SELECT * FROM Room WHERE types = %s", (types, ))
        r = await self.fetchall()
        if not r:
            return None
        
        return [Room(**i) for i in r]
    
    async def get_free_room(self, today: datetime) -> List[List["Room"]]:
        free = []
        busy = []
        self.cursor("SELECT * FROM Room")

        r = await self.fetchall()
        for i in r:
            self.cursor("SELECT * FROM Resident WHERE date_end < %s AND date_start > %s AND room_id = %s", (today, today, i['room_id']))
            if not await self.fetchone():
                free.append(Room(**i))

            else:
                busy.append(Room(**i))

        return free, busy
            


class ResidentQuery(MySQL):


    async def insert(self, guest_id: int, room_id: int, date_start: datetime, date_end: datetime):
        self.cursor("INSERT INTO Resident(guest_id, room_id, date_start, date_end) VALUES(%s, %s, %s, %s)",
                    (guest_id, room_id, date_start, date_end))
        
        await self.commit()

    async def remove(self, guest_id: int):
        self.cursor("DELETE FROM Resident WHERE guest_id = %s", (guest_id, ))
        await self.commit()

    async def get(self, guest_id: int) -> "Resident":
        self.cursor("SELECT * FROM Resident WHERE guest_id = %s", (guest_id, ))
        r = await self.fetchone()
        if not r:
            return None
        
        return Resident(**r)
    
    async def get_by_room_number(self, room_number: int):
        self.cursor("SELECT * FROM Room WHERE number = %s", (room_number, ))
        r = await self.fetchone()
        if not r:
            return None
        
        self.cursor("SELECT * FROM Resident WHERE room_id = %s", (r['room_id']))
        response = await self.fetchall()

        if not response:
            return None
        
        return [Resident(**i) for i in response]

    async def get_resident(self):
        count = 0
        self.cursor("SELECT * FROM Resident")
        r = await self.fetchall()
        for i in r:
            self.cursor("SELECT count FROM Guests WHERE guest_id = %s", (i['guest_id'], ))
            count += (await self.fetchone())['count']

        return count

    async def busy_rooms(self) -> "Resident":
        self.cursor("SELECT * FROM Resident")
        r = await self.fetchall()

        return [Resident(**i) for i in r]

            
    
    async def is_busy(self, room_id: int) -> bool:
        self.cursor("SELECT * FROM Resident WHERE room_id = %s", (room_id, ))
        r = await self.fetchone()
        return False if not r else True
    
    async def is_busy_by_date(self, date_start: datetime, room_id: int):
        self.cursor("SELECT * FROM Resident WHERE date_end >= %s AND room_id = %s", (date_start, room_id))
        r = await self.fetchall()
        if not r:
            return False
        
        return True
    
    
    async def get_by_room_id(self, room_id: int) -> "Resident":
        self.cursor("SELECT * FROM Resident WHERE room_id = %s", (room_id, ))
        r = await self.fetchone()
        if not r:
            return None
        
        return Resident(**r)
    

@dataclass
class Hotel:
    pass


@dataclass
class Room:
    
    room_id: int
    number: int
    count: int
    status: str
    types: str
    cost: float

@dataclass
class Resident:
    
    guest_id: int
    room_id: int
    date_start: datetime
    date_end: datetime