import pandas as pd
import json
import re

# # 读取JSON文件
# with open('assets/papers.json', 'r', encoding='utf-8') as file:
#     data = json.load(file)
#
# # 遍历papers数组中的每个条目
# for paper in data['papers']:
#     # 如果存在others字段
#     if 'others' in paper:
#         # 如果others字段中有底层算法，删除它
#         if '底层算法' in paper['others']:
#             del paper['others']['底层算法']
#         if 'others' in paper['others']:
#             del paper['others']['others']
#         # 如果others字段为空，则删除others字段本身
#         if not paper['others']:
#             del paper['others']
#
# # 将修改后的数据写入新的JSON文件
# with open('modified_paper.json', 'w', encoding='utf-8') as file:
#     json.dump(data, file, ensure_ascii=False, indent=4)
#
# print("JSON文件已修改并保存为modified_paper.json")

## 读取xlsx 转 json
# 读取Excel文件
file_path = r'D:\研究生\科研\时序数据\时序数据可视化综述\导出CSV条目整理\网站表格-可视化任务-可视化类型-2024年11月26日.xlsx'
df = pd.read_excel(file_path)

# 重命名列
df.rename(columns={'题目': 'name', '时间': 'year', '作者': 'authors'}, inplace=True)

# 定义需要合并的任务类型字段
fields_to_merge_task = [
    "模式识别",
    "异常发现",
    "预测分析",
    "趋势分析",
    "分类比较",
    "观察探索",
    "其他"
]

# 定义需要合并的图像类型字段
fields_to_merge_image = [
    "点图",
    "线形图",
    "条形图",
    "弧形图",
    "区域",
    "地图",
    "网格",
    "树与层次图",
    "网络图",
    "大于2维"
]

# 去除字符串值中的多余空格
def strip_spaces(row):
    for key, value in row.items():
        if isinstance(value, str):
            row[key] = re.sub(r'^\s+|\s+$', '', value)  # 移除首尾空白字符
            row[key] = re.sub(r'\s+', ' ', row[key])    # 移除内部连续空白字符
        elif isinstance(value, list):
            row[key] = [re.sub(r'^\s+|\s+$', '', v) for v in value if isinstance(v, str)]
            row[key] = [re.sub(r'\s+', ' ', v) for v in row[key]]
    return row

# 进行任务类型字段的转换
def merge_fields(row, fields):
    return [row[field].strip() for field in fields if pd.notna(row[field]) and row[field].strip()]

# 应用转换函数
df['任务类型'] = df.apply(lambda row: merge_fields(row, fields_to_merge_task), axis=1)
df['图像类型'] = df.apply(lambda row: merge_fields(row, fields_to_merge_image), axis=1)

# 删除旧的字段
df.drop(columns=fields_to_merge_task + fields_to_merge_image, inplace=True)

# 合并 authors, 任务驱动, 创新点 到 others 字段
def merge_others(row):
    others = {
        "authors": row.get('authors', '').strip(),
        "创新点": row.get('创新点', '').strip()
    }
    return others

# 应用合并 others 的函数
df['others'] = df.apply(merge_others, axis=1)

# 删除旧的字段
df.drop(columns=['authors', '任务驱动', '创新点', '应用领域', '数据来源'], inplace=True)

# 将创新阶段字段转换为列表
def convert_to_list(value):
    if isinstance(value, str):
        return [item.strip() for item in value.split('、') if item.strip()]
    return value

# 应用转换函数到创新阶段字段
df['创新阶段'] = df['创新阶段'].apply(convert_to_list)

# 将 Tag 字段转换为列表
def convert_to_tag(tag):
    if isinstance(tag, str):
        return [tag.strip()]
    return tag

# 应用转换函数到 Tag 字段
df['Tag'] = df['Tag'].apply(convert_to_tag)

# 创建 venue 列
def create_venue(ccf_value):
    if ccf_value:
        return f"CCF {ccf_value.strip()}"
    return None

# 应用创建 venue 的函数
df['venue'] = df['CCF'].apply(create_venue)
df['CCF'] = df['CCF'].apply(convert_to_list)

# 去除所有字符串值中的多余空格
df = df.apply(strip_spaces, axis=1)

# 指定新的列顺序
new_order = ["name", "venue", "year", "others", "CCF", "Tag", "任务类型", "图像类型", "创新阶段"]

# 使用 reindex 方法调整列的顺序
df = df.reindex(columns=new_order)

# 将DataFrame转换为JSON格式，并设置缩进
json_data = df.to_json(orient='records', force_ascii=False, indent=4)

# 将JSON数据写入文件
with open('78_new_papers.json', 'w', encoding='utf-8') as file:
    file.write(json_data)

print("JSON文件已保存为78_new_papers.json")


