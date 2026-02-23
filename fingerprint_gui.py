# fingerprint_gui.py 生成机器指纹GUI界面
import hashlib
import winreg
import tkinter as tk
from tkinter import messagebox

def get_machine_guid() -> str:
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
    guid, _ = winreg.QueryValueEx(key, "MachineGuid")
    return str(guid).strip()

def machine_fingerprint() -> str:
    guid = get_machine_guid().encode("utf-8")
    return hashlib.sha256(guid).hexdigest()

if __name__ == "__main__":
    fp = machine_fingerprint()

    root = tk.Tk()
    root.withdraw()  # 不显示主窗口

    # 复制到剪贴板
    root.clipboard_clear()
    root.clipboard_append(fp)
    root.update()

    messagebox.showinfo(
        "EVALERT RequestCode",
        f"机器指纹（已复制到剪贴板）：\n\n{fp}\n\n直接粘贴发给授权方即可。"
    )
    root.destroy()