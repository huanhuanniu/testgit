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
import copy
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


def time_diff(data):
    data = data.sort_values('time')  # 对时间排序
    data = data.reset_index(drop=True)
    data['time_diff'] = data['time'].diff().dt.total_seconds()

    return data


def split_df(df, index_list):
    # 时间不连续的分段
    dfs = []
    for i, index in enumerate(index_list):
        if i == 0:
            # 第一个数据框从0开始
            dfs.append(df.loc[:index - 1])
        else:
            # 其他数据框从上一个索引加1开始
            dfs.append(df.loc[index_list[i - 1]:index - 1])
    # 最后一个数据框到最后一个索引结束
    dfs.append(df.loc[index_list[-1]:])
    # 打印结果
    # for i, df_split in enumerate(dfs):
    #     print(f"Dataframe {i + 1}")
    #     print(df_split)
    return dfs



def status_groups(data, status, limit=60):
    if data[status].max()>0:
        ts_start_list = []
        ts_end_list = []
        ws_mean_list = []
        ws_max_list = []
        ws_min_list = []
        pitch_mean_list = []
        pitch_max_list = []
        pitch_min_list = []

        grouped = data.groupby(((data[status].shift() != data[status])).cumsum())
        for i,j in grouped:
            if 1 in j[status].tolist():
                if j['time_diff'].max()<limit:
                    ts_start = j['time'].tolist()[0]
                    ts_start_list.append(ts_start)
                    ts_end = j['time'].tolist()[-1]
                    ts_end_list.append(ts_end)
                    ws_mean = j['CI_WindSpeed1'].mean()
                    ws_mean_list.append(ws_mean)
                    ws_max = j['CI_WindSpeed1'].max()
                    ws_max_list.append(ws_max)
                    ws_min = j['CI_WindSpeed1'].min()
                    ws_min_list.append(ws_min)
                    pitch_mean = j['CI_PitchPositionA1'].mean()
                    pitch_mean_list.append(pitch_mean)
                    pitch_max = j['CI_PitchPositionA1'].max()
                    pitch_max_list.append(pitch_max)
                    pitch_min = j['CI_PitchPositionA1'].min()
                    pitch_min_list.append(pitch_min)
                else:
                    above_limit = j.loc[j['time_diff'] >= limit].index.tolist()
                    split_dfs = split_df(j, above_limit)
                    for split_df_i in split_dfs:
                        if split_df_i.empty is False:
                            ts_start = split_df_i['time'].tolist()[0]
                            ts_start_list.append(ts_start)
                            ts_end = split_df_i['time'].tolist()[-1]
                            ts_end_list.append(ts_end)
                            ws_mean = split_df_i['CI_WindSpeed1'].mean()
                            ws_mean_list.append(ws_mean)
                            ws_max = split_df_i['CI_WindSpeed1'].max()
                            ws_max_list.append(ws_max)
                            ws_min = split_df_i['CI_WindSpeed1'].min()
                            ws_min_list.append(ws_min)
                            pitch_mean = split_df_i['CI_PitchPositionA1'].mean()
                            pitch_mean_list.append(pitch_mean)
                            pitch_max = split_df_i['CI_PitchPositionA1'].max()
                            pitch_max_list.append(pitch_max)
                            pitch_min = split_df_i['CI_PitchPositionA1'].min()
                            pitch_min_list.append(pitch_min)
            else:
                continue

        result = pd.DataFrame({'ts_start': ts_start_list, 'ts_end': ts_end_list, 'ws_mean': ws_mean_list, 'ws_max': ws_max_list,
                               'ws_min': ws_min_list, 'pitch_mean': pitch_mean_list, 'pitch_max': pitch_max_list, 'pitch_min': pitch_min_list})
        result['ts_diff'] = (result['ts_end'] - result['ts_start'])
        result['ts_diff'] = result['ts_diff'].apply(lambda x: x.total_seconds())

    return result



def dataProcess(ids, pdir, result_dir):
    for id in ids:
        starting_stat_all = pd.DataFrame()
        standstill_stat_all = pd.DataFrame()
        stop_stat_all = pd.DataFrame()
        pdir_id = pdir + str(id)
        for i in read_path(pdir_id):
            try:
                df_i = pd.read_csv(i, encoding='gbk', index_col=False)
                df_i = df_i[var_list]
                var_std = [0]*len(var_list)
                for var in range(len(var_list)):
                    var_std[var] = config_var.loc[config_var['1.5MW变量名'] == var_list[var], '现有分析程序中的变量名'].values[0]
                df_i.columns = var_std
                df_i['time'] = pd.to_datetime(df_i['time'])
                df_i = df_i.sort_values(by='time')
                df_i = df_i.drop_duplicates('time', keep='first')

                df_i = df_i[~df_i.applymap(lambda x:is_chinese(str(x))).any(1)]
                df_i.reset_index(drop=True, inplace=True)
                df_i = time_diff(df_i)

                df_i[df_i.select_dtypes(include=['object']).columns] = df_i.select_dtypes(include=['object']).apply(
                    pd.to_numeric, errors='coerce')

                starting_stat = status_groups(df_i, 'starting', limit=60)
                starting_stat['wtid'] = id
                starting_stat['status'] = 'starting'
                standstill_stat = status_groups(df_i, 'standstill', limit=60)
                standstill_stat['wtid'] = id
                standstill_stat['status'] = 'standstill'
                stop_stat = status_groups(df_i, 'stop', limit=60)
                stop_stat['wtid'] = id
                stop_stat['status'] = 'stop'
                starting_stat_all = pd.concat([starting_stat_all, starting_stat])
                standstill_stat_all = pd.concat([standstill_stat_all, standstill_stat])
                stop_stat_all = pd.concat([stop_stat_all, stop_stat])



                # time0 = i.split('\\')[-1][5:24]
                # time0 = datetime.strptime(time0, '%Y-%m-%d-%H-%M-%S')
                # time_list = [0]*len(df_i)

                # for j in range(len(time_list)):
                #     time_list[j] = time0 + timedelta(seconds=j)
                # df_i['time'] = time_list
                # df_id = pd.concat([df_id, df_i])
            except Exception as e:
                print(i + e.__class__.__name__, e)
            print(i + ' end!!')
        starting_stat_all.sort_values(by='ts_start')
        starting_stat_all.reset_index(inplace=True, drop=True)

        standstill_stat_all.sort_values(by='ts_start')
        standstill_stat_all.reset_index(inplace=True, drop=True)

        stop_stat_all.sort_values(by='ts_start')
        stop_stat_all.reset_index(inplace=True, drop=True)

        starting_stat_all.to_csv(result_dir + id + '_starting.csv')
        standstill_stat_all.to_csv(result_dir + id + '_standstill.csv')
        stop_stat_all.to_csv(result_dir + id + '_stop.csv')
        print(id + ' end!!')

        # df_id = df_id.sort_values(by='time')
        # df_id = df_id.set_index('time')

        # resample_data = df_id.resample('10min').agg(['min', 'max', 'mean', 'std'])
        # resample_data.reset_index(inplace=True)
        # resample_data.columns = ['_'.join(col).strip() for col in resample_data.columns.values]
        # resample_data = resample_data.rename(columns={'time_': 'time'})
        # resample_data = resample_data.set_index('time')
        # resample_data.dropna(how='all', axis=0, inplace=True)
        # resample_data = resample_data.sort_values(by='time')
        # resample_data.reset_index(inplace=True)
        # resample_data.to_csv(result_dir + str(id) +'_10min_hebing.csv')
    print('All end!!!!')



if __name__ == '__main__':
    ids = [f"FJ{i:02}" for i in range(1, 34)]
    pdir = r'E:\08-娑婆风电场\01-SCADA数据\\'
    result_dir = r'E:\08-娑婆风电场\计算结果\SCADA结果\启停机结果\\'
    config_dir = r'E:\08-娑婆风电场\config\\'
    config_var = pd.read_excel(config_dir + 'config_var.xlsx', sheet_name='SCADA_10s')[
        ['现有分析程序中的变量名', '1.5MW变量名']]
    var_list = [item for item in config_var['1.5MW变量名'].tolist() if not (pd.isna(item)) == True]
    dataProcess(ids, pdir, result_dir)


