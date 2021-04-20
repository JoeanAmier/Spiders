import random


def retry(func):
    max_retry = 10

    def run():
        for i in range(max_retry):
            status_code = func()
            if status_code == 200:
                return f'第{i + 1}次访问 ' + str(status_code) + ' 访问成功！'
            else:
                print(f'第{i + 1}次访问', status_code, '重试中！')
        return '访问失败！'

    return run


@retry
def requests():
    return random.choice([200, 404, 404, 404, 404])


def common():
    pass


def main():
    response = requests()
    print(response)
    print(requests)
    print(retry)
    print(common)


if __name__ == '__main__':
    main()
