from redis import Redis


def get_redis_list():
    redis = Redis(host='127.0.0.1', port=6379, password='')
    while True:
        text = redis.lpop('标题')
        if text is None:
            break
        else:
            print(text.decode('utf-8'))


if __name__ == '__main__':
    get_redis_list()
