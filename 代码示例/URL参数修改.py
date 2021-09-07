from urllib.parse import urlparse, urlunparse, parse_qs, urlencode


def replace_field(url, name, value):
    parse = urlparse(url)  # 把网址转成  ParseResult  对象
    query = parse.query  # ParseResult  对象的.query  属性，是一个字符串，也就是网址中，问号后面的内容
    query_pair = parse_qs(query)  # 把 .query 输出的字符串转成字典
    query_pair[name] = value  # 修改值
    new_query = urlencode(query_pair, doseq=True)  # 把字段转成. query 形式的字符串
    new_parse = parse._replace(query=new_query)
    return urlunparse(new_parse)  # 把ParseResult对象转回网址字符串


url_list = [
    'https://xxx.com/articlelist?category=technology',
    'https://xxx.com/articlelist?category=technology&after=',
    'https://xxx.com/articlelist?category=technology&after=asdrtJKSAZFD',
    'https://xxx.com/articlelist?category=technology&after=asdrtJKSAZFD&other=abc'
]

for url in url_list:
    next_page = replace_field(url, 'after', '0000000')
    print(next_page)
