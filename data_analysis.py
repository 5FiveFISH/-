'''数据获取'''
import pandas as pd
attr_features = pd.read_csv(r"D:\****\tmp_user_attribute_feature.csv", encoding='utf-16', sep='\t', na_values='\\N')
attr_features['answer_time'] = pd.to_datetime(attr_features['answer_time'])
attr_features['call_date'] = pd.to_datetime(attr_features['call_date'])
attr_features


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

'''命中时段分析'''
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams.update({'font.family': 'Arial Unicode MS'})
plt.rcParams.update({'font.size': 14})


# 命中日期分布
count = browsing_info['call_date'].value_counts().sort_index()
plt.figure(figsize=(8, 5))
plt.plot(np.array(count.index), count.values, marker='o')
plt.xlabel('日期')
plt.ylabel('命中频率')
plt.title('外呼命中日期分布情况')
tick_positions = pd.date_range(start=count.index.min(), end=count.index.max(), freq='5D')
plt.xticks(tick_positions, tick_positions.strftime('%m-%d'), rotation=45)
plt.grid(True)

# 命中工作日分布
browsing_info['call_weekay'] = browsing_info['call_weekay'].map(
    {1:'周一',2:'周二',3:'周三',4:'周四',5:'周五',}
)
count = browsing_info['call_weekay'].value_counts().sort_index()
plt.figure(figsize=(8, 5))
plt.plot(np.array(count.index), count.values, marker='o')
plt.xlabel('工作日')
plt.ylabel('命中频率')
plt.title('外呼命中工作日分布情况')
plt.xticks(rotation=45)
plt.grid(True)

# 命中时间段分布
count = browsing_info['call_hour'].value_counts().sort_index()
plt.figure(figsize=(8, 5))
plt.plot(np.array(count.index), count.values, marker='o')
plt.xlabel('小时')
plt.ylabel('命中频率')
plt.title('外呼命中时间段分布情况')
plt.xticks(rotation=45)
plt.grid(True)


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

'''饼图'''
import plotly.express as px

# is_single
counts = attr_features['is_single'].value_counts()
labels = counts.index.map({1:'单身',0:'非单身'})
fig = px.pie(counts, values=counts.values, names=labels, hole=0.3,
             color_discrete_sequence=px.colors.sequential.Teal)
fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(counts))
fig.update_layout(width=380, height=380, showlegend=False)
fig.show()

# sex、age_group
columns = ['sex', 'age_group']
for col in columns:
    counts = attr_features[col].value_counts()
    fig = px.pie(counts, values=counts.values, names=counts.index, title=col, hole=0.3,
                 color_discrete_sequence=px.colors.sequential.Teal)
    fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(counts))
    fig.update_layout(width=400, height=400, showlegend=False, title_x=0.5, title_y=0.95, margin=dict(t=2))
    fig.show()



'''直方图'''
import plotly.figure_factory as ff

# 年龄
fig = ff.create_distplot([attr_features['age'].dropna()], group_labels=['年龄'], bin_size=2, show_rug=False)
fig.update_layout(title='年龄分布图', font=dict(size=18))  # 设置标题文字大小
fig.update_xaxes(title_text='年龄', title_font=dict(size=14), dtick=10)  # 设置 x 轴标签文字大小
fig.update_yaxes(title_text='密度', title_font=dict(size=14))  # 设置 y 轴标签文字大小
fig.update_traces(marker=dict(opacity=0.7))  # 设置直方图的透明度
fig.update_layout(width=600, height=400)
fig.show()



'''地图'''

import copy
from pyecharts import options as opts
from pyecharts.charts import Map

attr_features['user_city'] = attr_features['user_city'].str.replace(r'市$', '', regex=True)
city = attr_features['user_city'].value_counts()
city_list = [list(ct) for ct in city.items()]
def province_city():
    '''这是从接口里爬取的数据（不太准，但是误差也可以忽略不计！）'''
    area_data = {}
    with open(r'D:\****\中国省份_城市.txt', mode='r', encoding='utf-8') as f:
        for line in f:
            line = line.strip().split('_')
            area_data[line[0]] = line[1].split(',')
    province_data = []
    for ct in city_list:
        for k, v in area_data.items():
            for i in v:
                if ct[0] in i:
                    ct[0] = k
                    province_data.append(ct)
    area_data_deepcopy = copy.deepcopy(area_data)
    for k in area_data_deepcopy.keys():
        area_data_deepcopy[k] = 0
    for i in province_data:
        if i[0] in area_data_deepcopy.keys():
            area_data_deepcopy[i[0]] = area_data_deepcopy[i[0]] +i[1]
    province_data = [[k,v]for k,v in area_data_deepcopy.items()]
    best = max(area_data_deepcopy.values())
    return province_data,best
province_data,best = province_city()
#地图_中国地图（带省份）Map-VisualMap（连续型）
c1 = (
    Map()
    .add( "外呼命中人群分布图", province_data, "china")
    .set_global_opts(
        title_opts=opts.TitleOpts(title="外呼命中人群分布图"),
        visualmap_opts=opts.VisualMapOpts(max_=int(best / 2)),
    )
    .render("map_china.html")
)


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

'''饼图'''
import plotly.express as px

# 会员等级
counts = attr_features['cust_level'].value_counts()
fig = px.pie(counts, values=counts.values, names=counts.index, title=col, hole=0.3,
             color_discrete_sequence=px.colors.sequential.Teal)
fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(counts))
fig.update_layout(width=400, height=400, showlegend=False, title_x=0.5, title_y=0.95, margin=dict(t=2))
fig.show()

# 会员类型
counts = attr_features['cust_type'].value_counts()
labels = counts.index.map({1:'老带新新会员',2:'新会员(新客户)',3:'老会员(新客户)',4:'老会员老客户',-1:'其他'})
fig = px.pie(counts, values=counts.values, names=labels,
             title='cust_type', hole=0.3,
             color_discrete_sequence=px.colors.sequential.Teal)
fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(counts))
fig.update_layout(width=500, height=500, showlegend=False, title_x=0.5, title_y=0.9, margin=dict(t=2))
fig.show()

# 企微用户
counts = attr_features['is_office_weixin'].value_counts()
labels = counts.index.map({1:'企微用户',0:'非企微用户'})
fig = px.pie(counts, values=counts.values, names=labels, hole=0.3,
             color_discrete_sequence=px.colors.sequential.Teal)
fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(counts))
fig.update_layout(width=420, height=420, showlegend=False)
fig.show()

# 可触达渠道
# 将access_channels列中的多个渠道拆分成单独的行，统计每类渠道的出现次数
counts = attr_features['access_channels'].str.split(',').explode().value_counts()
fig = px.pie(counts, values=counts.values, names=counts.index, hole=0.3,
             color_discrete_sequence=px.colors.sequential.Teal)
fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(counts))
fig.update_layout(width=480, height=480, showlegend=False)
fig.show()



'''直方图'''
import plotly.express as px

# 注册时间
fig = px.histogram(attr_features, x='rg_time', nbins=80, marginal='box', title='注册时间分布')
fig.update_xaxes(title_text='注册时间', title_font=dict(size=14))  # 设置 x 轴标签文字大小
fig.update_yaxes(title_text='命中频率', title_font=dict(size=14))  # 设置 y 轴标签文字大小
fig.update_traces(marker=dict(opacity=0.7))  # 设置直方图的透明度
fig.update_layout(width=600, height=400)
fig.show()

# 添加企微时间
fig = px.histogram(attr_features[attr_features['office_weixin_time'] != 0], x='office_weixin_time', nbins=80, marginal='box', title='添加企微时间分布')
fig.update_xaxes(title_text='添加企微时间', title_font=dict(size=14))  # 设置 x 轴标签文字大小
fig.update_yaxes(title_text='命中频率', title_font=dict(size=14))  # 设置 y 轴标签文字大小
fig.update_traces(marker=dict(opacity=0.7))  # 设置直方图的透明度
fig.update_layout(width=600, height=400)
fig.show()


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import plotly.express as px

columns = ['elderly_num', 'child_num']
for col in columns:
    counts = attr_features[col].value_counts()
    fig = px.pie(counts, values=counts.values, names=counts.index, title=col, hole=0.3,
                 color_discrete_sequence=px.colors.sequential.Teal)
    fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(counts))
    fig.update_layout(width=400, height=400, showlegend=False, title_x=0.5, title_y=0.95, margin=dict(t=2))
    fig.show()


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import plotly.express as px

# 产品价格敏感度
counts = attr_features['prd_price_sensitivity'].value_counts()
fig = px.pie(counts, values=counts.values, names=counts.index,
             title='prd_price_sensitivity', hole=0.3,
             color_discrete_sequence=px.colors.sequential.Teal)
fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(counts))
fig.update_layout(width=400, height=400, showlegend=False, title_x=0.5, title_y=1, margin=dict(t=2))
fig.update_traces(rotation=90)
fig.show()

# 其余
columns = ['schedule_domestic_flight','schedule_domestic','schedule_abroad_flight','schedule_abroad_flight',
           'transport_type_preference','hobbie_hotel_lvl','hobbie_dest_class','travel_people','start_timebucket_preference',
           'marketing_preference_degree','marketing_type_preference_degree']
for col in columns:
    counts = attr_features[col].value_counts()
    fig = px.pie(counts, values=counts.values, names=counts.index, title=col, hole=0.3,
                 color_discrete_sequence=px.colors.sequential.Teal)
    fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(counts))
    fig.update_layout(width=400, height=400, showlegend=False, title_x=0.5, title_y=0.95, margin=dict(t=2))
    fig.show()


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

'''饼图'''
import plotly.express as px

# 其余
columns = ['transport_type_preference','hobbie_hotel_lvl','hobbie_dest_class','travel_people','start_timebucket_preference',
           'marketing_preference_degree','marketing_type_preference_degree']
for col in columns:
    counts = attr_features[col].value_counts()
    fig = px.pie(counts, values=counts.values, names=counts.index, title=col, hole=0.3,
                 color_discrete_sequence=px.colors.sequential.Teal)
    fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(counts))
    fig.update_layout(width=400, height=400, showlegend=False, title_x=0.5, title_y=0.95, margin=dict(t=2))
    fig.show()

# 爱玩偏好
counts = attr_features['love_play_preference'].str.split(',').explode().value_counts()
fig = px.pie(counts, values=counts.values, names=counts.index,
             title='love_play_preference', hole=0.3,
             color_discrete_sequence=px.colors.sequential.Teal)
fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(counts))
fig.update_layout(width=400, height=400, showlegend=False, title_x=0.5, title_y=0.95, margin=dict(t=2))
fig.show()



'''直方图'''
import plotly.express as px
import re

travel_days = attr_features['travel_days'].str.extract(r'(\d+)').astype(float)
fig = px.histogram(travel_days, nbins=70, marginal='box', title='行程天数偏好分布')
fig.update_xaxes(title_text='行程天数', title_font=dict(size=14))  # 设置 x 轴标签文字大小
fig.update_yaxes(title_text='命中频率', title_font=dict(size=14))  # 设置 y 轴标签文字大小
fig.update_traces(marker=dict(opacity=0.7))  # 设置直方图的透明度
fig.update_traces(opacity=0.7)
fig.update_layout(width=600, height=400)
fig.show()


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import plotly.express as px

fig = px.histogram(attr_features, x='travel_rfm', nbins=35, marginal='box', title='度假RFM分布')
fig.update_xaxes(title_text='度假RFM', title_font=dict(size=14))  # 设置 x 轴标签文字大小
fig.update_yaxes(title_text='命中频率', title_font=dict(size=14))  # 设置 y 轴标签文字大小
fig.update_traces(marker=dict(opacity=0.7))  # 设置直方图的透明度
fig.update_traces(opacity=0.7)
fig.update_layout(width=600, height=400)
fig.show()


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

'''数据获取'''
import pandas as pd

browsing_info = pd.read_csv(r"D:\****\tmp_user_browsing_info.csv", encoding='utf-16', sep='\t', na_values='\\N')
browsing_info['call_date'] = pd.to_datetime(browsing_info['call_date'])
browsing_info['visit_date'] = pd.to_datetime(browsing_info['visit_date'])
browsing_info

indicators = pd.read_csv(r"D:\****\tmp_user_behavior_indicators.csv", encoding='utf-16', sep='\t', na_values='\\N')
indicators['call_date'] = pd.to_datetime(indicators['call_date'])
indicators['first_visit_date'] = pd.to_datetime(indicators['first_visit_date'])
indicators['last_visit_date'] = pd.to_datetime(indicators['last_visit_date'])
indicators



'''用户命中次数分布'''
import plotly.express as px

hit = indicators.groupby('cust_id')['call_date'].count().reset_index()
hit.columns = ['cust_id', 'hit_num']
hit_counts = hit['hit_num'].value_counts()
fig = px.pie(hit_counts, values=hit_counts.values, names=hit_counts.index, hole=0.3,
             color_discrete_sequence=px.colors.sequential.Teal)
fig.update_traces(textinfo='percent+label+value', pull=[0.1]+[0] * len(hit_counts))
fig.update_layout(width=400, height=400, showlegend=False)
fig.update_traces(rotation=90)
fig.show()


'''命中前有无浏览'''
import plotly.express as px

counts = indicators['browsing_flag'].value_counts()
fig = px.pie(counts, values=counts.values, names=counts.index, hole=0.3,
             color_discrete_sequence=px.colors.sequential.Teal)
fig.update_traces(textinfo='percent+label+value', pull=[0.1]+[0] * len(counts))
fig.update_layout(width=420, height=420, showlegend=False)
fig.show()


'''命中前的访问间隔'''
import plotly.express as px

# 第一次访问间隔
indicators['time_to_first_visit'] = (indicators['call_date'] - indicators['first_visit_date']).dt.days
fig = px.histogram(indicators, x='time_to_first_visit', nbins=20, marginal='box', title='第一次访问间隔')
fig.update_xaxes(title_text='命中前初次访问时间间隔/天数', title_font=dict(size=14), dtick=1)  # 设置 x 轴标签文字大小
fig.update_yaxes(title_text='人数', title_font=dict(size=14))  # 设置 y 轴标签文字大小
fig.update_traces(marker=dict(opacity=0.7))  # 设置直方图的透明度
fig.update_layout(width=600, height=400)
fig.show()
# 最后一次访问间隔
indicators['time_to_last_visit'] = (indicators['call_date'] - indicators['last_visit_date']).dt.days
fig = px.histogram(indicators, x='time_to_last_visit', nbins=20, marginal='box', title='最后一次访问间隔')
fig.update_xaxes(title_text='命中前末次访问时间间隔/天数', title_font=dict(size=14), dtick=1)  # 设置 x 轴标签文字大小
fig.update_yaxes(title_text='人数', title_font=dict(size=14))  # 设置 y 轴标签文字大小
fig.update_traces(marker=dict(opacity=0.7))  # 设置直方图的透明度
fig.update_layout(width=600, height=400)
fig.show()


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import plotly.express as px

# 近7日活跃天数
fig = px.histogram(indicators_3, x='active_days_in_7d', nbins=20, marginal='box', title='近7日活跃天数')
fig.update_xaxes(title_text='近7日活跃天数', title_font=dict(size=14))  # 设置 x 轴标签文字大小
fig.update_yaxes(title_text='人数', title_font=dict(size=14))  # 设置 y 轴标签文字大小
fig.update_traces(marker=dict(opacity=0.7))  # 设置直方图的透明度
fig.update_layout(width=600, height=400)
fig.show()


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import plotly.graph_objects as go

# indicators_2：有访问记录的用户数据
indicators_2 = indicators[indicators['browsing_flag']==1]


'''PV & 日均PV'''
data = [indicators_2['pv'], indicators_2['pv_daily_avg']]
labels = ['pv', 'pv_daily_avg']
# 创建箱线图
fig = go.Figure()
for i in range(len(data)):
    fig.add_trace(go.Box(y=data[i], name=labels[i], boxpoints='outliers'))
    # 在箱线图上添加文本标签
    median = data[i].median()
    q1 = data[i].quantile(0.25)
    q3 = data[i].quantile(0.75)
    min_val = data[i].min()
    max_val = data[i].max()
    text = [f'Median: {median}', f'Q1: {q1}', f'Q3: {q3}', f'Min: {min_val}', f'Max: {max_val}']
    fig.add_trace(go.Scatter(x=[i+1]*len(text), y=[median, q1, q3, min_val, max_val],
                             mode='text', text=text, textposition='bottom center'))
# 更新布局
fig.update_layout(title='Box Plot for pv and pv_daily_avg (Log Scale)', title_x=0.5,
                  yaxis=dict(title='Value', type='log'),
                  width=1000, height=450)
fig.show()


'''近7日活跃时长 & 日均活跃时长'''
data = [indicators_2['active_duration_in_7d'], indicators_2['active_duration_daily_avg']]
labels = ['active_duration_in_7d', 'active_duration_daily_avg']
# 创建箱线图
fig = go.Figure()
for i in range(len(data)):
    fig.add_trace(go.Box(y=data[i], name=labels[i], boxpoints='outliers'))
    # 在箱线图上添加文本标签
    median = data[i].median()
    q1 = data[i].quantile(0.25)
    q3 = data[i].quantile(0.75)
    min_val = data[i].min()
    max_val = data[i].max()
    text = [f'Median: {median}', f'Q1: {q1}', f'Q3: {q3}', f'Min: {min_val}', f'Max: {max_val}']
    fig.add_trace(go.Scatter(x=[i+1]*len(text), y=[median, q1, q3, min_val, max_val],
                             mode='text', text=text, textposition='bottom center'))
# 更新布局
fig.update_layout(title='Box Plot for Active_duration_in_7d and Active_duration_daily_avg (Log Scale)', title_x=0.5,
                  yaxis=dict(title='Value', type='log'),
                  width=1200, height=450)
fig.show()


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

'''浏览产品量'''
# 直方图
import plotly.figure_factory as ff

fig = ff.create_distplot([indicators_2['browsing_products_cnt']], group_labels=['浏览产品量'], bin_size=1, show_rug=False)
fig.update_xaxes(title_text='浏览产品量', title_font=dict(size=14), range=[0,20], dtick=2)  # 设置 x 轴标签文字大小
fig.update_yaxes(title_text='密度', title_font=dict(size=14))  # 设置 y 轴标签文字大小
fig.update_traces(marker=dict(opacity=0.7))  # 设置直方图的透明度
fig.update_layout(width=600, height=400)
fig.show()

# 饼图
import plotly.express as px

counts = indicators['browsing_products_cnt'].value_counts()
# 仅保留前6个最大的数据点，其他数据点合并到 "其他" 类别中
top_counts = counts.head(6)
other_count = counts[6:].sum()
top_counts['其他'] = other_count
fig = px.pie(top_counts, values=top_counts.values, names=top_counts.index, hole=0.3,
             color_discrete_sequence=px.colors.sequential.Teal)
fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(top_counts))
fig.update_layout(width=400, height=400, showlegend=False)
fig.show()



'''到达预定页数'''
# 直方图
import plotly.figure_factory as ff

fig = ff.create_distplot([indicators_2[indicators_2['browsing_products_cnt']>0]['to_booking_pages_cnt']], group_labels=['到达预定页数'], bin_size=1, show_rug=False)
fig.update_xaxes(title_text='到达预定页数', title_font=dict(size=14), range=[0,20], dtick=2)  # 设置 x 轴标签文字大小
fig.update_yaxes(title_text='密度', title_font=dict(size=14))  # 设置 y 轴标签文字大小
fig.update_traces(marker=dict(opacity=0.7))  # 设置直方图的透明度
fig.update_layout(width=600, height=400)
fig.show()

# 饼图
import plotly.express as px

counts = indicators_2[indicators_2['browsing_products_cnt']>0]['to_booking_pages_cnt'].value_counts()
# 仅保留前6个最大的数据点，其他数据点合并到 "其他" 类别中
top_counts = counts.head(6)
other_count = counts[6:].sum()
top_counts['其他'] = other_count
fig = px.pie(top_counts, values=top_counts.values, names=top_counts.index, hole=0.3,
             color_discrete_sequence=px.colors.sequential.Teal)
fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(top_counts))
fig.update_layout(width=400, height=400, showlegend=False)
fig.show()


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

'''搜索频率'''
# 直方图
import plotly.figure_factory as ff

fig = ff.create_distplot([indicators_2['search_freq']], group_labels=['搜索频率'], bin_size=1, show_rug=False)
fig.update_xaxes(title_text='搜索频率', title_font=dict(size=14), range=[0,20], dtick=2)  # 设置 x 轴标签文字大小
fig.update_yaxes(title_text='密度', title_font=dict(size=14))  # 设置 y 轴标签文字大小
fig.update_traces(marker=dict(opacity=0.7))  # 设置直方图的透明度
fig.update_layout(width=600, height=400)
fig.show()

# 饼图
import plotly.express as px

# 搜索频率
counts = indicators['search_freq'].value_counts()
top_counts = counts.head(6)
other_count = counts[6:].sum()
top_counts['其他'] = other_count
fig = px.pie(top_counts, values=top_counts.values, names=top_counts.index, hole=0.3,
             color_discrete_sequence=px.colors.sequential.Teal)
fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(top_counts))
fig.update_layout(width=400, height=400, showlegend=False)
fig.show()

# 度假产品搜索频率
indicators_3 = indicators_2[indicators_2['search_freq'] > 0]  # 有搜索历史的用户数据
counts = indicators_3['vac_search_freq'].value_counts()
top_counts = counts.head(6)
other_count = counts[6:].sum()
top_counts['其他'] = other_count
fig = px.pie(top_counts, values=top_counts.values, names=top_counts.index, hole=0.3,
             color_discrete_sequence=px.colors.sequential.Teal)
fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(top_counts))
fig.update_layout(width=400, height=400, showlegend=False)
fig.show()

# 单资源产品搜索频率
counts = indicators_3['single_search_freq'].value_counts()
top_counts = counts.head(6)
other_count = counts[6:].sum()
top_counts['其他'] = other_count
fig = px.pie(top_counts, values=top_counts.values, names=top_counts.index, hole=0.3,
             color_discrete_sequence=px.colors.sequential.Teal)
fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(top_counts))
fig.update_layout(width=400, height=400, showlegend=False)
fig.show()



'''词云图——热门搜索词'''
import jieba
from pyecharts.charts import WordCloud
import pyecharts.options as opts
from collections import Counter

# search_key分词
search_key = browsing_info[browsing_info['browsing_flag']==1]['search_key'].dropna().apply(lambda x: " ".join(jieba.cut(x)))
# 将文本按空格分割成词语，并统计每个词语的出现次数作为权重
word_list = text.split()
word_counts = Counter(word_list)

# 转换成元组列表，每个元组包含词语和词语的权重
data_pair = [(word, count) for word, count in word_counts.items()]
shape_image = "image.png"
# 创建词云图
wordcloud = (
    WordCloud()
    .add(series_name="搜索热点分析", data_pair=data_pair, word_size_range=[10, 66], shape=shape_image)
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title="搜索热点分析", title_textstyle_opts=opts.TextStyleOpts(font_size=23)
        ),
        tooltip_opts=opts.TooltipOpts(is_show=True),
    )
)
# 保存词云图到文件
wordcloud.render("词云图.html")


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# 箱线图（对数轴）——停留时间
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Box(y=indicators_3['residence_time_on_search'], name='residence_time_on_search', boxpoints='outliers'))
fig.update_layout(title='Box Plot for Residence_time_on_search',
                  yaxis=dict(title='Value', type='log'),
                  width=800, height=500)
fig.show()



# 直方图——搜索点击率
import plotly.figure_factory as ff

fig = ff.create_distplot([indicators_3['search_ctr']], group_labels=['搜索点击率'], bin_size=0.05, show_rug=False)
fig.update_xaxes(title_text='搜索点击率', title_font=dict(size=14), dtick=0.1)  # 设置 x 轴标签文字大小
fig.update_yaxes(title_text='密度', title_font=dict(size=14))  # 设置 y 轴标签文字大小
fig.update_traces(marker=dict(opacity=0.7))  # 设置直方图的透明度
fig.update_layout(width=600, height=400)
fig.show()


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import plotly.express as px

# 产品类别
columns = ['producttype_class_name', 'one_producttype_name']
for col in columns:
  counts = browsing_info[col].value_counts()
  fig = px.pie(counts, values=counts.values, names=counts.index, hole=0.3,
               color_discrete_sequence=px.colors.sequential.Teal)
  fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(counts))
  fig.update_layout(width=400, height=400, showlegend=False)
  fig.update_traces(rotation=90)
  fig.show()

# 目的地类别
columns = ['dest_one_group_name', 'dest_two_group_name']
for col in columns:
  counts = browsing_info[col].value_counts()
  # 仅保留前10个最大的数据点，其他数据点合并到 "其他" 类别中
  top_counts = counts.head(10)
  other_count = counts[10:].sum()
  top_counts['其他'] = other_count
  fig = px.pie(top_counts, values=top_counts.values, names=top_counts.index, hole=0.3,
               color_discrete_sequence=px.colors.sequential.Teal)
  fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(top_counts))
  fig.update_layout(width=400, height=400, showlegend=False)
  fig.show()


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# 直方图——行程天数
import plotly.figure_factory as ff

fig = ff.create_distplot([indicators_2['max_duration'].dropna()], group_labels=['浏览产品的平均行程天数'], bin_size=2, show_rug=False)
fig.update_xaxes(title_text='浏览产品的平均行程天数', title_font=dict(size=14), dtick=10)  # 设置 x 轴标签文字大小
fig.update_yaxes(title_text='密度', title_font=dict(size=14))  # 设置 y 轴标签文字大小
fig.update_traces(marker=dict(opacity=0.7))  # 设置直方图的透明度
fig.update_layout(width=600, height=400)
fig.show()

# 箱线图——行程天数
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Box(y=indicators_2['max_duration'], name='max_duration', boxpoints='outliers'))
fig.update_layout(title='Box Plot for Max_duration',
                  yaxis=dict(title='Value', type='log'),
                  width=600, height=400)
fig.show()


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

'''词云图'''
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 产品名称分组去重，分词
route_name = browsing_info[browsing_info['browsing_flag']==1].groupby('cust_id')['route_name'].apply(lambda x: x.drop_duplicates()).reset_index()
route_name = route_name['route_name'].dropna().apply(lambda x: " ".join(jieba.cut(x)))
# 设置停用词列表
stop_words = set([",", "、", "<", ">", "的", "是", " ", "丨", "【", "】", "+", "/",
                  "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                  "国内", "国际", "火车票", "机票", "酒店", "商旅", "散", "客票", "专用", "含",
                  "日", "游", "日游", "门票", "大", "晚", "人"])
# 将所有分词结果合并成一个字符串
text = " ".join(route_name.tolist())
# 创建词云对象，指定停用词
wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=stop_words, font_path="/opt/****/jupyter/****/tmp_data/simhei.ttf", collocations=False).generate(text)
# 绘制词云图
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')  # 关闭坐标轴
plt.show()



'''饼图'''
import plotly.express as px

counts = indicators['shopping_preference'].value_counts()
fig = px.pie(counts, values=counts.values, names=counts.index.map({0:"无购物偏好",1:"有购物偏好"}), hole=0.3,
             color_discrete_sequence=px.colors.sequential.Teal)
fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(counts))
fig.update_layout(width=400, height=400, showlegend=False)
fig.show()


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# 直方图——平均满意度
import plotly.figure_factory as ff

fig = ff.create_distplot([indicators_2['prd_satisfaction'].dropna()], group_labels=['平均满意度'], bin_size=2, show_rug=False)
fig.update_xaxes(title_text='平均满意度', title_font=dict(size=14), dtick=2, range=[60,100])  # 设置 x 轴标签文字大小
fig.update_yaxes(title_text='密度', title_font=dict(size=14))  # 设置 y 轴标签文字大小
fig.update_traces(marker=dict(opacity=0.7))  # 设置直方图的透明度
fig.update_layout(width=600, height=400)
fig.show()


# 饼图——最大总评级别
import plotly.express as px

counts = indicators['prd_comp_grade_level'].value_counts()
fig = px.pie(counts, values=counts.values, names=counts.index, hole=0.3,
             color_discrete_sequence=px.colors.sequential.Teal)
fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(counts))
fig.update_layout(width=400, height=400, showlegend=False)
fig.show()


# 饼图——优惠券领取量
import plotly.express as px

counts = indicators['collect_coupons_cnt'].value_counts()
fig = px.pie(counts, values=counts.values, names=counts.index, hole=0.3,
             color_discrete_sequence=px.colors.sequential.Teal)
fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(counts))
fig.update_layout(width=400, height=400, showlegend=False)
fig.show()


# 箱线图
import plotly.graph_objects as go

columns = ['lowest_price','prd_remark_amount','prd_essence_amount','prd_coupon_amount','prd_money_amount','prd_photo_amount']
for col in columns:
    fig = go.Figure()
    fig.add_trace(go.Box(y=indicators_2[col], name=col, boxpoints='outliers'))
    fig.update_layout(yaxis=dict(title='Value', type='log'),
                        width=800, height=400)
    fig.show()


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

'''数据获取'''
import subprocess as sbs
sbs.run('source /etc/profile; hadoop fs -getmerge hdfs://emr-cluster/user/****/warehouse/tmp_access_path /opt/****/jupyter/****/tmp_data/tmp_access_path.csv', shell=True)

import pandas as pd
colnames = ['cust_id', 'call_date', 'visit_date', 'access_path']
access_path = pd.read_csv("/opt/****/jupyter/****/tmp_data/tmp_access_path.csv", encoding='utf-8', sep=chr(1), names=colnames, na_values='\\N')
access_path


'''路径分析——桑基图'''
import plotly.graph_objects as go

# 将路径中“首页=10.61.0”替换为“首页”
access_path['access_path'] = access_path['access_path'].str.replace(r'=10.61.0', '', regex=True)
# 统计每个链接的出现频率
link_frequencies = access_path['access_path'].str.split('-').explode().value_counts().to_dict()
# 拆分访问路径并为每个路径元素创建唯一编号
path_elements = access_path['access_path'].str.split('-').explode().unique()
node_ids = {element: i for i, element in enumerate(path_elements)}
# 创建节点列表和边列表，并记录每个节点的频率
nodes = [{'label': element, 'frequency': link_frequencies.get(element, 0)} for element in path_elements]
edges = []

# 构建桑基图的节点和边
for path in access_path['access_path']:
    path_elements = path.split('-')
    for i in range(len(path_elements) - 1):
        source_node = node_ids[path_elements[i]]
        target_node = node_ids[path_elements[i + 1]]
        edges.append((source_node, target_node))

# 创建桑基图
fig = go.Figure(go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=[f"{node['label']} ({node['frequency']})" for node in nodes],  # 在标签中包含频率信息
    ),
    link=dict(
        source=[edge[0] for edge in edges],
        target=[edge[1] for edge in edges],
        value=[link_frequencies[nodes[node[0]]['label']] for node in edges],  # 设置边的值为链接的频率
    )
))

# 设置节点标签的位置
# fig.update_traces(textposition='middle')

# 设置图形布局和标题
fig.update_layout(title="用户访问路径桑基图（按频率）")
fig.write_html("sankey.html")
fig.show()

