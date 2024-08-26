import pygrib



# 获取文件夹 /home/ann/opt/GFS2Tensor/gfsdl/20240821/06/中所有文件的绝对路径
import os
import glob

import torch

grbs_file_list = glob.glob('/home/ann/opt/GFS2Tensor/gfsdl/20240821/06/*')
# 将文件列表按文件名排序
grbs_file_list.sort()
for file in grbs_file_list:
    grbs= pygrib.open(file)
    # 移动游标到第一个GRIB记录
    grbs.seek(0)
    # 遍历获取降雨等数据记录
    precipitation_rate = None
    print(f'------------------*******************{file}------------------*******************')
    for inx, grb in enumerate(grbs):
        '''
        当前下载的 grb 信息
            ** Plant canopy surface water & CNWAT 表示植物冠层表面的水量，即植物表面存储的水量，单位为 kg/m²
            ** Convective precipitation rate(instant) & CPRAT 表示对流降水的速率，单位为 kg/m²/s，即每平方米每秒的降水量。
            Precipitation rate(instant) & PRATE 表示总降水的速率，包含对流和非对流降水，单位为 kg/m²/s。
            ** Convective precipitation rate (avg) & ACPCP 表示累积的对流降水量，单位为 kg/m²，表示一段时间内通过对流产生的总降水量。
            Precipitation rate (avg) & PRATE 表示总降水的速率，包含对流和非对流降水，单位为 kg/m²/s
            Total Precipitation & APCP 表示指定周期内总降水量的累积值，单位通常是 kg/m² 或 mm
            Total Precipitation (0-x hrs) & APCP 表示总降水量的累积值，单位通常是 kg/m² 或 mm
            ** Convective precipitation (water) & CPRAT 指定时间段内对流降水的总量
            ** Convective precipitation (water) (0-now hrs) & CPRAT 指定时间段内对流降水的总量
        grb 打印示例  5:Precipitation rate:kg m**-2 s**-1 (avg):regular_ll:surface:level 0:fcst time 378-381 hrs (avg):from 202408210600
         `print(grb)` 打印的信息中，每个部分对应于 `grb` 对象的不同属性。以下是这些信息的解析：
        1. **5**: 
           - 这是 GRIB 文件中该记录的索引或编号，通常对应 `grb.message_number`。
        
        2. **Precipitation rate**: 
           - 这是变量的名称，通常对应 `grb.name`。
        
        3. **kg m**-2 s**-1**: 
           - 这是变量的单位，通常对应 `grb.units`。
        
        4. **(avg)**: 
           - 这是统计方法，表示这是一个平均值，通常可以从 `grb.stepTypeInternal` 属性获取。
        
        5. **regular_ll**: 
           - 这是网格类型，表示这是一个规则的纬度/经度网格，通常对应 `grb.gridType`。
        
        6. **surface**: 
           - 这是水平，表示该变量是针对地表的，通常对应 `grb.typeOfLevel`。
        
        7. **level 0**: 
           - 这是变量的水平层次，通常对应 `grb.level`。
        
        8. **fcst time 378-381 hrs (avg)**:   统计的周期不确定
           - **378-381 hrs (avg)**: 这是预测时间的范围和统计方法，表示平均值的时间跨度，通常对应 `grb.startStep` 和 `grb.endStep`，或者 `grb.stepRange`。
           - **fcst time**: 表示这是一个预报时间，通常对应 `grb.forecastTime`。
        
        9. **from 202408210600**: 
           - 这是数据的起始时间，通常对应 `grb.dataDate` 和 `grb.dataTime`，也可能结合 `grb.analDate` 或 `grb.validDate`。
        '''
        if grb.name == 'Precipitation rate' and grb.stepTypeInternal == 'avg': # 平均降水量
            # print(grb)
            pass
            # precipitation_rate_grb = grb
            # # 获取grb中可用键 和 网格降雨数据记录
            # # keys = grb.keys()
            # precipitation_rat = grb.values
            # # print(keys)
            # analDate = grb.analDate   # 模型运行时间
            # forecastTime = grb.forecastTime
            # print(analDate,forecastTime)
            # # 获取网格的经纬度
            # lats, lons = grb.latlons()
            # print(lats.shape, lats.min(), lats.max(), lons.shape, lons.min(), lons.max())
            # 获取某个子集的数据
            # data, lats, lons = grb.data(lat1=50, lat2=53, lon1=120, lon2=130)
            # print(data.shape, lats.min(), lats.max(), lons.min(), lons.max())
        elif  grb.name == 'Precipitation rate' and grb.stepTypeInternal == 'instant': # 瞬时降水量
            # print(grb)
            data, lats, lons = grb.data()
            print(data.shape, lats.shape, lons.shape)
            # data, lats, lons 全部转化为张量
            # data = torch.tensor(data)
            # lats = torch.tensor(lats)
            # lons = torch.tensor(lons)
            # 三个张量合并
            # grb_tensor = torch.cat((data, lats, lons), dim=0)
            # print(grb_tensor.shape)
            pass

