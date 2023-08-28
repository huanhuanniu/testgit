# *_*coding:utf-8 *_*
"""
Created on Mon Aug  5 12:15:29 2019

@author: wcx
"""

"""
功能: 合并SCADA数据
输入: 不同变量、不同时间、不同机组的数据
输出: 按照机组输出csv
"""

import pandas as pd
import os
import re
from datetime import datetime
from datetime import timedelta
import warnings
warnings.filterwarnings('ignore')


def is_chinese(string):
    """
    判断字符串是否含有中文字符
    """
    chinese_pattern = re.compile(u'[\u4e00-\u9fa5]+')
    return chinese_pattern.search(string)


def read_path(folder):
    lst = []
    for root, dirs, files in os.walk(folder):
        if len(files)==0:
            continue
        for f in files:
            #记得修改机组号
            #if (f.startswith('F11_f') and f.endswith('000000.csv')):
            if f.endswith('.csv'):
                path = root + os.path.sep + f
                lst.append(path)
    return lst


pdir = r'E:\08-娑婆风电场\01-SCADA数据\\'
config_dir = r'E:\08-娑婆风电场\config\\'
result_dir = r'E:\08-娑婆风电场\05-计算结果\合并10分钟数据-批量\\'
config_var = pd.read_excel(config_dir + 'config_var_piliang.xlsx', sheet_name='SCADA')[['现有分析程序中的变量名', '1.5MW变量名']]
var_list = [item for item in config_var['1.5MW变量名'].tolist() if not(pd.isna(item)) == True]


#ids = ['F46WTC', 'F48WTC', 'F50WTC', 'F51WTC', 'F65WTC', 'F66WTC', 'F71WTC', 'F77WTC', 'F79WTC']
ids = [f"FJ{i:02}" for i in range(1, 34)]
for id in ids:
    df_id = pd.DataFrame()
    pdir_id = pdir + str(id)
    for i in read_path(pdir_id):
        try:
            df_i = pd.read_csv(i, encoding='gbk', index_col=False)
            df_i = df_i[var_list]
            var_std = [0]*len(var_list)
            for var in range(len(var_list)):
                var_std[var] = config_var.loc[config_var['1.5MW变量名'] == var_list[var], '现有分析程序中的变量名'].values[0]
            df_i.columns = var_std
            df_i.reset_index(drop=True, inplace=True)

            df_i = df_i[~df_i.applymap(lambda x:is_chinese(str(x))).any(1)]

            df_i['time'] = pd.to_datetime(df_i['time'])

            # time0 = i.split('\\')[-1][5:24]
            # time0 = datetime.strptime(time0, '%Y-%m-%d-%H-%M-%S')
            # time_list = [0]*len(df_i)

            # for j in range(len(time_list)):
            #     time_list[j] = time0 + timedelta(seconds=j)
            # df_i['time'] = time_list
            df_id = pd.concat([df_id, df_i])
        except Exception as e:
            print(i + e.__class__.__name__, e)
    df_id = df_id.sort_values(by='time')
    df_id = df_id.set_index('time')
    # object转为numeric
    df_id[df_id.select_dtypes(include=['object']).columns] = df_id.select_dtypes(include=['object']).apply(pd.to_numeric,
                                                                                                  errors='coerce')

    resample_data = df_id.resample('10min').agg(['min', 'max', 'mean', 'std'])
    resample_data.reset_index(inplace=True)
    resample_data.columns = ['_'.join(col).strip() for col in resample_data.columns.values]
    resample_data = resample_data.rename(columns={'time_': 'time'})
    resample_data = resample_data.set_index('time')
    resample_data.dropna(how='all', axis=0, inplace=True)
    resample_data = resample_data.sort_values(by='time')
    resample_data.reset_index(inplace=True)
    resample_data.to_csv(result_dir + str(id) +'_10min_hebing.csv')
    print('end!!!!')

