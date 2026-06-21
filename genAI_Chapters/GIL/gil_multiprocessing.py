import time 
from multiprocessing import Process
def produce():
# more process == less time and more productivity but such gil is not used often    
    runner = 0
    print(f"kaam chalu huaa")
    for _ in range (1000_000_00):
        runner = runner+1
    print(f"kaam khatam huaa")

if __name__ == "__main__":
      
    alpha = Process(target=produce)
    psi = Process(target=produce)

    start = time.time()
    alpha.start()
    psi.start()
    alpha.join()
    psi.join()
    end = time.time()
    print(f"production exit within {end-start:.2f}")        
        