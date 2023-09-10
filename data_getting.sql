--  sql1 = '选取机器人外呼命中用户'
drop table if exists tmp_call_label_cust;
create table tmp_call_label_cust as
select cust_id, answer_time, to_date(answer_time) call_date from dw.kn1_fe_cust_poi_predict_call_result_detail_v2
where dt >= '20230701' and type in (1, 4) and answer_flag=1 and label=1     -- 模型1、4命中人群
    and cust_id in (select distinct cust_id from dw.kn1_usr_cust_attribute);    -- 剔除已注销用户


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- sql2 = '用户属性维度'
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


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- sql3 = '用户浏览行为明细'
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


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- sql4 = '用户行为维度'
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


---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- sql5 = '获取用户访问路径'
create table tmp_access_path as
select distinct cust_id,call_date,visit_date,access_path 
from tmp_user_browsing_info 
where browsing_flag=1;

