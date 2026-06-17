'''
============================================================
 多线程 threading
============================================================
对照笔记: 06 并发编程-threading/进程与线程.md
  — 并发 vs 并行
  — threading.Thread 创建线程
  — threading.Lock 线程安全
  — GIL 全局解释器锁
  — multiprocessing 多进程
============================================================
'''

import threading
import time

# ═══════════════════════════════════════════════════════════════
# 1. 并发 vs 并行 概念
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【并发 vs 并行】")
print("=" * 50)

print("  并发 (Concurrency): 单个 CPU 交替执行多个任务")
print("  并行 (Parallelism): 多个 CPU 同时执行多个任务")
print("  CPython GIL: 多线程无法真正并行计算，适合 I/O 密集型")
print()

# ═══════════════════════════════════════════════════════════════
# 2. threading.Thread — 创建并启动线程
# ═══════════════════════════════════════════════════════════════
print("=" * 50)
print("【threading.Thread — 基本线程】")
print("=" * 50)


def worker(name, delay, count=3):
    """线程工作函数"""
    for i in range(count):
        time.sleep(delay)
        print(f"  [{name}] 第 {i+1} 次执行 (睡眠 {delay}s)")

# 创建线程
t1 = threading.Thread(target=worker, args=('线程A', 0.5))
t2 = threading.Thread(target=worker, args=('线程B', 0.3))
t3 = threading.Thread(target=worker, kwargs={'name': '线程C', 'delay': 0.4, 'count': 2})

print("  启动 3 个线程...")
start = time.time()
t1.start()
t2.start()
t3.start()

# join 等待线程结束
t1.join()
t2.join()
t3.join()
elapsed = time.time() - start
print(f"  3 个线程全部完成 (耗时 {elapsed:.1f}s)")
print("  注意: 总时间 ≈ 最长线程时间，而非三者之和 (并发执行)")

# ═══════════════════════════════════════════════════════════════
# 3. threading.Lock — 线程安全
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【threading.Lock — 线程安全】")
print("=" * 50)

counter_with_lock = 0
counter_without_lock = 0
lock = threading.Lock()


def increment_safe(n):
    """带锁的递增 — 安全"""
    global counter_with_lock
    for _ in range(n):
        with lock:              # 等价于 lock.acquire() / lock.release()
            counter_with_lock += 1


def increment_unsafe(n):
    """无锁递增 — 不安全"""
    global counter_without_lock
    for _ in range(n):
        counter_without_lock += 1

# 带锁版本
threads = [threading.Thread(target=increment_safe, args=(100000,)) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"  带 Lock 计数器 (期望 400000): {counter_with_lock}")

# 无锁版本 (可能有竞态)
threads = [threading.Thread(target=increment_unsafe, args=(100000,)) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"  无 Lock 计数器 (期望 400000): {counter_without_lock}")
print(f"  (无锁时多个线程可能同时读写，导致竞态条件)")

# ═══════════════════════════════════════════════════════════════
# 4. GIL — 全局解释器锁
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【GIL 全局解释器锁】")
print("=" * 50)

print("  CPython 中 GIL 限制:")
print("    • 同一时刻只有一个线程执行 Python 字节码")
print("    • I/O 密集型: 多线程有效 (I/O 时释放 GIL)")
print("    • CPU 密集型: 多线程反而更慢 (线程切换开销)")
print()
print("  解决方案:")
print("    • CPU 密集型 → multiprocessing 多进程")
print("    • I/O 密集型 → threading 多线程 / asyncio 异步")

# ═══════════════════════════════════════════════════════════════
# 5. multiprocessing — 多进程
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【multiprocessing 多进程】")
print("=" * 50)

try:
    import multiprocessing

    def cpu_task(n):
        """CPU 密集型任务"""
        total = 0
        for i in range(n):
            total += i * i
        return total

    print("  CPU 密集型: 用 multiprocessing 实现真正并行")
    print("    from multiprocessing import Process")
    print("    p = Process(target=func, args=(...))")
    print("    p.start()")
    print("    p.join()")
    print()
    print("  进程数建议: os.cpu_count() 或 cpu_count() - 1")

except ImportError:
    pass

# ═══════════════════════════════════════════════════════════════
# 6. 对比总结
# ═══════════════════════════════════════════════════════════════
print()
print("=" * 50)
print("【多线程 vs 多进程 vs 异步】")
print("=" * 50)

print("  threading       : 轻量, 共享内存, GIL限制, 适合 I/O 密集型")
print("  multiprocessing : 重量, 独立内存, 真并行, 适合 CPU 密集型")
print("  asyncio         : 单线程协程, 最高效 I/O, 需要 async/await")
print()
print("  shutdown 示例:")
print("    t = threading.Thread(target=cleanup)")
print("    t.daemon = True  # 主线程退出时自动终止")
