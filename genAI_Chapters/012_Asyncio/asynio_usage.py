import asyncio as asy

# jab paramount run hua, toh ander bond(casino royale) run hua, ye begin hua then next line me await dekhliya apna thread, 
# aur event loop ke queue me jage dediya casino royal ke coroutine ku ki jab apka await return kare which is 10 sec sleep toh ap run hosakte
# phir unne 2 kadam piche aake second wala : bond("no time to die") run kara aur usme bi unne await dekhliya, event loop ke 
# queue me jage dediya no time to die ke coroutine ku ki jab apka await return kare which is 10 sec sleep toh ap run hosakte. 
# ye halt yahan bi dekke phirse doh kadam piche aur dekha ki spectre ka bond run karna hai, 
# aur uske ander bi asy.sleep dikha aur unne phirse pehele ke jaise 2 kadam piche and skyfall kholdiya, 
# yahan bi nirashaa aur atlast jab first wala: casino royal ka sleep end hua, 
# toh event loop usku system me jagae diya to run jo print kara casino royale aur aisa no time to die ka sleep end hua toh usku bi thread diya gaya,
# aur unne bi run hua {no time to die is over} aur ye silsila khtam hua when skyfall ka timer end hone pe "skyfall over" print hua

async def bond(movie):
    print(f"{movie} began")
    await asy.sleep(10)
    print(f"{movie} over")
async def paramount():
    await asy.gather(
        bond("casino Royale"),
        bond("no time to die"),
        bond("spectre"),
        bond("skyfall"),
    )  
asy.run(paramount())    
      
    
    