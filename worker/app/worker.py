from opsbox_common.settings import QUEUE_NAME, REDIS_URL
from redis import Redis
from rq import Queue, Worker


def main():
    conn = Redis.from_url(REDIS_URL)
    q = Queue(QUEUE_NAME, connection=conn)
    w = Worker([q], connection=conn)
    w.work(with_scheduler=True)


if __name__ == "__main__":
    main()
