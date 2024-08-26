#FROM registry.cn-hangzhou.aliyuncs.com/mapuni/python
FROM registry.cn-hangzhou.aliyuncs.com/mapuni/python
LABEL authors="zhenc"


# 设置工作目录
WORKDIR /GFS2TensorDB

# 创建符号链接设置时区
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# 复制当前目录内容到工作目录
COPY . /GFS2TensorDB

# 安装 Python 依赖项
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r ./requirements.txt

# 清理 pip 缓存
RUN pip cache purge
