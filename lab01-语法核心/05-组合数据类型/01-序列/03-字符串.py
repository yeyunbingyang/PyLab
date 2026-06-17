"""
Python 字符串（String）学习示例
"""

# =========================================================
# 一、字符串的定义
# =========================================================

# 使用单引号定义字符串
s1 = 'hello, world!'
print("s1:", s1)

# 使用双引号定义字符串
s2 = "你好，世界！❤️"
print("s2:", s2)

# 使用三引号定义多行字符串
s3 = '''hello,
wonderful
world!'''
print("s3:", s3)

# str()
print("str(s1):", str(s1))



# =========================================================
# 二、转义字符
# =========================================================

# 使用反斜杠转义
s1 = '\'hello, world!\''
s2 = '\\hello, world!\\'
print("\n转义字符:")
print(s1)  # 'hello, world!'
print(s2)  # \hello, world!\

# =========================================================
# 三、原始字符串
# =========================================================

# r 或 R 前缀的原始字符串
s1 = 'it \is \time \to \read \now'
s2 = r'\it \is \time \to \read \now'
print("\n原始字符串:")
print(s1)  # \it \is \time \to \read \now  (会转义)
print(s2)  # \it \is \time \to \read \now  (不转义)

# =========================================================
# 四、字符的特殊表示
# =========================================================

# 八进制、十六进制和 Unicode 编码表示字符
s1 = '\141\142\143\x61\x62\x63'  # 八进制和十六进制表示
s2 = '\u9a86\u660a'  # Unicode编码
print("\n特殊字符表示:")
print(s1)  # abcabc
print(s2)  # 骆昊

# =========================================================
# 五、字符串的运算
# =========================================================

# 拼接和重复字符串
s1 = 'hello' + ', ' + 'world'
print("\n拼接字符串:")
print(s1)  # hello, world

s2 = '!' * 3
print("\n重复字符串:")
print(s2)  # !!!

s1 += s2
print(s1)  # hello, world!!!

s1 *= 2
print(s1)  # hello, world!!!hello, world!!!

# =========================================================
# 六、字符串的比较
# =========================================================

# 字符串比较运算
s1 = 'a whole new world'
s2 = 'hello world'

print("\n字符串比较:")
print(s1 == s2)             # False
print(s1 < s2)              # True
print(s1 == 'hello world')  # False
print(s2 == 'hello world')  # True

# 使用 ord() 获取字符的 Unicode 编码
print(ord('A'))  # 65
print(ord('a'))  # 97
print(ord('骆'))  # 39558
print(ord('昊'))  # 26122

# =========================================================
# 七、成员运算
# =========================================================

# 检查子字符串是否存在于字符串中
s1 = 'hello, world'
s2 = 'goodbye, world'

print("\n成员运算:")
print('wo' in s1)      # True
print('wo' not in s2)  # False
print(s2 in s1)        # False

# =========================================================
# 八、获取字符串长度
# =========================================================

# 使用 len() 获取字符串的长度
s = 'hello, world'
print("\n字符串长度:")
print(len(s))                 # 12
print(len('goodbye, world'))  # 14

# =========================================================
# 九、索引和切片
# =========================================================

# 字符串索引和切片
s = 'abc123456'
n = len(s)
print("\n索引和切片:")
print(s[0], s[-n])    # a a
print(s[n-1], s[-1])  # 6 6
print(s[2], s[-7])    # c c
print(s[5], s[-4])    # 3 3
print(s[2:5])         # c12
print(s[-7:-4])       # c12
print(s[2:])          # c123456
print(s[:2])          # ab
print(s[::2])         # ac246
print(s[::-1])        # 654321cba

# =========================================================
# 十、字符串的方法
# =========================================================

# 字符串大小写转换
s1 = 'hello, world!'
print("\n字符串大小写转换:")
print(s1.capitalize())  # Hello, world!
print(s1.title())       # Hello, World!
print(s1.upper())       # HELLO, WORLD!

# 字符串查找
print("\n字符串查找:")
print(s1.find('or'))      # 8
print(s1.find('or', 9))   # -1
print(s1.index('or'))     # 8
# print(s1.index('or', 9))  # ValueError: substring not found

# 字符串匹配
print("\n字符串匹配:")
print(s1.startswith('He'))   # False
print(s1.startswith('hel'))  # True
print(s1.endswith('!'))      # True

# 数字和字母判断
s2 = 'abc123456'
print(s2.isdigit())  # False 判断是否为数字
print(s2.isalpha())  # False 判断是否为字母
print(s2.isalnum())  # True 判断是否为数字或字母

# =========================================================
# 十一、字符串的格式化
# =========================================================

# 使用占位符进行字符串格式化
a = 321
b = 123
print("\n字符串格式化:")
print('%d * %d = %d' % (a, b, a * b))

# 使用format方法格式化字符串
print('{0} * {1} = {2}'.format(a, b, a * b))

# 使用f-string格式化
print(f'{a} * {b} = {a * b}')

# 精确控制格式化
pi = 3.1415926
print(f'Pi to 2 decimal places: {pi:.2f}')  # 3.14
print(f'Pi in scientific notation: {pi:.2e}')  # 3.14e+00

# =========================================================
# 十二、字符串的修剪与替换
# =========================================================

# 修剪字符串的空格
s1 = '   jackfrued@126.com  '
print("\n修剪操作:")
print(s1.strip())      # jackfrued@126.com
print(s1.lstrip())     # jackfrued@126.com
print(s1.rstrip())     #   jackfrued@126.com

# 替换字符串中的内容
s = 'hello, good world'
print(s.replace('o', '@'))     # hell@, g@@d w@rld
print(s.replace('o', '@', 1))  # hell@, good world

# =========================================================
# 十三、拆分与合并字符串
# =========================================================

# 拆分字符串
s = 'I love you'
words = s.split()
print("\n拆分字符串:")
print(words)            # ['I', 'love', 'you']
print('~'.join(words))  # I~love~you


# 拆分自定义分隔符
s = 'I#love#you#so#much'
words = s.split('#')
print(words)  # ['I', 'love', 'you', 'so', 'much']
words = s.split('#', 2)
print(words)  # ['I', 'love', 'you#so#much']

# =========================================================
# 十四、编码与解码字符串
# =========================================================

# 编码和解码操作
a = '骆昊'
b = a.encode('utf-8')
c = a.encode('gbk')
print("\n编码与解码:")
print(b)                  # b'\xe9\xaa\x86\xe6\x98\x8a'
print(c)                  # b'\xc2\xe6\xea\xbb'
print(b.decode('utf-8'))  # 骆昊
print(c.decode('gbk'))    # 骆昊

