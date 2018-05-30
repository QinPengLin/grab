# coding=utf-8
import random
import string


def random_string(length, char_pool=string.ascii_letters + string.digits):
    """
    生成随机字符串
    :param int length:
    :param str char_pool:
    :return:
    """
    return ''.join(random.choice(char_pool) for _ in range(length))

def cookiejar_to_json(cookiejar):
    """
    将cookie转成dict
    :param CookieJar cookiejar:
    :return:
    """
    cookies = []
    for cookie in iter(cookiejar):
        print cookie
        cookies.append({
            'domain': cookie.domain,
            'path': cookie.path,
            'expires': cookie.expires,
            'name': cookie.name,
            'value': cookie.value
        })
    return cookies

def get_file_content(file_path):
    """
    读取文件
    :param file_path:
    :return:
    """
    _file = open(file_path)
    content = _file.read()
    _file.close()
    return content
