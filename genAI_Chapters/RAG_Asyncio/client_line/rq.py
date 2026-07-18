from redis import Redis
from rq import Queue

queue_connect = Redis(host="localhost",port=6379) # connecting the properties and host to queue
q = Queue(connection=queue_connect) # connection established

 

