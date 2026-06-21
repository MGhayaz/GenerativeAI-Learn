import requests
import threading
import time

def download(url):
    print(f"working : {threading.current_thread().name}")
    resp = requests.get(url)
    print("imported")
    
urls = [
    "https://wallpapercave.com/wp/wp16407964.webp",
    "https://wallpapercave.com/uwp/uwp5050562.jpeg",
    "https://images.pexels.com/photos/29270283/pexels-photo-29270283.jpeg"
] 
start = time.time()
threads = []
for url in urls :
    t = threading.Thread(target=download, args=(url,), name= url)
    t.start()
    threads.append(t)
for t in threads :
    t.join()
print("all imported")        