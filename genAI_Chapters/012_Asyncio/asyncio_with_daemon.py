import asyncio
import threading
import time

def runner():
    while True :
        print("began")
        time.sleep(1)
        print("end")
    

async def main():
    await asyncio.sleep(3)
    print("order from main")
threading.Thread(target=runner,daemon =True).start()        
    
asyncio.run(main())    