# Import FastAPI class to create the web application
# Query is used to define and validate query parameters from the URL
from fastapi import FastAPI, Query
# NOTE rq worker --worker-class rq.worker.SimpleWorker to use server in windows
# Import the Redis Queue (RQ) object
# This queue is responsible for sending jobs to the background worker jo LLM model hai 
from client_line.rq import q

# Import the function that the worker will execute
# Instead of processing inside FastAPI, this function runs in the worker process
from worker_line.worker import process_runner


# Create an instance of the FastAPI application
# Everything (routes, middleware, docs, etc.) is attached to this object
app = FastAPI()


# GET endpoint
# Runs when someone opens:
# http://localhost:8000/
@app.get('/')
def root():

    # Return a simple string showing that the server is running
    return "status : server on board"


# POST endpoint
# Runs when a POST request is sent to:
# http://localhost:8000/chat
@app.post('/chat')
def chat(

    # Create a required query parameter named "user_query"
    # Query(...) means this value is mandatory and has  to filled 
    # description is shown in Swagger UI documentation - "the chat query of user"
    user_query: str = Query(
        ...,
        description="the chat query of user"
    )
):

    # Send a background job to Redis Queue
    #
    # q.enqueue(
    #     function_to_execute, - process_runner
    #     arguments_for_function - user_query jo further banjari "process_runner(user_query)"
    # )
    #
    # IMPORTANT:
    # This DOES NOT execute the function immediately.
    # It simply stores the job inside Redis. (abi bas line me khade kara, kaam karke nai diya server)
    # A separate Worker process will pick it up later.
    job = q.enqueue(process_runner, user_query)

    # Immediately return the job ID
    # Client can use this ID later to check the result - not a real life example magar har app cache me rakti id
    return {
        "status": "queued",
        "job_id": job.id
    }


# GET endpoint
# Used to retrieve the result of a previously submitted job
#
# Example:
# /job-result?job_id=abcd123
@app.get('/job-result')
def result(

    # Required query parameter mane id diye toh ich function kam karinga
    # User must provide the Job ID
    job_id: str = Query(
        ...,
        description="the job id"
    )
):

    # Search Redis Queue using the provided Job ID
    # If found, it returns the Job object
    job = q.fetch_job(job_id=job_id) # checks whether the job id present in queue, returns job object with all included properties or if not, returns none

    # Get the value returned by process_runner()
    #
    # If the worker has not finished yet,
    # this may return None.
    result = job.return_value()

    # Return the final processed result
    return {
        "result": result
    }