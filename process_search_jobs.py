import argparse
from datetime import datetime
from job_queue import JobQueue

parser = argparse.ArgumentParser()

airdate = datetime.now()
queue = JobQueue.load_from_cache()
queue.perform_searches(datetime(month=airdate.month, day=airdate.day, year=airdate.year))