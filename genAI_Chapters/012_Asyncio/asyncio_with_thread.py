import asyncio
from concurrent.futures import ThreadPoolExecutor
import time 

def produce(item):
    print(item)
    time.sleep(5)
    return ("over")
async def main():
    loop = asyncio.get_running_loop()  # jo bi jana event loop me chalne layak ya kam karne ke layak hai usku loop me dalo
    with ThreadPoolExecutor() as pool: # system se moauka(thread)
        result = await loop.run_in_executor(pool,produce,"pen") # woh jane ku kaam do with specification like target, mauka aur other stuff
        print(result)    
asyncio.run(main())            