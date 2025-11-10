import sys
import os
import traceback
import ctypes # 我们用它来在 GUI 模式下显示错误弹窗

# 导入 pdfCropMargins 的主函数
try:
    from pdfCropMargins.pdfCropMargins import main as pdfCropMargins_main
except ImportError:
    print("错误：未找到 pdfCropMargins 库。")
    sys.exit(1)

def get_application_path():
    """获取可执行文件所在的目录"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def show_gui_error(title, text):
    """使用 ctypes 弹窗显示错误"""
    try:
        ctypes.windll.user32.MessageBoxW(0, text, title, 0x10) # 0x10 是 MB_ICONERROR
    except Exception:
        pass # 即使弹窗失败，也继续

def main_wrapper():
    try:
        app_dir = get_application_path()
        
        gs_exe_path = os.path.join(
            app_dir, 
            "_internal",
            "ghostscript", 
            "bin", 
            "gswin64c.exe"
        )
        
        if not os.path.exists(gs_exe_path):
            error_msg = f"致命错误：未找到依赖的 Ghostscript。\n请检查路径：{gs_exe_path}"
            show_gui_error("依赖缺失", error_msg)
            sys.exit(1)

        # -------------------- [!! 核心 GUI 逻辑 !!] --------------------
        
        # 1. 检查用户是否只是双击了 .exe
        #    len(sys.argv) == 1 意味着没有其他参数
        if len(sys.argv) == 1:
            print("[Wrapper] 检测到双击启动，自动注入 -gui 参数。")
            sys.argv.append("-gui")

        # 2. 无论如何，都注入 Ghostscript 路径
        sys.argv.extend(["-gsp", gs_exe_path])
        
        print(f"[Wrapper] 启动 pdfCropMargins...")
        print(f"[Wrapper] 最终命令行: {sys.argv}")
        
        # 3. 运行主程序
        pdfCropMargins_main() 
        
        # ---------------------------------------------------------
        
    except Exception as e:
        # 如果程序崩溃，我们必须用弹窗显示错误，因为控制台将不可见
        error_info = traceback.format_exc()
        print("!!!!!!!!!!!!!! 程序意外崩溃 !!!!!!!!!!!!!!")
        print(error_info)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        show_gui_error("程序意外崩溃", f"发生了一个未处理的错误：\n\n{error_info}")
        sys.exit(1)

if __name__ == "__main__":
    main_wrapper()