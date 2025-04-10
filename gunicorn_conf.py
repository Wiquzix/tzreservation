bind = "0.0.0.0:8000"
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
reload = True
loglevel = "debug"
accesslog = "-"
errorlog = "-" 