import pymysql

# 1. 创建连接
conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    password='1234',
    database='pymysql',
    charset='utf8mb4'
)
print(f"连接成功: {conn}")

# ═══════════════════════════════════════
# 查
# ═══════════════════════════════════════
print("\n【查询所有】")
try:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM emp")
        rows = cursor.fetchall()
        print(f"  共 {cursor.rowcount} 条记录")
        for row in rows:
            print(f"  {row}")
except Exception as e:
    print(f"  查询失败: {e}")

print("\n【查询 id=1】")
try:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM emp WHERE id=%s", (1,))
        row = cursor.fetchone()
        print(f"  结果: {row}")
except Exception as e:
    print(f"  查询失败: {e}")

# ═══════════════════════════════════════
# 增
# ═══════════════════════════════════════
print("\n【插入】")
try:
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO emp(name, age) VALUES(%s, %s)", ('Tom', 20))
        conn.commit()
        print(f"  插入成功，新记录 ID: {cursor.lastrowid}")
        print(f"  影响行数: {cursor.rowcount}")
except Exception as e:
    conn.rollback()
    print(f"  插入失败: {e}")

# 插入后立即查看
print("\n【插入后查询】")
with conn.cursor() as cursor:
    cursor.execute("SELECT * FROM emp WHERE name=%s", ('Tom',))
    print(f"  找到: {cursor.fetchone()}")

# ═══════════════════════════════════════
# 改
# ═══════════════════════════════════════
print("\n【更新】")
try:
    with conn.cursor() as cursor:
        cursor.execute("UPDATE emp SET age=%s WHERE name=%s", (21, "Tom"))
        conn.commit()
        print(f"  影响行数: {cursor.rowcount}")
        if cursor.rowcount == 0:
            print("  ⚠️ 没有记录被更新")
except Exception as e:
    conn.rollback()
    print(f"  更新失败: {e}")

# 更新后查看
print("\n【更新后查询】")
with conn.cursor() as cursor:
    cursor.execute("SELECT * FROM emp WHERE name=%s", ('Tom',))
    print(f"  Tom 现在的数据: {cursor.fetchone()}")

# ═══════════════════════════════════════
# 删
# ═══════════════════════════════════════
print("\n【删除】")
try:
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM emp WHERE name=%s", ("Tom",))
        conn.commit()
        print(f"  影响行数: {cursor.rowcount}")
        if cursor.rowcount == 0:
            print("  ⚠️ 没有记录被删除")
except Exception as e:
    conn.rollback()
    print(f"  删除失败: {e}")

# 删除后查看
print("\n【删除后查询】")
with conn.cursor() as cursor:
    cursor.execute("SELECT * FROM emp WHERE name=%s", ('Tom',))
    result = cursor.fetchone()
    print(f"  Tom 还存在吗: {'是' if result else '否'}")

# 关闭连接
conn.close()
print("\n连接已关闭")