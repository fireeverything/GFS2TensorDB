"""
WRF-ARW Model & GFS Automation System using Python 3
Credit : Muhamad Reza Pahlevi (@elpahlevi) & Agung Baruna Setiawan Noor (@agungbaruna)
If you find any trouble, reach the author via email : mr.levipahlevi@gmail.com
"""
import logging
import os
import re
import requests
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta

# Folder path
gfs_save_dir = r"D:\workspacepy\GFS2TensorDB\gfsdl"  # Path to GFS dataset folder

# GFS 数据集默认参数
cycle_times = ["00", "06", "12", "18"]  # GFS模型每天运行四次，分别是 00Z、06Z、12Z 和 18Z。00Z 表示午夜的 UTC 时间
base_url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25_1hr.pl'  # 用于提取特定的0.25度分辨率的逐小时数据集
'''
这些参数指定了要提取的数据变量：
    var_ACPCP=on： (ACPCP)累计对流性降水量，表示指定时间段内的总降水量。
    var_APCP=on：(APCP)累计降水量（Accumulated Precipitation），通常以毫米为单位。
    var_CNWAT=on：(CNWAT)云水含量（Net Precipitable Water），大气中云层的液态水含量。
    var_CPRAT=on： (CPRAT)对流性降水速率（Precipitation Rate），表示单位时间内的降水量。
    var_CWAT=on：(CWAT)总云水含量（Cloud Water），表示云中水蒸气的含量。
    var_PLPL=on：(PLPL)液态相态概率（Precipitation Type），表示降水的类型（如雨、雪、冰等）。
    var_PRATE=on：(PRATE)降水率（Precipitation Rate），表示单位时间内的降水量
    var_PWAT=on： (PWAT)可降水量（Precipitable Water），表示大气中的总水汽量。
    var_RWMR=on： (RWMR)雨水混合比（Rain Water Mixing Ratio），表示单位体积空气中雨水的质量。
    lev_surface=on：这个参数指定了要提取的数据层级，为地表层 (surface)
    subregion=：留空意味着不设置特定的子区域，下载的是全区域数据。不过由于会指定 toplat, leftlon, rightlon, bottomlat 这些参数的存在，实际上指定了一个子区域。
    
'''
var_s = 'var_ACPCP=on&var_APCP=on&var_CNWAT=on&var_CPRAT=on&var_CWAT=on&var_PLPL=on&var_PRATE=on&var_PWAT=on&var_RWMR=on&lev_surface=on&subregion='
gfs_url_dir = '%2Fgfs.{0}%2F{1}%2Fatmos'  # 要下载文件存储在noaa服务器的路径 两个占位符，分别对应20240821格式的日期 和 00 格式 cycle_times
dl_file_suffixes = [f'f{i:03d}' for i in range(384)]  # 要下载文件的文件名后缀
dl_file = 'gfs.t{2}z.pgrb2.0p25.{3}'  # 要下载文件的文件名 两个占位符，分别对应00格式cycle_times 和  dl_file_suffixes
# 自定义GFS下载筛选参数
gfs_num_workers = 14  # 分配同时下载gfs数据集的线程数
gfs_download_increment = 1  # 下载数据集在时间尺度上的间隔 单位：小时
gfs_left_lon = 73.6  # -180 to 180 定义数据集范围 西至
gfs_right_lon = 135.1  # -180 to 180 定义数据集范围 东至
gfs_top_lat = 53.5  # -90 to 90 定义数据集范围 北至
gfs_bottom_lat = 4  # -90 to 90 定义数据集范围 南至

complete_url = f"{base_url}?dir={gfs_url_dir}&file={dl_file}&{var_s}&toplat={gfs_top_lat}&leftlon={gfs_left_lon}&rightlon={gfs_right_lon}&bottomlat={gfs_bottom_lat}"


def gfs_download_worker(request_url):
    # 从 request_url中提取文件名和日期
    parsed_url = urllib.parse.urlparse(request_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    # 获取并解码 'dir' 参数的值
    dir_value_encoded = query_params.get('dir', [''])[0]
    dir_value = urllib.parse.unquote(dir_value_encoded)
    # 使用正则表达式从 'dir' 中提取日期和时间
    match = re.search(r'gfs\.(\d{8})/(\d{2})', dir_value)
    if match:
        date = match.group(1)
        cycle = match.group(2)
    else:
        date = None
        cycle = None
    # 获取 'file' 参数的值
    file_name = query_params.get('file', [''])[0]
    save_file_dir = f'{gfs_save_dir}/{date}/{cycle}'
    save_file_path = f'{save_file_dir}/{file_name}'
    if not os.path.exists(save_file_path):
        # 判断目录是否存在，不存在则级联创建
        os.makedirs(save_file_dir, exist_ok=True)
        # 请求数据
        response = requests.get(request_url)
        if response.status_code == 200:
            with open(save_file_path, "wb") as f:
                f.write(response.content)
            print(f"INFO: GFS Downloader - {file_name} has been downloaded")
        elif response.status_code == 404:
            print(f"INFO: GFS Downloader - {file_name} is not found, skipped")
    else:
        print(f"INFO: GFS Downlaoder - File {file_name} is already exist, skipped")


def start_GFS_download():
    # 获取当前时间
    now = datetime.now()
    # 将获取到的当地时间now转化为 UTC+0 时间
    now = now.astimezone(timezone.utc)
    # 获取前一天的日期
    now = now - timedelta(days=1)
    # 将now转化为 20240821 这种形式的字符串
    now_date_str = now.strftime("%Y%m%d")
    formatted_complete_urls = []  # 用于存储本次下载的所有GFS数据地址
    for cycle_time in cycle_times:
        if int(cycle_time) < now.hour or True:
            for dl_file_suffix in dl_file_suffixes:
                formatted_complete_urls.append(
                    complete_url.format(now_date_str, cycle_time, cycle_time, dl_file_suffix))
    with ThreadPoolExecutor(max_workers=gfs_num_workers) as executor:
        executor.map(gfs_download_worker, formatted_complete_urls)


if __name__ == '__main__':
    start_GFS_download()
