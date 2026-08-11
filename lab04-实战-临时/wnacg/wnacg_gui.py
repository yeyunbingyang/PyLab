"""
wnacg 漫画下载器 GUI 版
打包命令：
    pip install pyinstaller
    pyinstaller --onefile --windowed --icon=icon.ico --name=wnacg_Downloader wnacg_gui.py
"""
import os
import sys
import io
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# 注入当前目录到 sys.path，以便 import byName
_hook_added = False
_pkg_dir = os.path.dirname(os.path.abspath(__file__))
if _pkg_dir not in sys.path:
    sys.path.insert(0, _pkg_dir)

from byName import main as download_main


# ==================== Stdout 重定向 ====================
class TextRedirector(io.StringIO):
    """将 print 输出重定向到 tkinter Text 组件"""

    def __init__(self, text_widget, tag=None):
        super().__init__()
        self.text_widget = text_widget
        self.tag = tag
        self._buffer = []

    def write(self, s):
        if not s:
            return
        self._buffer.append(s)
        # 用 after_idle 保证线程安全地更新 UI
        self.text_widget.after_idle(self._flush)

    def _flush(self):
        text = ''.join(self._buffer)
        self._buffer.clear()
        self.text_widget.configure(state='normal')
        self.text_widget.insert('end', text, self.tag)
        self.text_widget.see('end')
        self.text_widget.configure(state='disabled')

    def flush(self):
        pass


# ==================== GUI ====================
class WnacgGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('绅士漫画下载器 - wnacg')
        self.root.geometry('800x620')
        self.root.resizable(True, True)

        # 变量
        self.name_var = tk.StringVar(value='獵艷管理員')
        self.dir_var = tk.StringVar(value=os.path.join(os.path.expanduser('~'), 'Downloads', 'wnacg'))
        self.running = False
        self._worker = None
        self._done = False       # 防止 _on_done 被多重调用

        self._build_ui()
        self._center_window()

    def _build_ui(self):
        # ----- 顶部：漫画名称 -----
        frame_top = ttk.Frame(self.root, padding=10)
        frame_top.pack(fill='x')

        ttk.Label(frame_top, text='漫画名称：').pack(side='left')
        entry = ttk.Entry(frame_top, textvariable=self.name_var, width=50)
        entry.pack(side='left', padx=(5, 0), fill='x', expand=True)
        entry.bind('<Return>', lambda e: self._start())

        # ----- 保存目录 -----
        frame_dir = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        frame_dir.pack(fill='x')

        ttk.Label(frame_dir, text='保存目录：').pack(side='left')
        entry_dir = ttk.Entry(frame_dir, textvariable=self.dir_var)
        entry_dir.pack(side='left', padx=(5, 5), fill='x', expand=True)
        ttk.Button(frame_dir, text='浏览...', command=self._browse_dir).pack(side='left')

        # ----- 操作按钮 -----
        frame_btn = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        frame_btn.pack(fill='x')

        self.btn_start = ttk.Button(frame_btn, text='▶ 开始下载', command=self._start)
        self.btn_start.pack(side='left', padx=(0, 10))
        self.btn_stop = ttk.Button(frame_btn, text='■ 停止', command=self._stop, state='disabled')
        self.btn_stop.pack(side='left')

        # ----- 日志输出 -----
        frame_log = ttk.LabelFrame(self.root, text='运行日志', padding=5)
        frame_log.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self.log_text = tk.Text(frame_log, wrap='word', state='disabled',
                                font=('Consolas', 10), bg='#1e1e1e', fg='#d4d4d4',
                                insertbackground='white')
        scroll_y = ttk.Scrollbar(frame_log, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll_y.set)
        self.log_text.pack(side='left', fill='both', expand=True)
        scroll_y.pack(side='right', fill='y')

        # ----- 底部：状态栏 -----
        self.status_bar = ttk.Label(self.root, text='就绪', relief='sunken', anchor='w')
        self.status_bar.pack(fill='x', padx=10, pady=(0, 5))

    def _center_window(self):
        self.root.update_idletasks()
        w, h = 800, 620
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f'{w}x{h}+{x}+{y}')

    def _browse_dir(self):
        d = filedialog.askdirectory(title='选择保存目录', initialdir=self.dir_var.get())
        if d:
            self.dir_var.set(d)

    def _log(self, msg):
        """安全地向日志框追加文字"""
        self.log_text.after_idle(lambda: self._log_sync(msg))

    def _log_sync(self, msg):
        self.log_text.configure(state='normal')
        self.log_text.insert('end', msg + '\n')
        self.log_text.see('end')
        self.log_text.configure(state='disabled')

    # ----- 启动 / 停止 -----
    def _set_ui_idle(self, idle):
        state = 'normal' if idle else 'disabled'
        self.btn_start.configure(state=state)
        self.btn_stop.configure(state='disabled' if idle else 'normal')
        self.status_bar.configure(text='就绪' if idle else '运行中…')

    def _start(self):
        name = self.name_var.get().strip()
        save_dir = self.dir_var.get().strip()
        if not name:
            messagebox.showwarning('提示', '请输入漫画名称')
            return
        if not save_dir:
            messagebox.showwarning('提示', '请选择保存目录')
            return

        if self.running:
            return

        self.running = True
        self._done = False
        self._set_ui_idle(False)
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.configure(state='disabled')

        # 重定向 stdout → GUI
        self._old_stdout = sys.stdout
        sys.stdout = TextRedirector(self.log_text)

        self._worker = threading.Thread(
            target=self._run_task,
            args=(name, save_dir),
            daemon=True,
        )
        self._worker.start()
        self.root.after(100, self._poll_worker)

    def _stop(self):
        """标记停止（线程无法强制终止，设标志后等它自然结束）"""
        if not self.running:
            return
        self.running = False
        self._log_sync('\n⚠ 用户请求停止（等待当前任务完成后退出…）')
        self.btn_stop.configure(state='disabled')

    def _run_task(self, name, save_dir):
        """在后台线程中执行下载"""
        try:
            download_main(name=name, save_dir=save_dir)
        except Exception as e:
            print(f'\n✗ 程序异常退出：{e}')
        finally:
            self.root.after_idle(self._on_done)

    def _on_done(self):
        """恢复 stdout，更新 UI（防止多重调用）"""
        if self._done:
            return
        self._done = True
        if self._old_stdout:
            sys.stdout = self._old_stdout
        self.running = False
        self._set_ui_idle(True)
        self._log_sync('\n程序结束。')
        messagebox.showinfo('完成', '全部任务结束，请查看日志。')

    def _poll_worker(self):
        """定期检查 worker 是否已结束（意外退出兜底）"""
        if self._worker and self._worker.is_alive():
            self.root.after(500, self._poll_worker)
        elif self.running:
            # 线程挂了但 _on_done 没跑 → 兜底
            self._on_done()

    def run(self):
        self.root.protocol('WM_DELETE_WINDOW', self._on_close)
        self.root.mainloop()

    def _on_close(self):
        if self.running:
            if not messagebox.askyesno('确认退出', '下载任务还在运行，确定要退出吗？\n（可能留下不完整的文件）'):
                return
            self.running = False
        self.root.destroy()


if __name__ == '__main__':
    app = WnacgGUI()
    app.run()
