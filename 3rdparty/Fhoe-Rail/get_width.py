import win32api
import win32con
import win32gui
import win32print

from utils.config.config import ConfigurationManager
from utils.log import log

def get_width():
    hwnd = win32gui.GetForegroundWindow()  # 根据当前活动窗口获取句柄
    log.info(hwnd)
    Text = win32gui.GetWindowText(hwnd)
    log.info(Text)

    # 获取活动窗口的大小
    window_rect = win32gui.GetWindowRect(hwnd)
    width = window_rect[2] - window_rect[0]
    height = window_rect[3] - window_rect[1]

    # 获取当前显示器的缩放比例
    dc = win32gui.GetWindowDC(hwnd)
    dpi_x = win32print.GetDeviceCaps(dc, win32con.LOGPIXELSX)
    dpi_y = win32print.GetDeviceCaps(dc, win32con.LOGPIXELSY)
    win32gui.ReleaseDC(hwnd, dc)
    scale_x = dpi_x / 96
    scale_y = dpi_y / 96

    # 计算出真实分辨率
    real_width = int(width * scale_x)
    real_height = int(height * scale_y)

    if not ConfigurationManager.normalize_file_path(ConfigurationManager.CONFIG_FILE_NAME):
        ConfigurationManager.init_config_file(real_width=real_width, real_height=real_height)
    
    if real_width != 1920 or real_height != 1080:
        log.warning("请调整分辨率为1920 x 1080")
        log.warning(f"错误的分辨率: {real_width} x {real_height}")
    else:
        pass  # 不执行任何操作，避免输出日志

    ConfigurationManager.modify_json_file(ConfigurationManager.CONFIG_FILE_NAME, "real_width", real_width)
    ConfigurationManager.modify_json_file(ConfigurationManager.CONFIG_FILE_NAME, "real_height", real_height)



def check_mult_screen():
    """ 检查是否使用多块屏幕 """
    sc_infos = win32api.EnumDisplayMonitors()
    if len(sc_infos) > 1:
        sc_list = []
        for index, sc in enumerate(sc_infos):
            info = win32api.GetMonitorInfo(sc_infos[index][0])
            hdc = win32gui.CreateDC(info['Device'], info['Device'], None)
            w = win32print.GetDeviceCaps(hdc, 118)
            s = w / (sc[2][2] - sc[2][0])
            sc_list.append(s)
        # 检查缩放比例是否一致
        is_ok = True
        for i in sc_list:
            if abs(i - sc_list[0]) >= 0.001:
                is_ok = False
                break
        if not is_ok:
            log.warning(f"您当前使用{len(sc_infos)}块屏幕，且缩放比例不一致，请确保游戏运行在主屏幕上")
