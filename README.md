# 获取图书馆人数的小项目

## 网站部署在

[这里](https://lib.xialing.icu)

## 起因

你是否因为图书馆的人数众多而烦恼？如果做不到心无旁骛，一天 24 小时，到底什么时候才能获得最高质量的自习体验？本项目记录了同济大学图书馆 24 小时的人数变化（如果嘉图和德图不是 24 小时开馆，记录还能简单点），从而让你洞悉图书馆人数的动态变化，选择最适合自己的自习时光。

## 环境配置

### python

建议使用虚拟环境：

```bash
python3 -m venv .venv

# 记得激活环境(Linux/MacOS)
source .venv/bin/activate
# 也有可能是(Windows)
.venv\Scripts\activate
```

然后安装所有的依赖：

```bash
pip install -r requirements.txt
```

### 前端

接下来是前端的配置：

切换到 `tju-lib-frontend` 文件夹，运行

`npm install` 安装所有的包。

### 数据库

接下来是数据库的配置，两张表，分别为：

```sql
CREATE TABLE `lib_cnt` (
  `id` int NOT NULL AUTO_INCREMENT,
  `lib_name` varchar(255) NOT NULL,
  `lib_ppl_cur` int NOT NULL,
  `lib_ppl_max` int NOT NULL,
  `rec_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3017 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='calc tongji lib population count continously'
```

```sql
CREATE TABLE `log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `msg` varchar(200) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `is_public` tinyint DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
```

数据就不方便提供了，运行几分钟脚本，爬一点测试数据吧。

### config.ini

在项目的根目录下，也就是和本文件平级的目录下，有一个 `config.ini` 被 git ignore 了，没有同步到仓库，需要手动配置。条目如下，一些隐私条目需要手动修改：

```ini
# ini info

# config of database
[database]
host = localhost
user = foo
password = bar
# read only account must be different from the root in real world
user-read-only = baz
password-read-only = haha
database = choose_a_name
port = 3306
charset = utf8mb4

[network]
; no need to add single quotes
; need to add www prefix
url = https://www.lib.tongji.edu.cn
target-class = hmp wow fadeInUp
lib-closed = 【闭馆】

[table]
name = lib_cnt
lib-name = lib_name
lib-ppl-cur = lib_ppl_cur
lib-ppl-max = lib_ppl_max
timestamp = rec_time

[log]
; dont forget end with /
info_addr = ./logs/
err_addr = ./errors/
encoding = utf-8
```

## 启动

在项目根目录下运行 `flask run --port=1314` 启动后端。

在 `tju-lib-frontend` 下输入 `npm run dev` 启动前端。

数据库，请自行配置好。

即可。
