# demo_dict.py

# 创建字典
xinhua = {
    '麓': '山脚下',
    '路': '道，往来通行的地方；方面，地区：南～货，外～货；种类：他俩是一～人',
    '蕗': '甘草的别名',
    '潞': '潞水，水名，即今山西省的浊漳河；潞江，水名，即云南省的怒江'
}
print(xinhua)

# 保存一个人的信息
person = {
    'name': '王大锤',
    'age': 55,
    'height': 168,
    'weight': 60,
    'addr': '成都市武侯区科华北路62号1栋101',
    'tel': '13122334455',
    'emergence contact': '13800998877'
}
print(person)

# 使用 dict 函数创建字典
person2 = dict(name='王大锤', age=55, height=168, weight=60, addr='成都市武侯区科华北路62号1栋101')
print(person2)

# 使用 zip 创建字典
items1 = dict(zip('ABCDE', '12345'))
print(items1)  # {'A': '1', 'B': '2', 'C': '3', 'D': '4', 'E': '5'}

items2 = dict(zip('ABCDE', range(1, 10)))
print(items2)  # {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}

# 字典生成式
items3 = {x: x ** 3 for x in range(1, 6)}
print(items3)  # {1: 1, 2: 8, 3: 27, 4: 64, 5: 125}

# 获取字典长度
person = {
    'name': '王大锤',
    'age': 55,
    'height': 168,
    'weight': 60,
    'addr': '成都市武侯区科华北路62号1栋101'
}
print(len(person))  # 5

# 遍历字典（默认遍历键）
for key in person:
    print(key)

# 成员运算
print('name' in person)  # True
print('tel' in person)   # False

# 索引访问值
print(person['name'])
print(person['addr'])

# 更新字典
person['age'] = 25
person['height'] = 178
person['tel'] = '13122334455'
person['signature'] = '你的男朋友是一个盖世垃圾，他会踏着五彩祥云去迎娶你的闺蜜'
for key, value in person.items():
    print(f'{key}: {value}')

# get 方法
print(person.get('name'))       # 王大锤
print(person.get('sex'))        # None
print(person.get('sex', True))  # True

# keys, values, items
print(person.keys())    # dict_keys([...])
print(person.values())  # dict_values([...])
print(person.items())   # dict_items([...])

# update 合并字典
person1 = {'name': '王大锤', 'age': 55, 'height': 178}
person2 = {'age': 25, 'addr': '成都市武侯区科华北路62号1栋101'}
person1.update(person2)
print(person1)

# Python 3.9+ 可以用 |=
person1 |= person2
print(person1)

# 删除元素
person = {'name': '王大锤', 'age': 25, 'height': 178, 'addr': '成都市武侯区科华北路62号1栋101'}
print(person.pop('age'))  # 25
print(person)
print(person.popitem())   # 删除最后一对
print(person)
person.clear()            # 清空字典
print(person)

# del 删除
person = {'name': '王大锤', 'age': 25, 'height': 178, 'addr': '成都市武侯区科华北路62号1栋101'}
del person['age']
del person['addr']
print(person)

# 应用示例1：统计字母出现次数
sentence = "Man is distinguished, not only by his reason, but by this singular passion..."
counter = {}
for ch in sentence:
    if 'A' <= ch <= 'Z' or 'a' <= ch <= 'z':
        counter[ch] = counter.get(ch, 0) + 1
sorted_keys = sorted(counter, key=counter.get, reverse=True)
for key in sorted_keys:
    print(f'{key} 出现了 {counter[key]} 次.')

# 应用示例2：筛选股价大于100元的股票
stocks = {
    'AAPL': 191.88,
    'GOOG': 1186.96,
    'IBM': 149.24,
    'ORCL': 48.44,
    'ACN': 166.89,
    'FB': 208.09,
    'SYMC': 21.29
}
stocks2 = {key: value for key, value in stocks.items() if value > 100}
print(stocks2)
