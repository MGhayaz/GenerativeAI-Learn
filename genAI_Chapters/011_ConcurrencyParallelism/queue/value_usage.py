from multiprocessing import Process , Value
import time
def activ_irshard(irshard_Bhai):
    for _ in range (30000):
        with irshard_Bhai.get_lock():
            irshard_Bhai.value+=1

if (__name__ == "__main__"):
    p = []
    irshard_Bhai = Value("i",0)
    start = time.time()
    for i in range (10) :
        p1 = Process(target = activ_irshard, args =(irshard_Bhai, ))
        p.append(p1)
    for p1 in p :    
        p1.start()
    for p1 in p :    
        p1.join()
    end = time.time()    
    print(irshard_Bhai.value)
    print(f"{end - start:.02f}")
    