# Django Q
##A multiprocessing task queue application for Django
### Status
In Alpha and Python 3 only (for now).
Everything should work, but the basic structure can still change.
Main focus will be put on creating tests now.


### Architecture
![Django Q schema](http://i.imgur.com/wTIeg2T.png) 

### Usage
Schedule the asynchronous exectution of a function by calling `async` from within your Django project.

```python
async(func,*args,hook=None,**kwargs)
```
The optional hook function gets the finished task object as its first argument after execution

### Management commands

#### `qcluster`
Start a cluster with `./manage.py qcluster`

####`qmonitor`
You can monitor basic information about all the connected clusters by running  `./manage.py qmonitor`

###Admin integration
Django Q registers itself with the admin page to show failed and succesful tasks.
From there task results can be read or deleted. If neccesary, failed tasks can be reintroduced to the queue.

### Signed Tasks
Tasks are first pickled to Json and then signed using Django's own signing module before being sent to a Redis list. This ensures that task packages on the Redis server can only be excuted and read by clusters and django servers who share the same secret key. 

Optionally, packages can be compressed before transport by setting `Q_COMPRESSED = True `

### Pusher
The pusher process continously checks the Redis list for new task packages and pushes them on the Task Queue.

### Worker
A worker process checks the package signing, unpacks the task, executes it and saves the return value. Irrespective of the failure or success of any of these steps, the package is then pushed onto the Result Queue. 

By default Django Q spawns a worker for each detected CPU on the host system.
This can be overridden by setting `Q_WORKERS =  n`. With *n* being the numbe of desired worker processes.

### Monitor
The result monitor checks the Result Queue for processed packages and saves both failed and succesful packages to the Django database.

By default only the last 100 succesful packages are kept in the database.
This can be increased or decreased at will by settings `Q_SAVE_LIMIT = n`. With *n* being the desired number of records. 
Set `Q_SAVE_LIMIT = 0` to save all results to the database.
Failed packages are always saved.

### Sentinel

The sentinel spawns all process and then checks the health of all workers, including the pusher and the monitor. Reincarnating processes if any may fail.
In case of a stop signal, the sentinel will halt the pusher and instruct the workers and monitor to finish the remaining items , before exiting.

### Hooks

Packages can be assigned a hook function, upon completion of the package this function will be called with the Task object as the first argument.

### Todo
I'll add to this README while I'm developing the various parts.