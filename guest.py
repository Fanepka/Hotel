from mysql import MySQL
from dataclasses import dataclass


class GuestQuery(MySQL):

    
    async def insert(self, fullname: str, count: int, passport: str, phone: str, nutrition: int, parking: int):
        self.cursor("INSERT INTO Guests(fullname, count, passport, phone, nutrition, parking) VALUES(%s, %s, %s, %s, %s, %s)", 
                    (fullname, count, passport, phone, nutrition, parking))
        
        await self.commit()

    async def remove(self, guest_id: int):
        self.cursor("DELETE FROM Guests WHERE id = %s", (guest_id, ))
        await self.commit()

    async def get(self, guest_id: int) -> "Guest":

        self.cursor("SELECT * FROM Guests WHERE guest_id = %s", (guest_id, ))
        r = await self.fetchone()
        if not r:
            return None
        
        return Guest(**r)
    
    async def get_by_fullname(self, fullname: str) -> "Guest":

        self.cursor("SELECT * FROM Guests WHERE fullname = %s", (fullname, ))
        r = await self.fetchone()
        if not r:
            return None
        
        return Guest(**r)
    
    async def get_all_by_fullname(self, fullname: str):
        
        self.cursor("SELECT * FROM Guests WHERE fullname = %s", (fullname, ))
        r = await self.fetchall()
        if not r:
            return None
        
        return [Guest(**i) for i in r]
    
    
    async def update_fullname_by_id(self, guest_id: int, fullname: str):
        self.cursor("UPDATE Guests SET fullname = %s WHERE guest_id = %s", (guest_id, fullname))
        await self.commit()

    async def update_phone_by_id(self, guest_id: int, phone: str):
        self.cursor("UPDATE Guests SET phone = %s WHERE guest_id = %s", (guest_id, phone))
        await self.commit()
    
    async def update_passport_by_id(self, guest_id: int, passport: str):
        self.cursor("UPDATE Guests SET passport = %s WHERE guest_id = %s", (guest_id, passport))
        await self.commit()

    async def update_fullname_by_fullname(self, fullname: str, new_fullname: str):
        self.cursor("UPDATE Guests SET fullname = %s WHERE fullname = %s", (fullname, new_fullname))
        await self.commit()

    async def update_phone_by_fullname(self, fullname: str, phone: str):
        self.cursor("UPDATE Guests SET phone = %s WHERE fullname = %s", (fullname, phone))
        await self.commit()
    
    async def update_passport_by_fullname(self, fullname: str, passport: str):
        self.cursor("UPDATE Guests SET passport = %s WHERE guest_id = %s", (fullname, passport))
        await self.commit()


@dataclass
class Guest:
    
    guest_id: int
    fullname: str
    count: int
    passport: str
    phone: str | int
    nutrition_breakfast: int
    nutrition_all: int
    parking: int
