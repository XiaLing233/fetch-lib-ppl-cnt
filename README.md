# 获取图书馆人数的小项目

## 起因

你是否因为图书馆的人数众多而烦恼？如果做不到心无旁骛，一天 24 小时，到底什么时候才能获得最高质量的自习体验？本项目记录了同济大学图书馆 24 小时的人数变化（如果嘉图和德图不是 24 小时开馆，记录还能简单点），从而让你洞悉图书馆人数的动态变化，选择最适合自己的自习时光。

## 环境配置

虚拟环境(`.venv`)可以解决不同 `python` 依赖同时存在的情况，类似于类的支配规则，低层屏蔽高层。创建一个环境，

```bash
mkdir foo
cd foo
python3 -m venv .venv

# 记得激活环境(Linux/MacOS)
.venv/bin/activate
# 也有可能是(Windows)
.venv\Scripts\activate
```

然后，输入以下命令，在`.venv` 中安装如下 `packages`：

```bash
# 和爬网页相关的
pip install requests                # 发送网络请求
pip install beautifulsoup4          # 对 html 进行解析
pip install mysql-connector-python  # 数据库
pip install configparser            # 读取配置文件，oop 造过的轮子
pip install logging                 # 日志相关

# flask 相关
pip install flask
pip install flask-cors # 允许跨域请求
```

接下来是前端的配置：

```bash
npm create vue@latest
# 安装完成后，切换到目录文件，运行：
npm install
# 可以通过
npm run dev
# 来测试安装状态
```

使用了 `ant design vue` 模板来开发，更高效：

```bash
npm install ant-design-vue@4.x --save
# 使用图标，具体使用哪个图标，需要预先注册：
npm install --save @ant-design/icons-vue
```

展示图表，需要用到 `vue-chartjs`

```bash
npm i vue-chartjs chart.js
npm install chartjs-adapter-date-fns # 对时间的处理
npm install date-fns # 一定要记得安装对时间的处理，而且，要在前端的对应位置安装，记得切换到正确的文件夹
npm install dayjs # 对坐标点日期转换的处理
```
