import threading
import time
def sourcing():
    for i in range(1,21):
        print(f"i am sourcing {i}")
    print("Quarter operations complete : " + sourcing.__name__)
    time.sleep(1) 
def producing():
    for i in range(1,21):
        print(f"i am producing {i}")
    print("Quarter operations complete : " + producing.__name__)
    time.sleep(1)  
producing_thread = threading.Thread(target=producing)
sourcing_thread = threading.Thread(target=sourcing)
producing_thread.start()
sourcing_thread.start()
producing_thread.join()
sourcing_thread.join()

         