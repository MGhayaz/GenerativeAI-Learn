from multiprocessing import Process , Queue
import time
def activ_irshard(queue):
    queue.put("Mentor")

if(__name__ == "__main__"):
    p = []
    queue = Queue()
    start = time.time()
    for i in range (3) :
        p1 = Process(target = activ_irshard, args =(queue,))
        p.append(p1)
    for p1 in p :    
        p1.start()
    for p1 in p :    
        p1.join()
    end = time.time()    
    print(queue.get())
    print(f"{end - start:.2f}")
    