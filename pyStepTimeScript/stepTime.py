# coding=UTF-8
# This Python file uses the following encoding: utf-8
import csv

# 解析原始数据
# ['T0_47', 'T1_108', 'T2_117', 'T3_26564', 'T4_26573', 'T5_28116', 'T6_28132', 'T7_28375', '","use_cache":false}']
import json


def parse_data(data):
    use_cache = False
    time = []
    for d in data[:8]:
        time.append(d[3:])
        if 'true' in data[8] or 'True' in data[8]:
            use_cache = True
    return use_cache, time


# 排序list使用
def compare_t7(elem):
    return int(elem[7])


def compare_fetch_config_cost(elem):
    return int(elem[3]) - int(elem[2])


def compare_fetch_composite_cost(elem):
    return int(elem[5]) - int(elem[4])


def compute_tp_value(list, key, tpxx):
    index = int(len(list) * tpxx)
    list.sort(key=key)
    
    print("tp_value index:%d - %s", (index, list[index]))
    return list[index]


def get_data(list, tpKey):
    if len(tpKey) < 4:
        print("Error >>> tpKey must lenght equal 4")
        return
    
    # 总耗时
    tp50_total = compare_t7(compute_tp_value(list, compare_t7, tpKey[0] / 100.00))
    tp70_total = compare_t7(compute_tp_value(list, compare_t7, tpKey[1] / 100.0))
    tp90_total = compare_t7(compute_tp_value(list, compare_t7, tpKey[2] / 100.00))
    tp99_total = compare_t7(compute_tp_value(list, compare_t7, tpKey[3] / 100.00))
    
    # infov2耗时
    tp50_fetch_config = compare_fetch_config_cost(
        compute_tp_value(list, compare_fetch_config_cost, tpKey[0] / 100.00))
    tp70_fetch_config = compare_fetch_config_cost(
        compute_tp_value(list, compare_fetch_config_cost, tpKey[1] / 100.00))
    tp90_fetch_config = compare_fetch_config_cost(
        compute_tp_value(list, compare_fetch_config_cost, tpKey[2] / 100.00))
    tp99_fetch_config = compare_fetch_config_cost(
        compute_tp_value(list, compare_fetch_config_cost, tpKey[3] / 100.00))
        
    # 合并接口耗时
    tp50_fetch_composite = compare_fetch_composite_cost(
        compute_tp_value(list, compare_fetch_composite_cost, tpKey[0] / 100.00))
    tp70_fetch_composite = compare_fetch_composite_cost(
        compute_tp_value(list, compare_fetch_composite_cost, tpKey[1] / 100.00))
    tp90_fetch_composite = compare_fetch_composite_cost(
        compute_tp_value(list, compare_fetch_composite_cost, tpKey[2] / 100.00))
    tp99_fetch_composite = compare_fetch_composite_cost(
        compute_tp_value(list, compare_fetch_composite_cost, tpKey[3] / 100.00))
    total_cost = [tp50_total, tp70_total, tp90_total, tp99_total]
    fetch_config_cost = [tp50_fetch_config, tp70_fetch_config, tp90_fetch_config, tp99_fetch_config]
    fetch_composite_cost = [tp50_fetch_composite, tp70_fetch_composite, tp90_fetch_composite, tp99_fetch_composite]
    return total_cost, fetch_config_cost, fetch_composite_cost


def print_result_item(list, title, key):
    for index, item in enumerate(list):
        title += '\t\t%d (TP%d)' % (item, key[index])
    print(title)


# show result
def print_result(datas):
    if len(datas) <= 0:
        print('暂无可用数据。')
        return
    
    #必须指定4分位线
    tpKey = [50, 75, 90, 95]

    total_cost, fetch_config_cost, fetch_composite_cost = get_data(datas, tpKey)
    print_result_item(total_cost, '二维码展示总耗时：', tpKey)
    print_result_item(fetch_config_cost, '拉取infov2耗时：', tpKey)
    print_result_item(fetch_composite_cost, '拉取合并接口耗时：', tpKey)


def print_beauty(time_not_use_cache, time_use_cache):
    print("未命中缓存的耗时数据(%d条)：\n---------------" % len(time_not_use_cache))
    print_result(time_not_use_cache)
    print()
    print("命中缓存的耗时数据(%d条)：\n---------------" % len(time_use_cache))
    print_result(time_use_cache)


android = './android.csv'
iOS = './ios.csv'


def compute_android(path=android):
    csv_file = open(path, "r")
    reader = csv.reader(csv_file)

    word = '{custom={"time_step":"'

    time_use_cache = []
    time_not_use_cache = []
    
    debugCount = 0
    t65Timeout = 0
    t54Timeout = 0

    for line in reader:
        if len(line) <= 0:
            continue
        if line[0] == 'partition_date':
            continue
        # 过滤掉无关数据
        origin_str = str(line[2])
        if word in origin_str:
            pre_data = origin_str[22:-1];

            # 过滤掉测试数据
            debugSource = True
            if '"buildType":"release"' in pre_data:
                debugSource = False
            if debugSource:
                debugCount = debugCount + 1
                continue;

            temp = pre_data.split('|')
            if len(temp) == 9:
                use_cache, time = parse_data(temp)
                
                # 过滤掉T5与T6超长的异常数据
                t65 = int(time[6])-int(time[5])
                if  t65 > 500:
                    #                    print('\n 6-5 timeout:', pre_data)
                    t65Timeout = t65Timeout + 1
                    continue
                
                # 拉码接口超过60秒
                t54 = int(time[5])-int(time[4])
                if  t54 > 6000:
                    #                    print('\n 6-5 timeout:', pre_data)
                    t54Timeout = t54Timeout + 1
                    continue
                
                if use_cache:
                    time_use_cache.append(time)
                else:
                    time_not_use_cache.append(time)

    print("\nandroid debug数据个数%d条, 异常数据%d条, 超时数据%d条 \n" % (debugCount, t65Timeout, t54Timeout))
    print_beauty(time_not_use_cache, time_use_cache)


def compute_iOS(path=iOS):
    csv_file = open(path, "r")
    reader = csv.reader(csv_file)

    word = '{custom='

    time_use_cache = []
    time_not_use_cache = []
    
    debugCount = 0
    t10Timeout = 0
    t65Timeout = 0

    for line in reader:
        if len(line) <= 0:
            continue
        if line[0] == 'partition_date':
            continue
        # 过滤掉无关数据
        origin_str = str(line[2])
        if word in origin_str:
            origin_str = origin_str.replace('{custom=', '')[:-1]
            json_data = json.loads(origin_str)
            
            pre_data = 'T0_0|%s|%s' % (json_data['time_step'], json_data['use_cache'])
            if 'T0' in json_data['time_step']:
                pre_data = '%s|%s' % (json_data['time_step'], json_data['use_cache'])
                    
            # 过滤掉测试数据
            buildType = 'nono'
            if json_data.get('buildType'):
                buildType = json_data['buildType']
            if buildType != 'release':
#                print('\n no build source:', pre_data)
                debugCount = debugCount + 1
                continue
            
            temp = pre_data.split('|')
            if len(temp) == 9:
                use_cache, time = parse_data(temp)
                
                # 过滤掉T0与T1超长的异常数据
                t65 = int(time[1])-int(time[0])
                if  t65 > 1000:
                    #                    print('\n 6-5 timeout:', pre_data)
                    t10Timeout = t10Timeout + 1
                    continue
                
                # 过滤掉T5与T6超长的异常数据
                t65 = int(time[6])-int(time[5])
                if  t65 > 500:
#                    print('\n 6-5 timeout:', pre_data)
                    t65Timeout = t65Timeout + 1
                    continue
                
                if use_cache:
                    time_use_cache.append(time)
                else:
                    time_not_use_cache.append(time)

    print("\nios debug数据个数%d条, 异常数据%d条, loading异常数据%d条\n" % (debugCount, t65Timeout, t10Timeout))
    print_beauty(time_not_use_cache, time_use_cache)


compute_android()
print('\n← Android\n\n\niOS →\n')
compute_iOS()
