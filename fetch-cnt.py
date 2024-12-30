# 定时统计图书馆的人数，并存储到数据库中

import requests
from bs4 import BeautifulSoup
import time
import mysql.connector
import configparser # 读取配置文件

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 设置数据库连接
DB_HOST = config['database']['host']
DB_USER = config['database']['user']
DB_PASSWORD = config['database']['password']
DB_DATABASE = config['database']['database']
DB_PORT = int(config['database']['port'])
DB_CHARSET = config['database']['charset']

REQUSET_URL = config['network']['url']

TABLE_NAME = config['table']['name']
TARGET_DIV_CLASS = config['network']['target-class']
LIB_CLOSED = config['network']['lib-closed']

LIB_NAME = config['table']['lib-name']
LIB_PPL_CUR = config['table']['lib-ppl-cur']
LIB_PPL_MAX = config['table']['lib-ppl-max']
TIMESTAMP = config['table']['timestamp']

# 数据库配置
DB_CONFIG = {
    'host': DB_HOST,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'database': DB_DATABASE,
    'port': DB_PORT,
    'charset': DB_CHARSET
}

# 向网页发送请求
def fetch_data():
    try:
        r = requests.get(REQUSET_URL)
        r.raise_for_status()
        return r.text
    except requests.RequestException as e:
        print(e)
        return None
    
# 解析网页
def parse_data(html):
    soup = BeautifulSoup(html, 'html.parser')

    # 先找到目标 div 标签
    target_div = soup.find('div', class_=TARGET_DIV_CLASS)

    if not target_div:
        print('target div not found')
        return None
    
    divs = target_div.find_all('div') # 找到所有的 div 标签，每个 div 包含的 section 代表一个图书馆

    sections = []

    for div in divs:
        sections.append(div.find('section')) # 只需要第一个 section 标签

    # 调试
    # print(sections)

    # 遍历每个 section 标签，获取图书馆的人数
    lib_data = []   # 存储每个图书馆的人数

    for section in sections:
        # print(section)

        # 获取图书馆名称
        lib_name = section.find('span', class_='where').text.strip()

        # 获取人数
        ppl_cnt = section.find('label', class_='focus').text.strip()
        if ppl_cnt == LIB_CLOSED: # 如果已经闭馆，则不记录
            continue
        else:
            ppl_cnt = int(ppl_cnt)

        # 获取最大容纳人数
        max_cnt = 0 # 最大容纳人数
        # 先找所有的 label 标签
        labels = section.find_all('label')
        for label in labels:
            if not label.get('class'):
                # 去掉文字中开头的 /，如 原来是 /3600，现在是 3600
                max_cnt = int(label.text.strip()[1:])
                break
        
        # 存储数据
        lib_data.append({
            'lib_name': lib_name,
            'ppl_cnt': ppl_cnt,
            'max_cnt': max_cnt
        })

    return lib_data

# 存储数据
def store_data(lib_data):
    # 连接数据库
    db = mysql.connector.connect(**DB_CONFIG)
    cursor = db.cursor()

    # 获取当前时间
    now = time.strftime('%Y-%m-%d %H:%M:%S')

    # 遍历每个图书馆的数据
    for data in lib_data:
        lib_name = data['lib_name']
        ppl_cnt = data['ppl_cnt']
        max_cnt = data['max_cnt']

        # 插入数据（不包含自增ID）
        sql = f"INSERT INTO {TABLE_NAME} ({LIB_NAME}, {LIB_PPL_CUR}, {LIB_PPL_MAX}, {TIMESTAMP}) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (lib_name, ppl_cnt, max_cnt, now))

    # 提交数据
    db.commit()

    # 关闭数据库
    cursor.close()
    db.close()


# 主函数
def main():
    html = fetch_data()

    # print("got html")
    # print(html)

    if html:
        lib_data = parse_data(html)

        print("request success")

        # 调试
        print(lib_data)

        store_data(lib_data)

    else:
        print("request failed")

if __name__ == '__main__':
    main()