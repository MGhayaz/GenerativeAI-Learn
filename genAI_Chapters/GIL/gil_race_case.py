import time 
import threading
runner = 0

# this situation is race case and is not thread safe, we can secure it with

#lock = threading.Lock()
def produce():
    global runner
    print(f"kaam chalu huaa by {threading.current_thread().name}")
    for _ in range (1000_000_00):
       # with lock :
            runner = runner+1
    print(f"kaam khatam huaa by {threading.current_thread().name}")

    
alpha_Thread = threading.Thread(target=produce,name="ALPHA_Irshard")
psi_Thread = threading.Thread(target=produce,name="psi_Asif")

start = time.time()
alpha_Thread.start()
psi_Thread.start()
alpha_Thread.join()
psi_Thread.join()
end = time.time()
print(f"production exit within {end-start:.2f}")        
        