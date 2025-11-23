#==============================================================================
#                    版本：v1.0  日期：2025-11-23
#==============================================================================
#郑重说明：
#    本项目为开放性项目，可以自由使用和修改，但禁止用于商业用途。
#    使用本项目即表示您同意自行承担使用风险，作者不对任何直接或间接的损失负责。
#    iso下载地址为第三方公开提供，若涉及版权和病毒问题请联系删除。
#    本项目禁止用于任何商业用途，违者必究。
#
#    作者：xujz 开发团队：book11（1人）
#    心里指导：冰冰妈（个屁）
#    玩耍朋友：冰冰妈（个屁）
#    开源地址：https://github.com/xujz66666/-
#    AI协助：豆包
#==============================================================================

import os 
import time
from urllib.request import urlopen
from tqdm import tqdm
import subprocess
from urllib.request import urlopen, URLError, HTTPError
import psutil
import platform
from url import *

class Install:
    def __init__(self, user_configuration={}):
        """定义属性"""
        self.user_configuration = user_configuration
        self.download_dir = self.user_configuration.get('download_dir', '.') # 下载位置
        self.chunk_size = 1024 * 1024  # 1MB块大小
        self.os_type = platform.system()

    def win11_check(self):
        """Win11硬件检测"""
        WIN11_MIN_REQUIREMENTS = {
            "ram_gb": 4,
            "disk_gb": 64,
            "tpm_version": 2.0,
            "cpu_ghz_min": 1.0,
            "cpu_cores_min": 2,
        }
        
        checks = {
            "ram": False,
            "disk": False,
            "cpu": False,
            "tpm": False
        }
        
        mem = psutil.virtual_memory()
        total_gb = round(mem.total / (1024**3), 1)
        checks["ram"] = total_gb >= WIN11_MIN_REQUIREMENTS["ram_gb"]
        
        disk = psutil.disk_usage(os.environ.get("SYSTEMDRIVE", "C:"))
        free_gb = round(disk.free / (1024**3), 1)
        checks["disk"] = free_gb >= WIN11_MIN_REQUIREMENTS["disk_gb"]
        
        cpu_cores = psutil.cpu_count(logical=False) or 0
        cpu_freq = (psutil.cpu_freq().current / 1000) if psutil.cpu_freq() else 0
        checks["cpu"] = (cpu_cores >= WIN11_MIN_REQUIREMENTS["cpu_cores_min"] and 
                        cpu_freq >= WIN11_MIN_REQUIREMENTS["cpu_ghz_min"])
        
        def run_cmd(cmd):
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="gbk", errors="ignore")
                return result.stdout.strip() if result.returncode == 0 else None
            except Exception as e:
                print(f"执行命令时出错: {e}")
                return None
        
        tpm_output = run_cmd("tpmtool getdeviceinformation")
        checks["tpm"] = tpm_output and "TPM 2.0" in tpm_output
        
        print("\nWin11硬件检查结果:")
        print(f"内存: {total_gb}GB (需要≥4GB) - {'通过' if checks['ram'] else '不通过'}")
        print(f"磁盘空间: {free_gb}GB (需要≥64GB) - {'通过' if checks['disk'] else '不通过'}")
        print(f"CPU: {cpu_cores}核 @ {cpu_freq}GHz (需要≥2核 @ ≥1.0GHz) - {'通过' if checks['cpu'] else '不通过'}")
        print(f"TPM: {'TPM 2.0' if checks['tpm'] else '未检测到TPM 2.0'} - {'通过' if checks['tpm'] else '不通过'}")
        
        return all(checks.values())
    
    def download_file(self, url, filename):
        """通用下载函数"""
        save_path = os.path.join(self.download_dir, filename) 
        
        if os.path.exists(save_path):
            file_size = os.path.getsize(save_path)
            print(f"\n文件 {filename} 已存在，大小: {file_size / (1024**3):.2f} GB")
            choice = input("是否重新下载? (y/n): ")
            if choice.lower() != 'y':
                print("跳过下载")
                return True
        
        try:
            print(f"\n开始下载: {filename}")
            print(f"来源: {url}")
            
            with urlopen(url) as response:
                file_size = int(response.headers.get("Content-Length", 0))
                
                with tqdm(
                    total=file_size,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=filename,
                    ascii=True
                ) as progress_bar:
                    with open(save_path, "wb") as file:
                        while True:
                            chunk = response.read(1024 * 1024)
                            if not chunk:
                                break
                            file.write(chunk)
                            progress_bar.update(len(chunk))
            
            print(f"\n下载完成: {save_path}")
            return True
            
        except HTTPError as e:
            print(f"HTTP错误: {e.code} - {e.reason}")
        except URLError as e:
            print(f"URL错误: {e.reason}")
        except Exception as e:
            print(f"下载失败: {str(e)}")
        
        return False
    
    def _validate_iso_file(self, iso_path: str) -> bool:
        """验证ISO文件是否有效"""
        if not os.path.exists(iso_path):
            print(f"错误：ISO文件不存在 - {iso_path}")
            return False
        if not os.path.isfile(iso_path):
            print(f"错误：不是有效的文件 - {iso_path}")
            return False
        if os.path.getsize(iso_path) < 10 * 1024 * 1024:
            print("警告：ISO文件过小，可能不是有效的镜像文件")
        return True

    def _validate_target_device(self, device_path: str) -> bool:
        """验证目标设备是否有效"""
        if self.os_type == "Linux":
            if not os.path.exists(device_path) or not os.path.isblock(device_path):
                print(f"错误：不是有效的块设备 - {device_path}")
                return False
        elif self.os_type == "Windows":
            try:
                with open(device_path, "rb"):
                    pass
            except Exception as e:
                print(f"错误：无法访问目标设备 - {e}")
                return False
        else:
            print(f"不支持的操作系统：{self.os_type}")
            return False
        return True

    def _get_device_size(self, device_path: str):
        """获取设备大小（字节）"""
        try:
            if self.os_type == "Linux":
                return os.path.getsize(device_path)
            elif self.os_type == "Windows":
                try:
                    import win32file
                    handle = win32file.CreateFile(
                        device_path,
                        win32file.GENERIC_READ,
                        win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
                        None,
                        win32file.OPEN_EXISTING,
                        0,
                        None
                    )
                    size = win32file.GetFileSize(handle)
                    win32file.CloseHandle(handle)
                    return size
                except ImportError:
                    print("警告：无法获取Windows设备大小，请安装pywin32库")
                    return None
        except Exception as e:
            print(f"获取设备大小失败：{e}")
            return None

    def write_iso_to_device(self, iso_path: str, device_path: str, confirm: bool = True) -> bool:
        """将ISO文件写入目标设备"""
        if not self._validate_iso_file(iso_path):
            return False
        if not self._validate_target_device(device_path):
            return False
        
        iso_size = os.path.getsize(iso_path)
        device_size = self._get_device_size(device_path)
        
        if device_size and iso_size > device_size:
            print(f"错误：ISO文件大小({iso_size/1024/1024:.1f}MB)大于设备容量({device_size/1024/1024:.1f}MB)")
            return False
        
        if confirm:
            print("\n警告：此操作将清除目标设备上的所有数据！")
            print(f"ISO文件: {iso_path} ({iso_size/1024/1024:.1f}MB)")
            print(f"目标设备: {device_path}")
            if device_size:
                print(f"设备容量: {device_size/1024/1024:.1f}MB")
            
            user_input = input("\n确认继续？(YES/no): ").strip().upper()
            if user_input != "YES":
                print("操作已取消")
                return False
        
        try:
            print("\n开始写入...")
            start_time = time.time()
            
            with open(iso_path, "rb") as iso_file:
                with open(device_path, "wb") as dev_file:
                    bytes_written = 0
                    while True:
                        chunk = iso_file.read(self.chunk_size)
                        if not chunk:
                            break
                        
                        dev_file.write(chunk)
                        bytes_written += len(chunk)
                        
                        progress = (bytes_written / iso_size) * 100
                        elapsed = time.time() - start_time
                        speed = bytes_written / (1024*1024) / elapsed if elapsed > 0 else 0
                        print(f"\r进度: {progress:.1f}% | 已写入: {bytes_written/1024/1024:.1f}MB | 速度: {speed:.1f}MB/s", end="")
            
            if self.os_type == "Linux":
                os.sync()
            print("\n\n写入完成！正在同步缓存...")
            time.sleep(2)
            
            elapsed_time = time.time() - start_time
            print(f"\n操作成功完成！")
            print(f"总耗时: {elapsed_time:.1f}秒 | 平均速度: {iso_size/(1024*1024)/elapsed_time:.1f}MB/s")
            return True
            
        except PermissionError:
            print("\n权限不足！请以管理员/root身份运行此程序")
            return False
        except Exception as e:
            print(f"\n写入失败：{str(e)}")
            return False
    
    def write_iso_to_device_prompt(self):
        """交互式ISO写入功能"""
        print("\n" + "="*50)
        print("ISO写入工具")
        print("="*50)
        
        iso_path = input("\n请输入ISO文件路径: ").strip()
        if not iso_path:
            print("错误：ISO路径不能为空")
            return
        
        print(f"\n当前系统: {self.os_type}")
        if self.os_type == "Linux":
            print("提示：Linux设备路径格式如 /dev/sdb (注意：不是分区如 /dev/sdb1)")
            print("      可使用 lsblk 命令查看设备列表")
        elif self.os_type == "Windows":
            print("提示：Windows设备路径格式如 \\\\.\\PhysicalDrive1")
            print("      可通过磁盘管理查看磁盘编号")
        
        device_path = input("\n请输入目标设备路径: ").strip()
        if device_path:
            self.write_iso_to_device(iso_path, device_path)
    
    def download_system(self):
        """下载系统ISO"""
        print("\n" + "="*50)
        print("系统ISO下载功能")
        print("="*50)
        
        url = None 
        save_path = None

        user_type = input("\n你想下载哪种系统[windows(w)/linux(l)]:")
        
        if user_type == "w":
            print("正在操作...")
            time.sleep(2)
            print("已选择Windows系统")
            user_windows_type = input("请选择Windows版本[11,10,8.1,7,xp]:")

            if user_windows_type == "11":
                url = windows_11
                save_path = "windows_11.iso"
                if not self.win11_check():
                    print("你的系统硬件配置不足，无法安装Win11，但仍可下载ISO文件")
                    choice = input("是否继续下载？(y/n): ")
                    if choice.lower() != 'y':
                        return
                print("正在下载Windows 11 ISO...")
                
            elif user_windows_type == "10":
                url = windows_10
                save_path = "windows_10.iso"
                print("正在下载Windows 10 ISO...")

            elif user_windows_type == "8.1":
                url = windows_8_1
                save_path = "windows_8_1.iso"
                print("正在下载Windows 8.1 ISO...")

            elif user_windows_type == "7":
                url = windows_7
                save_path = "windows_7.iso"
                print("正在下载Windows 7 ISO...")

            elif user_windows_type == "xp":
                url = windows_xp
                save_path = "windows_xp.iso"
                print("正在下载Windows XP ISO...")

            else:
                print("错误：无效的Windows版本")
                return
            
            
        elif user_type == "l":
            print("正在操作...")
            time.sleep(2)
            print("已选择Linux系统")
            user_linux_type = input("请选择Linux版本[ubuntu(u),arch(a),centos(c)]:")
            
            if user_linux_type == "u":
                url = ubuntu
                save_path = "ubuntu.iso"
                print("正在下载Ubuntu ISO...")

            elif user_linux_type == "a":
                url = arch
                save_path = "arch.iso"
                print("正在Arch Linux ISO...")

            elif user_linux_type == "c":
                url = centos
                save_path = "centos.iso"
                print("正在下载CentOS ISO...")

            else:
                print("错误：无效的Linux版本")
                return
            
        if url and save_path:
            self.download_file(url, save_path)

def clear_screen():
    """清屏函数，兼容Windows和Linux/Mac"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """主程序入口"""
    # 清屏
    clear_screen()
    
    # 打印欢迎界面
    print("="*60)
    print("           系统ISO下载与启动盘制作工具 v1.0")
    print("="*60)
    print("作者：xujz | 开源地址：https://github.com/xujz66666/-")
    print("="*60)
    
    # 创建安装工具实例
    config = {'download_dir': '.'}
    installer = Install(config)
    
    while True:
        print("\n请选择操作:")
        print("1. 下载系统ISO镜像")
        print("2. 将ISO写入U盘/移动硬盘")
        print("3. 退出程序")
        
        try:
            choice = input("\n输入选项编号(1-3): ").strip()
            
            if choice == "1":
                clear_screen()  # 进入下载功能前清屏
                installer.download_system()
                
            elif choice == "2":
                clear_screen()  # 进入写入功能前清屏
                installer.write_iso_to_device_prompt()
                
            elif choice == "3":
                print("\n感谢使用工具！")
                break
                
            else:
                print("错误：请输入有效的选项编号(1-3)")
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"\n程序出错：{str(e)}")
        
        # 操作完成后的提示
        input("\n按Enter键返回主菜单...")
        clear_screen()  # 返回主菜单前清屏
        
        # 重新打印欢迎界面
        print("="*60)
        print("           系统ISO下载与启动盘制作工具 v2.0")
        print("="*60)
        print("作者：xujz | 开源地址：https://github.com/xujz66666/-")
        print("="*60)
    
    # 程序结束提示
    print("\n" + "="*60)
    print("程序已退出，按任意键关闭窗口...")
    input()

if __name__ == "__main__":
    main()
