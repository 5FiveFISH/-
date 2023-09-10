# <font color = 'green' >机器人外呼命中群体的画像分析</font>
<br>

## <font color = 'blue' >一、项目描述</font>

### **1. 背景描述**  
&emsp;&emsp;机器人外呼是某旅游平台为了维护用户，提高用户留存率和转化率的一项日常业务运营工作。为了提高用户维护效率，降低维护工作成本，需要有针对性地筛选最有维护价值的目标人群进行维护，实现效率和价值最大化。  
&emsp;&emsp;根据不同算法模型筛选出目标用户群体，对这部分人群进行机器人外呼，得到外呼命中与否的结果，结果保存在数据库中。外呼命中是指通过智能外呼得到用户有出行或平台下单意向的真实反馈。  

### **2. 项目内容**
&emsp;&emsp;该项目选取机器人外呼命中人群，基于用户数据和平台流量数据，对该部分人群进行画像分析，分析命中用户的行为特征，为业务运营提供数据支持，优化维护策略。  
&emsp;&emsp;**主要工作步骤如下：**  
1. **数据库取数：** 导出外呼命中群体名单，以及命中人群的基本信息和流量行为数据；  
2. **画像分析：** 分析命中人群的共性特征，分析用户在命中前的浏览行为特征，构建用户画像；
3. **结论与建议：** 总结数据分析结果，给出维护策略，为业务运营提供见解。

### **3. 分析思路**
+ ***地理位置：*** 分析用户的地理位置信息，了解用户来自哪些省份、城市。这有助于定位受众，针对特定地区推出营销活动。
+ ***年龄和性别：*** 分析用户的年龄和性别分布，以便针对不同年龄段和性别的用户定制推广活动和服务。
+ ***家庭状况：*** 分析用户的家庭状况，例如单身、已婚、有无子女等，以便针对不同家庭类型提供不同的旅游方案。
+ ***兴趣爱好：*** 了解用户的兴趣爱好，例如喜欢的旅游类型、活动偏好、旅游目的地偏好等，从而提供更符合用户兴趣的旅游推荐。
+ ***消费习惯：*** 分析用户的消费习惯，包括预算范围、旅游花费、购物偏好等，有助于优化产品和服务的定价策略。
+ ***旅游频率*：** 了解用户的旅游频率，即用户平均多久会进行一次旅行。这有助于计划和推出季节性促销活动。
+ ***平台使用行为：*** 分析用户在平台上的行为，例如浏览历史、搜索偏好、点击率等，以优化用户体验和个性化推荐。
+ ***设备使用：*** 分析用户使用的设备类型，例如移动设备还是桌面设备，以优化平台的响应性和用户体验。
+ ***搜索关键词分析：*** 分析用户在平台上的搜索关键词，从中获取关于用户需求和兴趣的信息。
+ ***路径分析：*** 分析用户在平台的浏览轨迹，有助于发现高频的访问路径，以优化平台页面展示和内容推荐。
+ ***... ...***

### **4. 特征选取**
- **用户属性维度**  
基本信息：会员类型，会员星级，年龄，性别，地理位置，注册时间，添加企微时间，单身/已婚  
家庭状况：有无子女，有无老人  
心理特征（价格敏感度），兴趣爱好，购买能力
- **用户行为维度**  
用户活跃度：近7日活跃时长、近7日活跃天数、近7日活跃次数  
浏览历史：浏览产品类型（单资源产品/度假产品），浏览产品量，每种产品类型浏览产品量，浏览时间偏好（日期、时间段），停留时间，pv  
搜索偏好：搜索关键词、频率、搜索结果的点击率、搜索结果页停留时间  
点击：到达预定页数  
路径分析：浏览路径（通过session访问顺序提取路径）  
浏览偏好：目的地偏好（一级、二级区域），产品偏好（跟团游/自助游...），旅行天数偏好，产品满意度偏好，优惠偏好，购物偏好（产品包含购物/纯玩）  
设备使用：pc/m站、ios、安卓  

<br>

## <font color = 'blue' >二、导数</font>
### **1. 提取机器人外呼命中用户** 
&emsp;&emsp;基于机器人外呼结果表，将模型1和模型4命中的用户筛选出来，提取该部分用户的会员ID和接通时间，数据时间范围为2023.07.01-2023.08.30。
``` sql
-- 选取机器人外呼命中用户
drop table if exists tmp_call_label_cust;
create table tmp_call_label_cust as
select cust_id, answer_time, to_date(answer_time) call_date from dw.kn1_fe_cust_poi_predict_call_result_detail_v2
where dt >= '20230701' and type in (1, 4) and answer_flag=1 and label=1     -- 模型1、4命中人群
    and cust_id in (select distinct cust_id from dw.kn1_usr_cust_attribute);    -- 剔除已注销用户
```
### **2. 提取用户属性维度特征**
&emsp;&emsp;提取用户身份属性、基本信息、心理特征、兴趣爱好特征、购买能力等特征。
``` sql
-- 用户属性维度
drop table if exists tmp_user_attribute_feature;
create table tmp_user_attribute_feature as
select
    t1.cust_id,                                                                  -- 会员ID
    t1.answer_time,                                                              -- 机器人外呼接通时间
    t1.call_date,                                                                -- 机器人外呼命中日期
    t2.cust_level,                                                               -- 会员星级
    t2.cust_type,                                                                -- 会员类型：1 老带新新会员,2 新会员(新客户),3 老会员(新客户),4 老会员老客户,-1 其他
    t2.cust_group_type,                                                          -- 会员类型（1：普通散客；2：团队成员；3：团队会员）
    t2.is_office_weixin,                                                         -- 是否企业微信用户:0否 1是
    if(t1.call_date>t2.rg_time, datediff(t1.call_date, t2.rg_time)+1, 0) rg_time,-- 注册时间/天
    if(t1.call_date>t2.office_weixin_time and t2.office_weixin_time is not null, datediff(t1.call_date, t2.office_weixin_time)+1, 0) office_weixin_time,-- 添加企业微信时间/天
    sex,                                                                         -- 性别
    age,                                                                         -- 年龄
    age_group,                                                                   -- 年龄段
    user_city,                                                                   -- 所在城市
    user_province,                                                               -- 所在省
    access_channel_cnt,                                                          -- 可触达渠道数
    access_channels,                                                             -- 可触达渠道
    is_single,                                                                   -- 是否单身 0-否 1-是
    elderly_num,                                                                 -- 家庭中老人人数
    child_mum,                                                                   -- 家庭中小孩人数
    prd_price_sensitivity,                                                       -- 产品价格敏感度
    schedule_domestic_flight,                                                    -- 提前预订时间（国内机票）
    schedule_domestic,                                                           -- 提前预订时间（国内）
    schedule_abroad_flight,                                                      -- 提前预订时间（国际机票）
    schedule_abroad,                                                             -- 提前预订时间（国际）
    transport_type_preference,                                                   -- 交通偏好-- 交通类型偏好
    hobbie_hotel_lvl,                                                            -- 住宿偏好-- 酒店档次偏好
    love_play_preference,                                                        -- 产品类型偏好-- 爱玩偏好
    hobbie_dest_class,                                                           -- 产品类型偏好-- 目的地大类偏好
    travel_people,                                                               -- 出行安排偏好-- 出行人员构成倾向
    travel_days,                                                                 -- 出行安排偏好-- 行程天数
    start_timebucket_preference,                                                 -- 出行时间偏好-- 出行时间段偏好
    marketing_preference_degree,                                                 -- 营销偏好-- 促销活动偏好程度
    marketing_type_preference_degree,                                            -- 营销偏好-- 促销活动类型偏好
    travel_rfm                                                                   -- 购买能力-- 用户商业价值（度假RFM）
from tmp_call_label_cust t1
left join (
    -- 会员属性
    select
        cust_id, cust_type, cust_level, to_date(rg_time) rg_time, cust_group_type, is_office_weixin, to_date(office_weixin_time) office_weixin_time
    from dw.kn1_usr_cust_attribute
    where cust_id in (select distinct cust_id from tmp_call_label_cust)
) t2 on t2.cust_id = t1.cust_id

-- 基本属性
left join(
    -- 个人信息-- 性别
    select user_id, feature_name as sex from dw.ol_rs_meta_feature
    where dt='20230830' and one_class_name='基本属性' and three_class_name = '性别'
        and user_id in (select distinct cust_id from tmp_call_label_cust)
) t3 on t3.user_id = t1.cust_id
left join(
    -- 个人信息-- 年龄
    select user_id, feature_value as age from dw.ol_rs_meta_feature
    where dt='20230830' and one_class_name='基本属性' and three_class_name = '年龄'
        and user_id in (select distinct cust_id from tmp_call_label_cust)
) t4 on t4.user_id = t1.cust_id
left join(
    -- 个人信息-- 年龄段
    select user_id, feature_name as age_group from dw.ol_rs_meta_feature
    where dt='20230830' and one_class_name='基本属性' and three_class_name = '年龄段'
        and user_id in (select distinct cust_id from tmp_call_label_cust)
) t5 on t5.user_id = t1.cust_id
left join(
    -- 个人信息-- 所在城市
    select user_id, feature_name as user_city from dw.ol_rs_meta_feature
    where dt='20230830' and one_class_name='基本属性' and three_class_name = '所在城市'
        and user_id in (select distinct cust_id from tmp_call_label_cust)
) t6 on t6.user_id = t1.cust_id
left join(
    -- 个人信息-- 所在省
    select user_id, feature_name as user_province from dw.ol_rs_meta_feature
    where dt='20230830' and one_class_name='基本属性' and three_class_name = '所在省'
        and user_id in (select distinct cust_id from tmp_call_label_cust)
) t7 on t7.user_id = t1.cust_id
left join (
    -- 个人信息-- 可触达渠道
    select 
        user_id, 
        count(1) as access_channel_cnt,
        concat_ws(',', collect_set(three_class_name)) as access_channels
    from dw.ol_rs_meta_feature_basic_info_access_channel
    where feature_value = 1 and user_id in (select distinct cust_id from tmp_call_label_cust)
    group by user_id
) t8 on t8.user_id = t1.cust_id
left join (
    -- 基本信息-- 家庭信息
    select 
        user_id,
        if(max(case when three_class_name='家庭构成' and feature_name in ('单身', '朋友/闺蜜') then 1 else 0 end)=1,1,0) is_single,
        sum(case when three_class_name='老人年龄' then 1 else 0 end) elderly_num, 
        sum(case when three_class_name='儿童年龄' then 1 else 0 end) child_mum
    from dw.ol_rs_meta_feature
    where dt='20230830' and two_class_name='家庭信息' and user_id in (select distinct cust_id from tmp_call_label_cust)
    group by user_id
) t9 on t9.user_id = t1.cust_id

-- 心理特征
left join (
    -- 价格敏感度-- 产品价格敏感度
    select user_id, feature_name prd_price_sensitivity from dw.ol_rs_meta_feature
    where dt='20230830' and one_class_name='心理特征' and three_class_name='产品价格敏感度'
        and user_id in (select distinct cust_id from tmp_call_label_cust)
) t10 on t10.user_id = t1.cust_id
left join (
    -- 行程规划习惯-- 提前预订时间（国内机票）
    select user_id, feature_name schedule_domestic_flight from dw.ol_rs_meta_feature
    where dt='20230830' and one_class_name='心理特征' and three_class_name='提前预订时间（国内机票）'
        and user_id in (select distinct cust_id from tmp_call_label_cust)
) t11 on t11.user_id = t1.cust_id
left join (
    -- 行程规划习惯-- 提前预订时间（国内）
    select user_id, feature_name schedule_domestic from dw.ol_rs_meta_feature
    where dt='20230830' and one_class_name='心理特征' and three_class_name='提前预订时间（国内）'
        and user_id in (select distinct cust_id from tmp_call_label_cust)
) t12 on t12.user_id = t1.cust_id
left join (
    -- 行程规划习惯-- 提前预订时间（国际机票）
    select user_id, feature_name schedule_abroad_flight from dw.ol_rs_meta_feature
    where dt='20230830' and one_class_name='心理特征' and three_class_name='提前预订时间（国际机票）'
        and user_id in (select distinct cust_id from tmp_call_label_cust)
) t13 on t13.user_id = t1.cust_id
left join (
    -- 行程规划习惯-- 提前预订时间（国际）
    select user_id, feature_name schedule_abroad from dw.ol_rs_meta_feature
    where dt='20230830' and one_class_name='心理特征' and three_class_name='提前预订时间（国际）'
        and user_id in (select distinct cust_id from tmp_call_label_cust)
) t14 on t14.user_id = t1.cust_id

--  兴趣爱好特征
left join (
    --交通偏好-- 交通类型偏好
    select user_id, feature_name transport_type_preference
    from (
        select user_id, feature_name, row_number() over (partition by user_id order by feature_value desc) rank
        from dw.ol_rs_meta_feature
        where dt='20230830' and one_class_name='兴趣爱好特征' and three_class_name='交通类型偏好'
            and user_id in (select distinct cust_id from tmp_call_label_cust)
    ) t where rank = 1
) t15 on t15.user_id = t1.cust_id
left join (
    -- 住宿偏好-- 酒店档次偏好
    select user_id, feature_name hobbie_hotel_lvl
    from (
        select user_id, feature_name, row_number() over (partition by user_id order by feature_value desc) rank
        from dw.ol_rs_meta_feature
        where dt='20230830' and one_class_name='兴趣爱好特征' and three_class_name='酒店档次偏好'
            and user_id in (select distinct cust_id from tmp_call_label_cust)
    ) t where rank = 1
) t16 on t16.user_id = t1.cust_id
left join (
    -- 产品类型偏好-- 爱玩偏好
    select user_id, concat_ws(',', collect_set(feature_name)) love_play_preference 
    from dw.ol_rs_meta_feature
    where dt='20230830' and one_class_name='兴趣爱好特征' and three_class_name='爱玩偏好'
        and user_id in (select distinct cust_id from tmp_call_label_cust)
    group by user_id
) t17 on t17.user_id = t1.cust_id
left join (
    -- 产品类型偏好-- 目的地大类偏好
    select user_id, feature_name hobbie_dest_class
    from (
        select user_id, feature_name, row_number() over (partition by user_id order by feature_value desc) rank
        from dw.ol_rs_meta_feature
        where dt='20230830' and one_class_name='兴趣爱好特征' and three_class_name='目的地大类偏好'
            and user_id in (select distinct cust_id from tmp_call_label_cust)
    ) t where rank = 1
) t18 on t18.user_id = t1.cust_id
left join (
    -- 出行安排偏好-- 出行人员构成倾向
    select user_id, feature_name travel_people
    from (
        select user_id, feature_name, row_number() over (partition by user_id order by feature_value desc) rank
        from dw.ol_rs_meta_feature
        where dt='20230830' and one_class_name='兴趣爱好特征' and three_class_name='出行人员构成倾向'
            and user_id in (select distinct cust_id from tmp_call_label_cust)
    ) t where rank = 1
) t19 on t19.user_id = t1.cust_id
left join (
    -- 出行安排偏好-- 行程天数偏好
    select user_id, feature_name travel_days
    from (
        select user_id, feature_name, row_number() over (partition by user_id order by feature_value desc) rank
        from dw.ol_rs_meta_feature
        where dt='20230830' and one_class_name='兴趣爱好特征' and three_class_name='行程天数偏好'
            and user_id in (select distinct cust_id from tmp_call_label_cust)
    ) t where rank = 1
) t20 on t20.user_id = t1.cust_id
left join (
    -- 出行时间偏好-- 出行时间段偏好
    select user_id, feature_name start_timebucket_preference
    from (
        select user_id, feature_name, row_number() over (partition by user_id order by feature_value desc) rank
        from dw.ol_rs_meta_feature
        where dt='20230830' and one_class_name='兴趣爱好特征' and three_class_name='出行时间段偏好'
            and user_id in (select distinct cust_id from tmp_call_label_cust)
    ) t where rank = 1
) t21 on t21.user_id = t1.cust_id
left join (
    -- 营销偏好-- 促销活动偏好程度
    select user_id, feature_name marketing_preference_degree from dw.ol_rs_meta_feature
    where dt='20230830' and one_class_name='兴趣爱好特征' and three_class_name='促销活动偏好程度'
        and user_id in (select distinct cust_id from tmp_call_label_cust)
) t22 on t22.user_id = t1.cust_id
left join (
    -- 营销偏好-- 促销活动类型偏好
    select user_id, feature_name marketing_type_preference_degree
    from (
        select user_id, feature_name, row_number() over (partition by user_id order by feature_value desc) rank
        from dw.ol_rs_meta_feature
        where dt='20230830' and one_class_name='兴趣爱好特征' and three_class_name='促销活动类型偏好'
            and user_id in (select distinct cust_id from tmp_call_label_cust)
    ) t where rank = 1
) t23 on t23.user_id = t1.cust_id

-- 购买能力
left join (
    -- 购买能力-- 用户商业价值（度假RFM）
    select user_id, feature_name travel_rfm from dw.ol_rs_meta_feature
    where dt='20230830' and one_class_name='购买能力' and three_class_name='RFM值'
        and user_id in (select distinct cust_id from tmp_call_label_cust)
) t24 on t24.user_id = t1.cust_id;
```
### **3. 提取用户行为维度特征**
&emsp;&emsp;基于流量域，筛选命中用户的相关浏览明细。
``` sql
-- 用户浏览行为明细
drop table if exists tmp_user_browsing_info;
create table tmp_user_browsing_info as
select
     a.cust_id                                              -- 会员ID
    ,a.call_date                                            -- 机器人外呼命中日期
    ,b.visit_date                                           -- 访问日期
    ,if(b.visit_date between date_sub(a.call_date, 6) and a.call_date, 1, 0) browsing_flag  -- 近七日是否浏览 0-否 1-是
    ,b.operating_system                                     -- 操作系统
    ,b.visitor_trace                                        -- 访客标记
    ,b.product_id                                           -- 产品ID
    ,b.residence_time                                       -- 页面停留时间
    ,b.book_id                                              -- 预订页ID
    ,b.search_key                                           -- 搜索词
    ,case when b.search_key like '%清湖古镇%' or b.search_key like '%日游%' then 1
        when b.search_key rlike '.*(票|酒店).*' or b.search_key is null or lower(b.search_key)='null' then 0 
        else 1 
    end search_key_type                                     -- 搜索词类型 1-度假产品 0-其他
    ,b.is_click                                             -- 搜索结果是否点击 0-否 1-是
    ,c.access_path                                          -- 当天访问路径
    ,d.route_name                                           -- 浏览产品名称
    ,d.max_duration                                         -- 最大行程天数
    ,d.producttype_class_name                               -- 浏览产品大类
    ,d.one_producttype_name                                 -- 浏览产品一级品类
    ,d.dest_class_name                                      -- 产品目的地大类
    ,d.dest_one_group_name                                  -- 产品目的地一级分组
    ,d.dest_two_group_name                                  -- 产品目的地二级分组
    ,d.shopping_preference                                  -- 购物偏好 0-否 1-是
    ,e.lowest_price                                         -- 产品最低价
    ,f.f_satisfaction                                       -- 产品平均满意度
    ,f.f_comp_grade_level                                   -- 总评级别
    ,f.f_remark_amount                                      -- 点评数目
    ,f.f_essence_amount                                     -- 精华点评数目
    ,f.f_coupon_amount                                      -- 返抵用券金额
    ,f.f_money_amount                                       -- 返现金额
    ,f.f_photo_amount                                       -- 图片数目
    ,nvl(g.collect_coupons_status, 0) collect_coupons_status-- 优惠券领取状态 1-成功 0-未领取/失败
from tmp_call_label_cust a
left join (
    select
        vt_mapuid
        ,to_date(operate_time) visit_date
        ,operating_system
        ,visitor_trace
        ,product_id
        ,residence_time
        ,book_id
        ,case when search_key is null and scan_type='搜索' then regexp_extract(visit_url, 'keyword=(.*?)\/search_type=', 1)
            when search_key is not null then search_key else NULL
        end search_key
        ,case when scan_type='搜索' and position_id is not null then 1 else 0 end is_click
    from (
        select distinct 
            vt_mapuid,operate_time,visitor_trace,product_id,residence_time,position_id,book_id,scan_type,search_key,visit_url
            ,case when lower(operating_system) rlike '.*(android|windows|devtools).*' then 'android' else 'ios' end operating_system
        from dw.kn1_traf_app_day_detail
        where dt between '20230625' and '20230830' and to_date(operate_time) between '2023-06-25' and '2023-08-30' 
            and vt_mapuid in (select distinct cust_id from tmp_call_label_cust)
        union
        select distinct 
            vt_mapuid,operate_time,visitor_trace,product_id,residence_time,position_id,book_id,scan_type,search_key,visit_url
            ,'pc/m' operating_system
        from dw.kn1_traf_day_detail
        where dt between '20230625' and '20230830' and to_date(operate_time) between '2023-06-25' and '2023-08-30' 
            and vt_mapuid in (select distinct cust_id from tmp_call_label_cust)
    ) t
) b on b.vt_mapuid = a.cust_id
left join (
    -- 获取访问路径
    select vt_mapuid, visit_date, array(concat_ws('-', collect_list(page_level_1))) access_path
    from (
        select distinct vt_mapuid, operate_time, to_date(operate_time) visit_date, ord, page_level_1 from dw.kn1_traf_app_day_detail
        where dt between '20230625' and '20230830' and to_date(operate_time) between '2023-06-25' and '2023-08-30' 
            and vt_mapuid in (select distinct cust_id from tmp_call_label_cust)
        order by vt_mapuid, ord, operate_time
    ) tmp1
    group by vt_mapuid, visit_date
    union all
    select vt_mapuid, visit_date, array(concat_ws('-', collect_list(page_level_1))) access_path
    from (
        select distinct vt_mapuid, operate_time, to_date(operate_time) visit_date, ord, page_level_1 from dw.kn1_traf_day_detail
        where dt between '20230625' and '20230830' and to_date(operate_time) between '2023-06-25' and '2023-08-30' 
            and vt_mapuid in (select distinct cust_id from tmp_call_label_cust)
        order by vt_mapuid, ord, operate_time
    ) tmp2
    group by vt_mapuid, visit_date
) c on c.vt_mapuid = b.vt_mapuid and c.visit_date = b.visit_date
left join (
    select distinct 
        route_id, route_name, max_duration
        ,case when one_producttype_name like '门票' then '单资源产品' else producttype_class_name end producttype_class_name
        ,one_producttype_name, dest_class_name, dest_one_group_name, dest_two_group_name
        ,case when route_name rlike '.*(0购物|无购物|纯玩).*' then 0 else 1 end shopping_preference  -- 购物偏好 0-否 1-是
    from dw.kn2_dim_route_product_sale
) d on d.route_id = b.product_id
left join (
    -- 产品最低价
    select distinct route_id, lowest_price from dw.kn1_prd_route
) e on e.route_id = b.product_id
left join (
    -- 获取产品关联的满意度和评价总人数
    select 
        t1.f_product_id, f_satisfaction / 1000000 f_satisfaction, f_comp_grade_level, f_remark_amount, 
        f_essence_amount, f_coupon_amount, f_money_amount, f_photo_amount
    from dw.ods_ncs_t_nremark_stat_product t1
    join (
        select f_product_id, max(f_update_time) max_update_time
        from dw.ods_ncs_t_nremark_stat_product
        group by f_product_id
    ) t2 ON t1.f_product_id = t2.f_product_id and t1.f_update_time = t2.max_update_time
) f on f.f_product_id = b.product_id
left join (
    -- 用户领券情况
    select distinct cust_id, collect_coupons_status, to_date(operate_time) visit_date
    from dw.ods_crmmkt_mkt_scene_clear_intention_cust_transform
    where to_date(operate_time) between '2023-06-25' and '2023-08-30' and collect_coupons_status = 1 
        and cust_id in (select distinct cust_id from tmp_call_label_cust)
) g on g.cust_id = b.vt_mapuid and g.visit_date = b.visit_date;
```
&emsp;&emsp;基于上面用户的浏览明细，计算用户在命中日期近7日内的行为特征。
``` sql
-- 用户行为维度
drop table if exists tmp_user_behavior_indicators;
create table tmp_user_behavior_indicators as
select
     a.cust_id                                                          -- 会员ID
    ,a.call_date                                                        -- 命中日期
    ,case when b.cust_id is not null then 1 else 0 end browsing_flag    -- 用户命中近7日内有无浏览记录 0-否 1-是
    ,b.first_visit_date                                                 -- 第一次浏览日期
    ,b.last_visit_date                                                  -- 最后一次浏览日期
    ,b.active_days_in_7d                                                -- 近7日活跃天数
    ,b.pv                                                               -- 近7日pv
    ,b.pv_daily_avg                                                     -- 日均pv
    ,b.active_duration_in_7d                                            -- 近7日活跃时长
    ,b.active_duration_daily_avg                                        -- 日均活跃时长
    ,b.browsing_products_cnt                                            -- 浏览产品数量
    ,b.to_booking_pages_cnt                                             -- 到达预定页数
    ,b.search_freq                                                      -- 搜索频率
    ,b.residence_time_on_search                                         -- 搜索结果页停留时长
    ,b.search_ctr                                                       -- 搜索结果点击率
    ,b.vac_search_freq                                                  -- 度假产品搜索频率
    ,b.single_search_freq                                               -- 单资源产品搜索频率
    ,b.max_duration                                                     -- 浏览产品的平均行程天数
    ,b.vac_browsing_cnt                                                 -- 度假产品浏览量
    ,b.single_browsing_cnt                                              -- 单资源产品浏览量
    ,b.shopping_preference                                              -- 消费偏好 0-否 1-是
    ,b.shopping_pref_degree                                             -- 消费偏好程度
    ,b.lowest_price                                                     -- 浏览产品的平均最低价
    ,b.prd_satisfaction                                                 -- 浏览产品的平均满意度
    ,b.prd_comp_grade_level                                             -- 浏览产品的最大总评级别
    ,b.prd_remark_amount                                                -- 浏览产品的平均点评数目
    ,b.prd_essence_amount                                               -- 浏览产品的平均精华点评数目
    ,b.prd_coupon_amount                                                -- 浏览产品的平均返抵用券金额
    ,b.prd_money_amount                                                 -- 浏览产品的平均返现金额
    ,b.prd_photo_amount                                                 -- 浏览产品的平均音频数目
    ,b.collect_coupons_cnt                                              -- 优惠券领取量
from tmp_call_label_cust a
left join (
    select  
        cust_id
        ,call_date
        ,min(visit_date) first_visit_date
        ,max(visit_date) last_visit_date
        ,count(distinct visit_date) active_days_in_7d
        ,count(visitor_trace) pv
        ,round(count(visitor_trace) / count(distinct visit_date), 4) pv_daily_avg
        ,sum(residence_time) active_duration_in_7d
        ,round(sum(residence_time) / count(distinct visit_date), 4) active_duration_daily_avg
        ,count(distinct product_id) browsing_products_cnt
        ,count(book_id) to_booking_pages_cnt
        ,count(search_key) search_freq             -- 搜索频率
        ,sum(case when search_key is not null then residence_time else 0 end) residence_time_on_search    -- 搜索结果停留时间
        ,sum(is_click) / count(search_key) search_ctr  -- 搜索点击率
        ,sum(search_key_type) vac_search_freq       -- 度假产品搜索频率
        ,count(search_key) - sum(search_key_type) single_search_freq   -- 单资源产品搜索频率
        ,round(avg(max_duration), 4) max_duration
        ,count(distinct case when producttype_class_name like '度假产品' then product_id else null end) vac_browsing_cnt
        ,count(distinct case when producttype_class_name like '单资源产品' then product_id else null end) single_browsing_cnt
        ,max(shopping_preference) shopping_preference
        ,nvl(round(sum(shopping_preference)/count(case when producttype_class_name like '度假产品' then product_id else null end),4),0) shopping_pref_degree
        ,round(avg(lowest_price), 4) lowest_price
        ,round(avg(f_satisfaction), 4) prd_satisfaction
        ,max(f_comp_grade_level) prd_comp_grade_level
        ,round(avg(f_remark_amount), 4) prd_remark_amount
        ,round(avg(f_essence_amount), 4) prd_essence_amount
        ,round(avg(f_coupon_amount), 4) prd_coupon_amount
        ,round(avg(f_money_amount), 4) prd_money_amount
        ,round(avg(f_photo_amount), 4) prd_photo_amount
        ,count(distinct case when collect_coupons_status = 1 then visit_date else null end) collect_coupons_cnt
    from tmp_user_browsing_info
    where browsing_flag = 1         -- 只对有浏览行为的用户计算指标
    group by cust_id, call_date
) b on b.cust_id = a.cust_id and b.call_date = a.call_date;
```
 
<br>

## <font color = 'blue' >三、画像分析</font>
### **1. 命中人群基本特征分析**  
``` python
'''数据获取'''
import pandas as pd
attr_features = pd.read_csv(r"D:\****\tmp_user_attribute_feature.csv", encoding='utf-16', sep='\t', na_values='\\N')
attr_features['answer_time'] = pd.to_datetime(attr_features['answer_time'])
attr_features['call_date'] = pd.to_datetime(attr_features['call_date'])
attr_features
```
#### **（1）命中时段分析**
``` python
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
```
&emsp;&emsp;下面展示了机器人外呼命中用户的时间分布情况，以了解不同时间段的命中情况。结果如下，  
- 7月份命中率最高的在7月10日，8月份命中率最高的在8月14日，且8月份的命中率整体高于7月份；
- 工作日的命中情况大致呈下降趋势，周一最高，周二其次，慢慢减少，周四最低；
- 命中时间段在9点\~19点，和外呼时间保持一致，其中10:00\~11:00、14:00\~16:00处于命中高峰期，9:00、13:00、19:00左右的时间命中率较低。  
<!-- ![外呼命中日期分布情况](https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/202309071135609.png "外呼命中日期分布情况") -->
<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/202309071135609.png" alt="外呼命中日期分布情况" width="600" /> <br>
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/202309071315644.png" alt="外呼命中工作日分布情况" width="600" /> <br>
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/202309071315647.png" alt="外呼命中时间段分布情况" width="600" />
</div>  

#### **（2）基本信息分析** 
``` python
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
```
&emsp;&emsp;下面展示了命中人群的性别、感情状态、年龄以及地域分布情况。占比较大的命中群体的基本特征为女性、非单身、36\~45岁，命中人群主要分布在沿海区域，江苏省（6239）、上海（3923）、北京（3713）、广东省（2960）、浙江省（2679）等地区。
<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/202309071322668.png" alt="性别" width="380" />
    <p>性别</p>
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/202309071327081.png" alt="感情状态" width="380" />
    <p>感情状态</p>
  </div>
</div>

<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/202309071328032.png" alt="年龄段" width="420" />
    <p>年龄段</p>
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/202309071329964.png" alt="年龄" width="420" />
    <p>年龄段</p>
  </div>
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/202309071329820.png" alt="外呼命中人群地域分布图" width="800" />
</div>  

#### **（3）身份属性分析** 
``` python
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
```
&emsp;&emsp;下面展示了命中人群的身份属性特征的分布情况。
- 0级会员、会员类型为其他的占比最大，1级会员、老会员老客户占比次之。命中人群的注册时间在[2, 5822]，主要分布在132天\~2621天之间，中位数在1695天。
- 87.8%的命中群体都为非企微用户，只有12.2%的人群为企微用户，其中这部分用户添加企微的时间普遍在2\~200天、900\~1000天之间，说明添加企微时间较短或较长的用户更容易被命中。
- 在命中群体中，有62.2%的用户可被短信触达，仅有7.61%的用户可被企业微信触达，这也与企微用户占比较少的结果保持一致。  
<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/202309071419419.png" alt="会员等级" width="400" />
    <p>会员等级</p>
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/202309071421787.png" alt="会员类型" width="400" />
    <p>会员类型</p>
  </div>
</div>

<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E4%BC%81%E5%BE%AE%E7%94%A8%E6%88%B7.png" alt="企微用户" width="360" />
    <p>企微用户</p>
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E5%8F%AF%E8%A7%A6%E8%BE%BE%E6%B8%A0%E9%81%93.png" alt="可触达渠道" width="380" />
    <p>可触达渠道</p>
  </div>
</div>

<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E6%B3%A8%E5%86%8C%E6%97%B6%E9%97%B4.png" alt="注册时间" width="600" />
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E6%B7%BB%E5%8A%A0%E4%BC%81%E5%BE%AE%E6%97%B6%E9%97%B4.png" alt="添加企微时间" width="600" />
  </div>
</div>

#### **（4）家庭构成分析** 
``` python
import plotly.express as px

columns = ['elderly_num', 'child_num']
for col in columns:
    counts = attr_features[col].value_counts()
    fig = px.pie(counts, values=counts.values, names=counts.index, title=col, hole=0.3,
                 color_discrete_sequence=px.colors.sequential.Teal)
    fig.update_traces(textinfo='percent+label', pull=[0.1]+[0] * len(counts))
    fig.update_layout(width=400, height=400, showlegend=False, title_x=0.5, title_y=0.95, margin=dict(t=2))
    fig.show()
```
&emsp;&emsp;下面展示了命中人群的家庭构成情况。
- 家庭中有老人会增加用户的出游意愿，从而增加命中概率，但出游意愿也会随着老人人数的增加而降低；
- 用户的出游意愿会随着家庭中老人和孩子的人数增加而降低，老人和孩子数越少，被命中的概率越大。
<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E5%AE%B6%E5%BA%AD%E4%B8%AD%E8%80%81%E4%BA%BA%E6%95%B0.png" alt="家庭中老人数" width="360" />
    <p>家庭中老人数</p>
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E5%AE%B6%E5%BA%AD%E4%B8%AD%E5%B0%8F%E5%AD%A9%E6%95%B0.png" alt="家庭中小孩数" width="400" />
    <p>家庭中小孩数</p>
  </div>
</div>

#### **（5）心理特征分析** 
``` python
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
```
&emsp;&emsp;下面展示了命中人群的心理特征分布情况。
- 命中人群对产品价格敏感度较低，其中91.4%的用户的产品价格敏感度均为低，表明对产品价格敏感度越低的用户越容易被命中，出游意向越大；
- 对于国内机票、国内产品、国际机票、国际产品这四种品类，占比最多的命中人群的提前预定时间均为较短；和其他三类不同的是，国内产品的提前预定时间占比第二的为极短（24.3%），说明有相当一部分用户对国内行程的考虑时间极短，从预定到出发的间隔极短。
<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E4%BA%A7%E5%93%81%E4%BB%B7%E6%A0%BC%E6%95%8F%E6%84%9F%E5%BA%A6.png" alt="产品价格敏感度" width="420" />
  <p>产品价格敏感度</p>
</div>
<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E6%8F%90%E5%89%8D%E9%A2%84%E5%AE%9A%E6%97%B6%E9%97%B4%EF%BC%88%E5%9B%BD%E5%86%85%E6%9C%BA%E7%A5%A8%EF%BC%89.png" alt="提前预定时间（国内机票）" width="360" />
    <p>提前预定时间（国内机票）</p>
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E6%8F%90%E5%89%8D%E9%A2%84%E5%AE%9A%E6%97%B6%E9%97%B4%EF%BC%88%E5%9B%BD%E5%86%85%EF%BC%89.png" alt="提前预定时间（国内）" width="360" />
    <p>提前预定时间（国内）</p>
  </div>
</div>
<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E6%8F%90%E5%89%8D%E9%A2%84%E5%AE%9A%E6%97%B6%E9%97%B4%E5%91%A2%EF%BC%88%E5%9B%BD%E9%99%85%E6%9C%BA%E7%A5%A8%EF%BC%89.png" alt="提前预定时间（国际机票）" width="360" />
    <p>提前预定时间（国际机票）</p>
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E6%8F%90%E5%89%8D%E9%A2%84%E5%AE%9A%E6%97%B6%E9%97%B4%EF%BC%88%E5%9B%BD%E9%99%85%EF%BC%89.png" alt="提前预定时间（国际）" width="360" />
    <p>提前预定时间（国际）</p>
  </div>
</div>

#### **（6）兴趣爱好特征分析**  
``` python
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
```
&emsp;&emsp;下面展示了命中人群的兴趣爱好特征分布情况。
- 67.3%的命中人群倾向于选择飞机作为交通工具，其次是汽车，偏好火车出行的用户最少；
- 在酒店选择方面，偏好经济型酒店的用户占比最多，为33.5%，其次是豪华型，占比为20.7%，命中群体选择酒店更倾向于经济型或者豪华型，较少选择低等级的酒店；
- 命中人群中，31.9%的用户喜欢去乐园，占比最大，其次是度假、出海/赶海、漂流，偏好滑雪、露营、房车、城市人文的用户占比较少；
- 命中人群中，绝大部分用户倾向于周边游，其次是国内游，出境游最少；
- 命中人群中，30.1%的用户偏好家庭游，占比最大，其次是爸妈游和情侣游；
- 7-8月份命中群体中，47.3%的用户偏向非寒暑假出行，且占比最多，仅有16.1%的用户偏向暑假出行，19.3%的用户偏向工作日出游；
- 绝大部分命中用户对促销活动没有偏好，且促销活动的偏好程度越低的用户更容易被命中；
- 在有促销活动偏好程度的这部分命中人群中，大多数更喜欢有抵用券的促销活动，其次是有专项立减的促销活动；
- 命中人群的偏好出游天数集中分布在2\~6天，1天和5天的人数最多。
<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E4%BA%A4%E9%80%9A%E7%B1%BB%E5%9E%8B%E5%81%8F%E5%A5%BD.png" alt="交通类型偏好" width="360" />
    <p>交通类型偏好</p>
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E9%85%92%E5%BA%97%E6%A1%A3%E6%AC%A1%E5%81%8F%E5%A5%BD.png" alt="酒店档次偏好" width="400" />
    <p>酒店档次偏好</p>
  </div>
</div>
<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E7%88%B1%E7%8E%A9%E5%81%8F%E5%A5%BD.png" alt="爱玩偏好" width="400" />
    <p>爱玩偏好</p>
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E7%9B%AE%E7%9A%84%E5%9C%B0%E5%81%8F%E5%A5%BD.png" alt="目的地偏好" width="360" />
    <p>目的地偏好</p>
  </div>
</div>
<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E5%87%BA%E8%A1%8C%E4%BA%BA%E5%91%98%E6%9E%84%E6%88%90%E5%80%BE%E5%90%91.png" alt="出行人员构成倾向" width="400" />
    <p>出行人员构成倾向</p>
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E5%87%BA%E8%A1%8C%E6%97%B6%E9%97%B4%E6%AE%B5%E5%81%8F%E5%A5%BD.png" alt="出行时间段偏好" width="350" />
    <p>出行时间段偏好</p>
  </div>
</div>
<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E4%BF%83%E9%94%80%E6%B4%BB%E5%8A%A8%E5%81%8F%E5%A5%BD%E7%A8%8B%E5%BA%A6.png" alt="促销活动偏好程度" width="360" />
    <p>促销活动偏好程度</p>
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E4%BF%83%E9%94%80%E6%B4%BB%E5%8A%A8%E7%B1%BB%E5%9E%8B%E5%81%8F%E5%A5%BD.png" alt="促销活动类型偏好" width="400" />
    <p>促销活动类型偏好</p>
  </div>
</div>
<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E8%A1%8C%E7%A8%8B%E5%A4%A9%E6%95%B0%E5%81%8F%E5%A5%BD.png" alt="行程天数偏好" width="600" />
</div>

#### **（7）购买能力分析**  
``` python
import plotly.express as px

fig = px.histogram(attr_features, x='travel_rfm', nbins=35, marginal='box', title='度假RFM分布')
fig.update_xaxes(title_text='度假RFM', title_font=dict(size=14))  # 设置 x 轴标签文字大小
fig.update_yaxes(title_text='命中频率', title_font=dict(size=14))  # 设置 y 轴标签文字大小
fig.update_traces(marker=dict(opacity=0.7))  # 设置直方图的透明度
fig.update_traces(opacity=0.7)
fig.update_layout(width=600, height=400)
fig.show()
```
&emsp;&emsp;下面展示了命中人群的度假产品消费能力RFM模型评估值的分布情况。RFM∈[3, 9]，命中人群的RFM取值集中在4\~6.5分之间，RFM值为3的用户群体人数最多。
<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E6%B6%88%E8%B4%B9%E5%95%86%E4%B8%9A%E4%BB%B7%E5%80%BCRFM%EF%BC%88%E5%BA%A6%E5%81%87%EF%BC%89.png" alt="消费商业价值RFM（度假）" width="600" />
</div>
<br>

### **2. 命中人群行为特征分析** 
``` python
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
```
&emsp;&emsp;7-8月份，98.4%的用户被命中一次，而仅有1.64%的用户被命中两次。
<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E7%94%A8%E6%88%B7%E5%91%BD%E4%B8%AD%E6%AC%A1%E6%95%B0%E5%88%86%E5%B8%83.png" alt="用户命中次数分布" width="400" />
  <p>用户命中次数分布</p>
</div>
&emsp;&emsp;命中人群中，89.2%的用户在命中前7天有APP/PC/M站的访问记录，10.8%的用户无任何访问记录。  
<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E7%94%A8%E6%88%B7%E5%91%BD%E4%B8%AD%E5%89%8D%E6%9C%89%E6%97%A0%E8%AE%BF%E9%97%AE.png" alt="用户命中前有无访问 0-无 1-有" width="350" />
  <p>用户命中前有无访问 0-无 1-有</p>
</div>
&emsp;&emsp;下图显示了用户在命中前的访问时间与命中日期之间的时间间隔的分布情况。在有访问记录的人群中，有508位用户仅在命中当天进行了初次访问，且占比最少，大多数用户在命中前一天进行初次访问，占比最多，相当一部分用户在命中当天又进行了最后一次访问。结果表明，用户的访问时间多集中在命中前1~3天和命中当天。  
<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E5%91%BD%E4%B8%AD%E5%89%8D%E5%88%9D%E6%AC%A1%E8%AE%BF%E9%97%AE%E6%97%B6%E9%97%B4%E9%97%B4%E9%9A%94.png" alt="命中前初次访问时间间隔" width="600" />
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E5%91%BD%E4%B8%AD%E5%89%8D%E6%9C%AB%E6%AC%A1%E8%AE%BF%E9%97%AE%E6%97%B6%E9%97%B4%E9%97%B4%E9%9A%94.png" alt="命中前末次访问时间间隔" width="600" />
  </div>
</div>

``` python
import plotly.express as px

# 近7日活跃天数
fig = px.histogram(indicators_3, x='active_days_in_7d', nbins=20, marginal='box', title='近7日活跃天数')
fig.update_xaxes(title_text='近7日活跃天数', title_font=dict(size=14))  # 设置 x 轴标签文字大小
fig.update_yaxes(title_text='人数', title_font=dict(size=14))  # 设置 y 轴标签文字大小
fig.update_traces(marker=dict(opacity=0.7))  # 设置直方图的透明度
fig.update_layout(width=600, height=400)
fig.show()
```
&emsp;&emsp;大多数命中人群的近7日内活跃天数为1天，其次是2天，访问时间达4\~7天的用户数很少。  
<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E8%BF%917%E6%97%A5%E6%B4%BB%E8%B7%83%E5%A4%A9%E6%95%B0.png" alt="近7日活跃天数" width="600" />
</div>

``` python
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
```
&emsp;&emsp;下图展示了用户PV数和平均每日PV数的分布情况，使用对数轴绘制箱线图，旨在更好地展示包含广泛数值范围的数据集，特别是当数据集包含极端值（较小或较大的值）时，更清晰地看到数据在不同数量级上的分布情况。对数轴上的标签值是以指数形式显示的，用于指示每个刻度的数量级，以更好地呈现数据的广度和分布。  
&emsp;&emsp;命中人群近7日内的PV数集中在[6, 29]，中位数为13，平均在26次，日均PV集中在[5, 20]，中位数为10，平均在17次。  
<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/pv.png" alt="近7日pv" width="600" />
</div>
&emsp;&emsp;命中人群近7日内的活跃时长集中在[46, 796]，中位数为209s，平均活跃时长为860s，日均活跃时长集中在[39, 571.5]，中位数为167s，平均为529s。  
<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E6%B4%BB%E8%B7%83%E6%97%B6%E9%95%BF.png" alt="近7日活跃时长" width="600" />
</div>

``` python
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
```
&emsp;&emsp;为了更直观的展示，将浏览产品量、到达预定页数、搜索频率的直方图的横轴范围限定在[0, 20]，饼图只显示占比前6的类别，且将其余类别归并到“其他”类中。  
&emsp;&emsp;命中群体中，历史7天内，未浏览产品的用户占比34.3%，大部分用户浏览产品量在1\~3个之间，平均浏览2.6个产品。  
<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E6%B5%8F%E8%A7%88%E4%BA%A7%E5%93%81%E9%87%8F.png" alt="浏览产品量" width="600" />
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E6%B5%8F%E8%A7%88%E4%BA%A7%E5%93%81%E9%87%8Ftop6.png" alt="浏览产品量top6" width="360" />
    <p>浏览产品量top6</p>
  </div>
</div>
&emsp;&emsp;其中，70.6%的用户没有到达预定页，而29.4%的用户访问过预定页，访问次数集中在1~2次。  
<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E5%88%B0%E8%BE%BE%E9%A2%84%E5%AE%9A%E9%A1%B5%E6%95%B0.png" alt="到达预定页数" width="600" />
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E5%88%B0%E8%BE%BE%E9%A2%84%E5%AE%9A%E9%A1%B5%E6%95%B0top6.png" alt="到达预定页数top6" width="380" />
    <p>到达预定页数top6</p>
  </div>
</div>

``` python
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
```
&emsp;&emsp;在访问过程中，40.3%的用户有过搜索历史，人均搜索次数为2次，其中11.6%的用户搜索过一次，占比最大，有10.4%的用户有过6次以上搜索；  
&emsp;&emsp;在搜索记录中，度假产品是搜索的热门品类，97.1%的用户只搜索过度假产品，搜索次数在7次以上的用户高达25.3%；  
&emsp;&emsp;其中，“青岛”、“北京”、“成都”、“三亚”、“西安”、“上海”、“新疆”、“杭州”是这部分命中人群的高频搜索词，即所偏好的出行目的地。  
<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E6%90%9C%E7%B4%A2%E9%A2%91%E7%8E%87.png" alt="搜索频率" width="600" />
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E6%90%9C%E7%B4%A2%E9%A2%91%E7%8E%87top6.png" alt="搜索频率top6" width="380" />
    <p>搜索频率top6</p>
  </div>
</div>
<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E5%BA%A6%E5%81%87%E4%BA%A7%E5%93%81%E6%90%9C%E7%B4%A2%E9%A2%91%E7%8E%87.png" alt="度假产品搜索频率" width="360" />
    <p>度假产品搜索频率</p>
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E5%8D%95%E8%B5%84%E6%BA%90%E4%BA%A7%E5%93%81%E6%90%9C%E7%B4%A2%E9%A2%91%E7%8E%87.png" alt="单资源产品搜索频率" width="400" />
    <p>单资源产品搜索频率</p>
  </div>
</div>
<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E7%83%AD%E9%97%A8%E6%90%9C%E7%B4%A2%E8%AF%8D.png" alt="热门搜索词" width="600" />
  <p>热门搜索词</p>
</div>

``` python
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
```
&emsp;&emsp;下图是用户在搜索页面的总停留时间的分布情况，可以看出总停留时间集中在[15, 143]秒之间，停留时间的中位数为49s，平均停留时间在64s左右。  
<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E6%90%9C%E7%B4%A2%E7%BB%93%E6%9E%9C%E9%A1%B5%E5%81%9C%E7%95%99%E6%97%B6%E9%97%B4.png" alt="搜索结果页停留时间" width="600" />
  <p>搜索结果页停留时间</p>
</div>
&emsp;&emsp;下图展示了在有搜索记录的人群中搜索结果的点击率情况，用户搜索点击率集中在[0, 0.1]，平均点击率在0.27左右。
<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E6%90%9C%E7%B4%A2%E7%82%B9%E5%87%BB%E7%8E%87.png" alt="搜索点击率" width="600" />
</div>

``` python
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
```
&emsp;&emsp;下图展示了用户浏览产品的相关信息。  
&emsp;&emsp;在浏览的产品中，单资源产品占比41.5%，占比较少，其中15%的产品为机票；  
&emsp;&emsp;用户浏览的度假产品高于单资源产品，占比58.5%，其中48.7%的产品为跟团游，这表明用户更偏向于度假产品中的跟团游，其次是自助游。  
<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E4%BA%A7%E5%93%81%E5%A4%A7%E7%B1%BB.png" alt="产品大类" width="330" />
    <p>产品大类</p>
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E4%BA%A7%E5%93%81%E4%B8%80%E7%BA%A7%E5%88%86%E7%B1%BB.png" alt="产品一级分类" width="400" />
    <p>产品一级分类</p>
  </div>
</div>
&emsp;&emsp;下图展示了用户浏览产品目的地类别的分布情况。排名前五的产品目的地为国内、华南、西南、华北、西北，其中云南、山东、海南、西北连线较为受用户欢迎。  
<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E4%BA%A7%E5%93%81%E4%B8%80%E7%BA%A7%E7%9B%AE%E7%9A%84%E5%9C%B0.png" alt="产品一级目的地" width="400" />
    <p>产品一级目的地</p>
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E4%BA%A7%E5%93%81%E4%BA%8C%E7%BA%A7%E7%9B%AE%E7%9A%84%E5%9C%B0.png" alt="产品二级目的地" width="400" />
    <p>产品二级目的地</p>
  </div>
</div>

``` python
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
```
&emsp;&emsp;用户浏览产品的平均行程天数主要在0\~12.5天，平均行程天数为2.5天。  
<div style="display: flex; justify-content: center; align-items: center;">
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E6%B5%8F%E8%A7%88%E4%BA%A7%E5%93%81%E7%9A%84%E5%B9%B3%E5%9D%87%E8%A1%8C%E7%A8%8B%E5%A4%A9%E6%95%B0-%E7%9B%B4%E6%96%B9%E5%9B%BE%E3%80%81.png" alt="浏览产品的平均行程天数" width="600" />
  </div>
  <div style="text-align: center;">
    <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E6%B5%8F%E8%A7%88%E4%BA%A7%E5%93%81%E7%9A%84%E5%B9%B3%E5%9D%87%E8%A1%8C%E7%A8%8B%E5%A4%A9%E6%95%B0-%E7%AE%B1%E7%BA%BF%E5%9B%BE.png" alt="浏览产品的平均行程天数" width="750" />
  </div>
</div>

``` python
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
```
&emsp;&emsp;通过对用户浏览产品的名称进行分析，6.95%的用户明显偏向于纯玩行程，无购物需求，而93%的用户有购物倾向。  
<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E7%83%AD%E9%97%A8%E6%B5%8F%E8%A7%88%E4%BA%A7%E5%93%81.png" alt="热门浏览产品" width="600" />
</div>
<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E8%B4%AD%E7%89%A9%E5%81%8F%E5%A5%BD.png" alt="购物偏好" width="400" />
  <p>购物偏好</p>
</div>

``` python
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
```
&emsp;&emsp;下面展示了用户浏览产品的平均最低价格、平均满意度、最大总评级别、平均点评数目、平均精华点评数目、平均返抵用券金额、平均返现金额、平均图片数目的分布情况。  
&emsp;&emsp;在浏览的产品中，产品的最低价格集中分布在[0, 2314]元之间，平均价格为1887元；  
&emsp;&emsp;产品的满意度评分集中在[90, 100]分，96\~98分的产品被浏览的频率最大，平均为94.55分；  
&emsp;&emsp;用户浏览产品的最大总评级别中，占比最多的是0级，占比55.6%；  
&emsp;&emsp;产品点评数目集中在[61, 8866]条，平均为73265条，精华点评数目集中在[0, 4]条，平均有2条；  
&emsp;&emsp;产品的返抵用券金额集中在[0, 40]元，平均为293元，返现金额集中在[0, 4.6]元，平均为36元；  
&emsp;&emsp;产品的图片数目集中在[68, 3325]个，平均有2976张。  
<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E4%BA%A7%E5%93%81%E5%B9%B3%E5%9D%87%E6%9C%80%E4%BD%8E%E4%BB%B7.png" alt="产品平均最低价" width="700" />
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E4%BA%A7%E5%93%81%E5%B9%B3%E5%9D%87%E6%BB%A1%E6%84%8F%E5%BA%A6.png" alt="产品平均满意度" width="600" />
</div>
<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E4%BA%A7%E5%93%81%E6%9C%80%E5%A4%A7%E6%80%BB%E8%AF%84%E7%BA%A7%E5%88%AB.png" alt="产品最大总评级别" width="300" />
  <p>产品最大总评级别</p>
</div>
<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E4%BA%A7%E5%93%81%E5%B9%B3%E5%9D%87%E7%82%B9%E8%AF%84%E6%95%B0%E7%9B%AE.png" alt="产品平均点评数目" width="700" />
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E4%BA%A7%E5%93%81%E5%B9%B3%E5%9D%87%E7%B2%BE%E5%8D%8E%E7%82%B9%E8%AF%84%E6%95%B0%E7%9B%AE.png" alt="产品平均精华点评数目" width="700" />
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E4%BA%A7%E5%93%81%E5%B9%B3%E5%9D%87%E8%BF%94%E6%8A%B5%E7%94%A8%E5%88%B8%E9%87%91%E9%A2%9D.png" alt="产品平均返抵用券金额" width="700" />
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E4%BA%A7%E5%93%81%E5%B9%B3%E5%9D%87%E8%BF%94%E7%8E%B0%E9%87%91%E9%A2%9D.png" alt="产品平均返现金额" width="700" />
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E4%BA%A7%E5%93%81%E5%B9%B3%E5%9D%87%E5%9B%BE%E7%89%87%E6%95%B0%E7%9B%AE.png" alt="产品平均图片数目" width="700" />
</div>

&emsp;&emsp;97%的用户在命中近7日内从未领取过优惠券，而仅有2.96%的用户领取过1张优惠券。  
<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E4%BC%98%E6%83%A0%E5%88%B8%E9%A2%86%E5%8F%96%E9%87%8F.png" alt="优惠券领取量" width="380" />
  <p>优惠券领取量</p>
</div>

&emsp;&emsp;路径分析（桑基图）： 
``` sql
-- 数据库取数：用户访问路径
create table tmp_access_path as
select distinct cust_id,call_date,visit_date,access_path 
from tmp_user_browsing_info 
where browsing_flag=1;
``` 
``` python
'''数据获取'''
import subprocess as sbs
sbs.run('source /etc/profile; hadoop fs -getmerge hdfs://emr-cluster/user/****/warehouse/tmp_access_path /opt/****/jupyter/c****/tmp_data/tmp_access_path.csv', shell=True)

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
```
&emsp;&emsp;上图展示了100条数据的路径分析图。  
<div align="center">
  <img src="https://raw.githubusercontent.com/5FiveFISH/Figure/main/img/%E8%A1%8C%E4%B8%BA%E8%BD%A8%E8%BF%B9%E5%9B%BE.png" alt="行为轨迹图" width="1200" />
  <p>行为轨迹图</p>
</div>
<br>


## <font color = 'blue' >四、结论与建议</font>
&emsp;&emsp;总结上述数据分析结果，有以下结论，
1. **命中时段：**  
   - 7月份命中率最高的在7月10日，8月份命中率最高的在8月14日，且8月份的命中率整体高于7月份；  
   - 工作日的命中情况大致呈下降趋势，周一最高，周二其次，慢慢减少，周四最低；  
   - 命中时间段在9点\~19点，和外呼时间保持一致，其中10:00\~11:00、14:00\~16:00处于命中高峰期，9:00、13:00、19:00左右的时间命中率较低。  
2. **命中人群特征：**  
   - 占比较大的命中群体的基本特征为女性、非单身、36\~45岁，命中人群主要分布在沿海区域，江苏省（6239）、上海（3923）、北京（3713）、广东省（2960）、浙江省（2679）等地区。  
   - 0级会员、会员类型为其他的占比最大，1级会员、老会员老客户占比次之；命中人群的注册时间在[2, 5822]，主要分布在132天\~2621天之间，中位数在1695天；87.8%的命中群体都为非企微用户，只有12.2%的人群为企微用户，其中这部分用户添加企微的时间普遍在2\~200天、900\~1000天之间，说明添加企微时间较短或较长的用户更容易被命中。  
   - 在命中群体中，有62.2%的用户可被短信触达，仅有7.61%的用户可被企业微信触达，这也与企微用户占比较少的结果保持一致。  
   - 家庭中有老人会增加用户的出游意愿，从而增加命中概率，但出游意愿也会随着老人人数的增加而降低；用户的出游意愿会随着家庭中老人和孩子的人数增加而降低，老人和孩子数越少，被命中的概率越大。  
   - 命中人群普遍对产品价格敏感度低，出行提前预定时间较短。  
   - 命中人群偏向于选择飞机作为交通工具，选择经济型或豪华型的酒店，游玩项目倾向于乐园、度假、出海/赶海、漂流，出行目的地偏向于周边游，其次是国内游，出行构成偏好家庭游、爸妈游和情侣游，出行时间段偏好在非寒暑假和工作日，出游天数集中分布在2~6天。  
   - 命中人群对促销活动的偏好程度低，大多数命中人群更喜欢有抵用券的促销活动，其次是有专项立减的促销活动；  
   - 命中人群的度假产品RFM评估值集中在4\~6.5分之间，3分居多。  
3. **命中前行为特征：**
   - 7-8月份，98.4%的用户被命中一次，而仅有1.64%的用户被命中两次。
   - 命中人群中，10.8%的用户无任何访问记录，89.2%的用户在命中前7天有APP/PC/M站的访问记录，且访问时间多集中在命中前1\~3天和命中当天。
   - 大部分命中人群近7日内活跃天数为1天，其次是2天，访问时间达4\~7天的用户数很少。
   - 命中人群近7日内的PV数集中在[6, 29]，中位数为13，平均在26次，日均PV集中在[5, 20]，中位数为10，平均在17次；命中人群近7日内的活跃时长集中在[46, 796]，中位数为209s，平均活跃时长为860s，日均活跃时长集中在[39, 571.5]，中位数为167s，平均为529s。
   - 65.7%的用户在命中近7日内浏览过产品，浏览产品量集中在1\~3个之间，平均浏览2.6个产品，其中仅有29.4%的用户到达预定页，访问次数集中在1\~2次。
   - 40.3%的用户有过搜索历史，人均搜索次数为2次，度假产品是搜索的热门品类，其中，“青岛”、“北京”、“成都”、“三亚”、“西安”、“上海”、“新疆”、“杭州”是这部分命中人群的高频搜索词，即所偏好的出行目的地；用户在搜索结果页的总停留时间集中在[15, 143]秒之间，平均停留时间在64s左右；搜索结果的点击率集中在[0, 0.1]，平均点击率在0.27左右。
   - 命中人群浏览的度假产品高于单资源产品，且更偏向于度假产品中的跟团游，其次是自助游；排名前五的产品目的地为国内、华南、西南、华北、西北，其中云南、山东、海南、西北连线较为受用户欢迎；浏览产品的行程时间集中在0\~5天，平均为2.5天；命中人群更偏向于包含双飞、购物、自由行的产品；对优惠券无明显偏好。
   - 在命中人群浏览的产品中，产品的最低价格集中分布在[0, 2314]元之间，平均价格为1887元；产品的满意度评分集中在[90, 100]分，96\~98分的产品被浏览的频率最大，平均为94.55分；产品点评数目集中在[61, 8866]条，平均为73265条，精华点评数目集中在[0, 4]条，平均有2条；产品的返抵用券金额集中在[0, 40]元，平均为293元，返现金额集中在[0, 4.6]元，平均为36元；产品的图片数目集中在[68, 3325]个，平均有2976张。
<br>

&emsp;&emsp;基于前述结论，以下是对运营维护的建议，期望能帮助运营团队更有针对性地推进活动和维护用户，提高用户参与度、留存率和转化率，从而提升业务绩效。
- **命中时段:**
  - 针对7月份和8月份的命中率差异，考虑季节性，提前进行促销活动和市场营销策略，提高7月份用户的命中率。
  - 在工作日的低命中时段，考虑进行特别优惠活动，以刺激用户在这些时段的互动。
  - 命中高峰期（10:00\~11:00和14:00\~16:00）是外呼的理想时间段，可以优先考虑在这些时间段进行机器人外呼。
- **命中人群特征:**
  - 针对主要分布在沿海区域的用户，可以根据其地理位置推出相关目的地的促销活动。
  - 针对非企业微信用户的大多数，可以增加企业微信的使用和宣传，以便扩大触达面。
  - 针对年龄、家庭情况等特征，可以定制不同的产品和服务，以满足不同人群的需求。
  - **对具有如下特征的人群进行重点维护：**
    - 36\~45岁，非单身，女性，居住在江苏、上海、北京、广东、浙江等沿海地区，家庭中有0\~1位老人或0\~1位孩子的用户群体；
    - 会员等级为0级和1级的老会员老客户，注册时间在132\~2621天，短信可触达的非企微人群；
    - 产品价格敏感度低，促销活动偏好程度低，交通偏好飞机，酒店偏好经济型或豪华型，喜欢乐园、度假、出海/赶海、漂流，出行偏好在非寒暑假和工作日，出游2\~6天，偏好家庭游、爸妈游、情侣游和周边游，有APP/PC/M站浏览记录的用户群体。
- **命中前行为特征:**
  - 针对访问频率较低，活跃天数仅为1或2天的用户，可以通过个性化内容推荐、提醒和奖励机制鼓励其更频繁的访问。
  - 对于搜索行为频繁的用户，提供更智能的搜索建议和过滤选项，提高搜索结果的质量，增加搜索点击率。
  - 对于活跃度高但浏览产品较少的用户，可以优化产品展示、页面推荐，引导其浏览更多产品。
- **促销策略:**
  - 针对对促销活动偏好程度较低的用户，可以提供更具吸引力的促销优惠，如抵用券、独家折扣、礼品或积分奖励。
  - 针对满意度较高的产品，可以将其推广给相关用户，以提高购买概率。

<br>

