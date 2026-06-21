from multiprocessing import Process
import time

def produce(parameter):
    print(f"[BEGIN] producing batch: {parameter}")
    time.sleep(5)
    print(f"[END] producing batch: {parameter}")
if (__name__ == "__main__"):
    l = []
    for i in range (4):
        p = Process(target=produce,args=(i+1,))
        l.append(p)
    for p in l :
        p.start()
    for p in l:
        p.join()    
    
       