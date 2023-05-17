import asyncio
import ru
import en

from utils import open_json



if __name__ == "__main__":
    while True:
        file = open_json('data/config.json')
        if file[2]['language'] == 'ru':
            asyncio.run(ru.main())
                        
        else:
            asyncio.run(en.main())

    