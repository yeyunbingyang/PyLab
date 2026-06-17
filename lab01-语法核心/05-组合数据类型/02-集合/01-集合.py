# demo_set.py

# 创建集合
set1 = {1, 2, 3, 3, 3, 2}
print(set1)  # {1, 2, 3}

set2 = {'banana', 'pitaya', 'apple', 'apple', 'banana', 'grape'}
print(set2)  # {'banana', 'pitaya', 'apple', 'grape'}

set3 = set('hello')
print(set3)  # {'h', 'e', 'l', 'o'}

set4 = set([1, 2, 2, 3, 3, 3, 2, 1])
print(set4)  # {1, 2, 3}

set5 = {num for num in range(1, 20) if num % 3 == 0 or num % 7 == 0}
print(set5)  # {3, 6, 7, 9, 12, 14, 15, 18}

# 遍历集合
set_languages = {'Python', 'C++', 'Java', 'Kotlin', 'Swift'}
for elem in set_languages:
    print(elem)

# 成员运算
set1 = {11, 12, 13, 14, 15}
print(10 in set1)      # False
print(15 in set1)      # True

set2 = {'Python', 'Java', 'C++', 'Swift'}
print('Ruby' in set2)  # False
print('Java' in set2)  # True

# 二元运算
set1 = {1, 2, 3, 4, 5, 6, 7}
set2 = {2, 4, 6, 8, 10}

print(set1 & set2)                      # 交集 {2, 4, 6}
print(set1.intersection(set2))          # {2, 4, 6}

print(set1 | set2)                      # 并集 {1, 2, 3, 4, 5, 6, 7, 8, 10}
print(set1.union(set2))                 # {1, 2, 3, 4, 5, 6, 7, 8, 10}

print(set1 - set2)                      # 差集 {1, 3, 5, 7}
print(set1.difference(set2))            # {1, 3, 5, 7}

print(set1 ^ set2)                      # 对称差 {1, 3, 5, 7, 8, 10}
print(set1.symmetric_difference(set2))  # {1, 3, 5, 7, 8, 10}

# 复合赋值运算
set1 = {1, 3, 5, 7}
set2 = {2, 4, 6}
set1 |= set2
print(set1)  # {1, 2, 3, 4, 5, 6, 7}

set3 = {3, 6, 9}
set1 &= set3
print(set1)  # {3, 6}

set2 -= set1
print(set2)  # {2, 4}

# 比较运算
set1 = {1, 3, 5}
set2 = {1, 2, 3, 4, 5}
set3 = {5, 4, 3, 2, 1}

print(set1 < set2)   # True
print(set1 <= set2)  # True
print(set2 < set3)   # False
print(set2 <= set3)  # True
print(set2 > set1)   # True
print(set2 == set3)  # True

print(set1.issubset(set2))    # True
print(set2.issuperset(set1))  # True

# 添加和删除元素
set1 = {1, 10, 100}
set1.add(1000)
set1.add(10000)
print(set1)  # {1, 10, 100, 1000, 10000}

set1.discard(10)
if 100 in set1:
    set1.remove(100)
print(set1)  # {1, 1000, 10000}

set1.clear()
print(set1)  # set()

# isdisjoint 判断是否有交集
set1 = {'Java', 'Python', 'C++', 'Kotlin'}
set2 = {'Kotlin', 'Swift', 'Java', 'Dart'}
set3 = {'HTML', 'CSS', 'JavaScript'}
print(set1.isdisjoint(set2))  # False
print(set1.isdisjoint(set3))  # True

# 不可变集合 frozenset
fset1 = frozenset({1, 3, 5, 7})
fset2 = frozenset(range(1, 6))
print(fset1 & fset2)  # frozenset({1, 3, 5})
print(fset1 | fset2)  # frozenset({1, 2, 3, 4, 5, 7})
print(fset1 - fset2)  # frozenset({7})
print(fset1 < fset2)  # False
