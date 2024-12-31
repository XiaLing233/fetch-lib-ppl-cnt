import configparser
from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')

# 设置数据库连接
DB_HOST = CONFIG['database']['host']
DB_USER_READ_ONLY = CONFIG['database']['user-read-only']
DB_PASSWORD_READ_ONLY = CONFIG['database']['password-read-only']
DB_DATABASE = CONFIG['database']['database']
DB_PORT = int(CONFIG['database']['port'])
DB_CHARSET = CONFIG['database']['charset']

# 数据库
TABLE_NAME = CONFIG['table']['name']
LIB_NAME = CONFIG['table']['lib-name']
LIB_PPL_CUR = CONFIG['table']['lib-ppl-cur']
LIB_PPL_MAX = CONFIG['table']['lib-ppl-max']
TIMESTAMP = CONFIG['table']['timestamp']

# 日志
INFO_ADDR = CONFIG['log']['info_addr']
ERROR_ADDR = CONFIG['log']['err_addr']
ENCODING = CONFIG['log']['encoding']

# 数据库配置
DB_CONFIG = {
    'host': DB_HOST,
    'user': DB_USER_READ_ONLY,
    'password': DB_PASSWORD_READ_ONLY,
    'database': DB_DATABASE,
    'port': DB_PORT,
    'charset': DB_CHARSET
}

# 获得图书馆人数
'''
传入的 json 数据格式：
{
    "lib_name": "图书馆名称",
    "timestamp": "时间戳",  # 形如 "2024-05-20"
}
'''
'''
返回的 json 数据格式：
{
    status: "ok" | "fail",
    msg: "错误信息",
    data[
        {
            "lib_ppl_cur": "当前人数",
            "time": "某一天的时间" # 形如 "10:23"
        }
    ]
}
'''
@app.route('/api/get-lib-ppl')
def get_lib_ppl():
    # 获取请求数据
    req_data = request.json
    lib_name = req_data['lib_name']
    timestamp = req_data['timestamp']
    
    # 连接数据库
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 查询数据库
    try:
        query = f"SELECT {LIB_PPL_CUR}, {TIMESTAMP} FROM {TABLE_NAME} WHERE {LIB_NAME} = '{lib_name}' AND {TIMESTAMP} = '{timestamp}'"
        cursor.execute(query)
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({
            'status': 'fail',
            'msg': '查询失败，数据库错误。\n输入的 SQL 语句为：' + query
        }), 400
    # 获取查询结果
    result = cursor.fetchall()

    # 如果查询结果为空
    if len(result) == 0:
        cursor.close()
        conn.close()
        return jsonify({
            'status': 'ok',
            'msg': '暂无数据',
        }), 200

    data = []
    for row in result:
        data.append({
            LIB_PPL_CUR: row[0],
            TIMESTAMP: str(row[1])[11:19]  # 只取时间部分
        })

    # 关闭数据库连接
    cursor.close()
    conn.close()

    # 返回数据
    return jsonify({
        'status': 'ok',
        'msg': '查询成功',
        'data': data
    }), 200