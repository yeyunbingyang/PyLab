# 1.块注释
# 我是块注释
print(111)

# 2.行内注释
print('我在学习python')  # 与代码同⾏,【#前⾯⾄少有两个空格】

# 3.多行注释
"""
我是多行注释
我是多行注释"""

'''
我是多行注释
我是多行注释'''
print(333)

# DocStrings（⽂档字符串）
def add(num1,num2):
    """ 完成传⼊的两个数之和

    :param num1: 加数1
    :param num2: 加数2
    :return: 和
   """

print(add)
print( add.__doc__ )

