import aiohttp
import asyncio as asy
import time
async def service(session, url):

        async with session.get(url) as resp:
            print(f"Status code : {resp.status}")

urls =  [
    "https://httpbin.org/delay/2",
    "https://httpbin.org/delay/3",
    "https://httpbin.org/delay/6"
]
            
async def main():
    async with aiohttp.ClientSession() as session:
          tasks = [service(session,url)for url in urls]
          await asy.gather(*tasks) # * use kare to traverse the list content
start =  time.time()          
asy.run(main())   
end = time.time()
print(f"{(end-start):.2f}")               