# 定时统计图书馆的人数，并存储到数据库中

import requests # 发送请求
from bs4 import BeautifulSoup # 解析 HTML
import time # 时间相关的处理
import pytz # 时区
import mysql.connector # 数据库连接
import configparser # 读取配置文件
import logging # 日志
from logging.handlers import TimedRotatingFileHandler # 每天生成一个日志文件
import os
from datetime import datetime

# 读取配置文件
# 还是开全局变量更安全一些，C 语言的习惯
CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini', encoding='utf-8')

# 设置数据库连接
DB_HOST = CONFIG['database']['host']
DB_USER = CONFIG['database']['user']
DB_PASSWORD = CONFIG['database']['password']
DB_DATABASE = CONFIG['database']['database']
DB_PORT = int(CONFIG['database']['port'])
DB_CHARSET = CONFIG['database']['charset']

REQUSET_URL = CONFIG['network']['url']

TARGET_DIV_CLASS = CONFIG['network']['target-class']
LIB_CLOSED = CONFIG['network']['lib-closed']

TABLE_NAME = CONFIG['table']['name']
LIB_NAME = CONFIG['table']['lib-name']
LIB_PPL_CUR = CONFIG['table']['lib-ppl-cur']
LIB_PPL_MAX = CONFIG['table']['lib-ppl-max']
TIMESTAMP = CONFIG['table']['timestamp']

INFO_ADDR = CONFIG['log']['info_addr']
ERROR_ADDR = CONFIG['log']['err_addr']
ENCODING = CONFIG['log']['encoding']

TZ = pytz.timezone('Asia/Shanghai') # UTC+8 时区

# 数据库配置
DB_CONFIG = {
    'host': DB_HOST,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'database': DB_DATABASE,
    'port': DB_PORT,
    'charset': DB_CHARSET
}

# 配置日志
def setup_logger():
    # 确保日志目录存在
    os.makedirs(INFO_ADDR, exist_ok=True)
    os.makedirs(ERROR_ADDR, exist_ok=True)
    
    # 主日志配置
    logger = logging.getLogger('main')
    logger.setLevel(logging.INFO)
    
    # 日常日志文件
    daily_handler = TimedRotatingFileHandler(
        f'{INFO_ADDR}info.log',
        when='midnight',
        interval=1,
        backupCount=7,
        encoding = ENCODING
    )
    daily_handler.setLevel(logging.INFO)
    
    # 错误日志文件
    error_handler = TimedRotatingFileHandler(
        f'{ERROR_ADDR}error.log',
        when='midnight',
        interval=1,
        backupCount=7,
        encoding = ENCODING
    )
    error_handler.setLevel(logging.ERROR)
    
    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s\n%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    daily_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)
    
    logger.addHandler(daily_handler)
    logger.addHandler(error_handler)
    return logger

LOGGER = setup_logger()

# 向网页发送请求
def fetch_data():
    try:
        r = requests.get(REQUSET_URL)
        r.raise_for_status()
        return r.text
    except requests.RequestException as e: # 如果没成功的话，没关系，反正几分钟后还会再请求
        print(e)
        return None
    
# 解析网页
def parse_data(html):
    soup = BeautifulSoup(html, 'html.parser')

    # 先找到目标 div 标签
    target_div = soup.find('div', class_=TARGET_DIV_CLASS)

    if not target_div:
        print('未找到目标 div 标签')
        return None
    
    divs = target_div.find_all('div') # 找到所有的 div 标签，每个 div 包含的 section 代表一个图书馆
    # 就很烦，每个 section 是嵌入在 div 里的，所以要先找到 div，再找到 section

    sections = []

    for div in divs:
        sections.append(div.find('section')) # 只需要第一个 section 标签

    # 遍历每个 section 标签，获取图书馆的人数
    lib_data = []   # 存储每个图书馆的人数

    for section in sections:
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
def store_data(lib_data): # 每次都需要重新设置 logger，因为日期可能会变
    # 如果 lib_data 为空，则不存储
    if not lib_data:
        return
    
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

    # 记录日志
    log_msg = now + '\n' # 记录一下时间，系统时间可能和这个时间有一点点误差
    for data in lib_data:
        log_msg += f"{data['lib_name']}: {data['ppl_cnt']}/{data['max_cnt']}\n"
    log_msg += "\n"
    LOGGER.info(log_msg)

    # 关闭数据库
    cursor.close()
    db.close()


# 设置每次请求间歇的时间
# 如果在 7:30 到 22:30 之间，则每分钟请求一次；如果在 22:30 - 次日 1:30 之间，则每 5 分钟请求一次；否则每 15 分钟请求一次
def set_interval():
    DAYTIME_SLEEP = 60
    NIGHT_SLEEP = 300
    LATENIGHT_SLEEP = 900

    now = time.localtime()
    hour = now.tm_hour
    minute = now.tm_min
    current_minutes = hour * 60 + minute # 换算成分钟

    day_start = 7 * 60 + 30  # 7:30
    day_end = 22 * 60 + 30   # 22:30
    night_start = 1 * 60 + 30 # 1:30

    if current_minutes >= day_start and current_minutes < day_end: # 如果在 7:30 到 22:30 之间
        return DAYTIME_SLEEP
    elif current_minutes >= day_end or current_minutes < night_start: # 如果在 22:30 - 次日 1:30 之间
        return NIGHT_SLEEP
    else: # 1:30 到 7:30 之间
        return LATENIGHT_SLEEP
    

# 主函数
def main():
    while True: # 保持运行
        html = fetch_data()

        # print("got html")
        # print(html)

        if html:
            lib_data = parse_data(html)

            # print("request success")

            # 调试
            print(lib_data)

            store_data(lib_data)

        else:
            print("request failed")
     
        # 设置间歇
        interval = set_interval()
        time.sleep(interval)

if __name__ == '__main__':
    main()

'''
参考的 html 结构：
<div class="hmp wow fadeInUp">
    <!-- 生产环境需取消注释 -->
    <div>
    <section>
        <span class="where">四平路校区图书馆</span>
        <span style="text-align: center;">
            <label class="focus">【闭馆】</label>        </span>
        <!-- <span>
        <laber class="title">可预约数：</laber><label class="focus">9999</label><label>/9999</label>
      </span> -->
    </section>
    </div>
    <div>
    <section>
        <span class="where">嘉定校区图书馆</span>
        <span>
            <laber class="title">在馆人数：</laber><label class="focus">367</label><label>/3600</label>        </span>
        <!-- <span>
        <laber class="title">可预约数：</laber><label class="focus">9999</label><label>/9999</label>
      </span> -->
    </section>
    </div>
    <div>
    <section>
        <span class="where">沪西校区图书馆</span>
        <span style="text-align: center;">
            <label class="focus">【闭馆】</label>        </span>
        <!-- <span>
        <laber class="title">可预约数：</laber><label class="focus">9999</label><label>/9999</label>
      </span> -->
    </section>
    </div>
    <div>
    <section>
        <span class="where">沪北校区图书馆</span>
        <span style="text-align: center;">
            <label class="focus">【闭馆】</label>        </span>
        <!-- <span>
        <laber class="title">可预约数：</laber><label class="focus">9999</label><label>/9999</label>
      </span> -->
    </section>
    </div>
    <div>
    <section>
        <span class="where">德文图书馆</span>
        <span>
            <laber class="title">在馆人数：</laber><label class="focus">158</label><label>/150</label>        </span>
        <!-- <span>
        <laber class="title">可预约数：</laber><label class="focus">9999</label><label>/9999</label>
      </span> -->
    </section>
    </div>
</div>
'''
