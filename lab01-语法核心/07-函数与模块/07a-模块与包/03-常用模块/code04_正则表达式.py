import re

'''
# 元字符：
\d  数字 0-9
\w  单词字符 (字母数字下划线)
\s  空白字符
.   任意字符 (不含换行，除非 DOTALL)

^   字符串/行开始
$   字符串/行结尾
\b  单词边界

[]  字符类 例如 [A-Za-z0-9]
[^] 否定字符类

*   0或多次
+   1或多次
?   0或1次
{m,n} m到n次

()  捕获分组
(?:) 非捕获分组
(?P<name>) 命名分组
\1  \2 反向引用

(?=...) 正向先行断言（之后必须是...）
(?!...) 负向先行断言（之后不能是...）
(?<=...) 正向后行断言（之前是...）  # 固定宽度限制
(?<!...) 负向后行断言

flags: re.I, re.M, re.S, re.X
常用函数: match, search, fullmatch, findall, finditer, sub, split

'''

# \d :数字
# 检测字符串是否为纯数字的字符串
result = re.match(r'\d+','1234234234')
print(result)
# \w:数字字母下划线
result = re.match(r'\w+','a*8')
print(result)
# \s:空白字符  \S 非空
result= re.match(r'^\s+$','    ')
print(result)
# . 任意字符
result = re.match(r'^code\d-\d-.+$','code5-2-random')
print(result)
# []区间，可选列表
result = re.match(r'^abc{2,5}$','abcccccc')
print(result)
# | 或者
result = re.match(r'^a|b|c$','d')
print(result)

# 身份证号
result = re.match(r'^\d{6}((20[012][01234])|(1[89]\d\d))\d{7}([\dX])$','12345619951234567X')
print(result)

result = re.match(r'^20[012][01234]$','2008')
print(result)

result = re.match(r'^1[89]\d\d$','1998')
print(result)

# 手机号码
result =re.match(r'^1\d{10}$','12345678391')
print(result)

from  my_package import  my_tools
print(my_tools.is_phone_number('12312312333'))
print(my_tools.is_id_number('4323451996445453456'))