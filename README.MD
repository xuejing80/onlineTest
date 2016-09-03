###环境需要
django>=1.9.5 python>=3.4
###需要的依赖：
1. pymysql 安装 pip3 install pymysql

###初始化数据库
1. 在onlineTest/settings.py内修改 DATABASES项

        'USER': 'mysql账号',
        'PASSWORD': 'mysql密码'

2. 执行sql脚本init.sql
3. 终端运行

        python3 manage.py makemigrations
        python3 manage.py migrate

###本地测试方法：
python3 manage.py runserver 访问127.0.0.1:8000/index

###部署到apache方法：
（暂缺