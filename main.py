#==============================================================================
#                    版本：bata 2.0
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







import os # 加载库
import time
from urllib.request import urlopen
from tqdm import tqdm
import subprocess
from urllib.request import urlopen, URLError, HTTPError
import psutil
import platform
from url import * # 加载url变量

class Install:
    def __init__(self,user_configuration={}):
        """定义属性"""
        self.user_configuration=user_configuration
        self.download_dir = self.user_configuration.get('download_dir', '.') # 下载位置
        self.chunk_size = 1024 * 1024  # 1MB块大小
        self.os_type = platform.system()

    def win11_check(self):
        """Win11硬件检测"""
        # 设置标准windows11硬件要求
        WIN11_MIN_REQUIREMENTS = {
            #内存
            "ram_gb": 4,
            #硬盘
            "disk_gb": 64,
            #TPM
            "tpm_version": 2.0,
            # cpu GHz
            "cpu_ghz_min": 1.0,
            # cpu 内核
            "cpu_cores_min": 2,
        }
        
        # 初始化所有检查项为False
        checks = {
            "ram": False,
            "disk": False,
            "cpu": False,
            "tpm": False
        }
        
        # 检查内存
        mem = psutil.virtual_memory()
        total_gb = round(mem.total / (1024**3), 1)
        checks["ram"] = total_gb >= WIN11_MIN_REQUIREMENTS["ram_gb"]
        
        # 检查磁盘
        disk = psutil.disk_usage(os.environ.get("SYSTEMDRIVE", "C:"))
        free_gb = round(disk.free / (1024**3), 1)
        checks["disk"] = free_gb >= WIN11_MIN_REQUIREMENTS["disk_gb"]
        
        # 检查CPU
        cpu_cores = psutil.cpu_count(logical=False) or 0
        cpu_freq = (psutil.cpu_freq().current / 1000) if psutil.cpu_freq() else 0
        checks["cpu"] = (cpu_cores >= WIN11_MIN_REQUIREMENTS["cpu_cores_min"] and 
                        cpu_freq >= WIN11_MIN_REQUIREMENTS["cpu_ghz_min"])
        
        # 检查TPM
        def run_cmd(cmd):
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="gbk", errors="ignore")
                return result.stdout.strip() if result.returncode == 0 else None
            except Exception as e:
                print(f"执行命令时出错: {e}")
                return None
        
        tpm_output = run_cmd("tpmtool getdeviceinformation")
        checks["tpm"] = tpm_output and "TPM 2.0" in tpm_output
        
        # 打印详细检查结果
        print("\nWin11硬件检查结果:")
        print(f"内存: {total_gb}GB (需要≥4GB) - {'通过' if checks['ram'] else '不通过'}")
        print(f"磁盘空间: {free_gb}GB (需要≥64GB) - {'通过' if checks['disk'] else '不通过'}")
        print(f"CPU: {cpu_cores}核 @ {cpu_freq}GHz (需要≥2核 @ ≥1.0GHz) - {'通过' if checks['cpu'] else '不通过'}")
        print(f"TPM: {'TPM 2.0' if checks['tpm'] else '未检测到TPM 2.0'} - {'通过' if checks['tpm'] else '不通过'}")
        
        # 所有检查都通过才返回True
        return all(checks.values())
    
    def download_file(self, url, filename):
        """通用下载函数，避免代码重复"""
        #下载位置
        save_path = os.path.join(self.download_dir, filename) 
        
        if os.path.exists(save_path):
            """文件存在处理"""
            file_size = os.path.getsize(save_path)
            print(f"\n文件 {filename} 已存在，大小: {file_size / (1024**3):.2f} GB")
            choice = input("是否重新下载? (y/n): ")
            if choice.lower() != 'y':
                print("跳过下载")
                # 下载完成后自动调用写入功能
                self.write_iso_to_device_prompt(save_path)
                return True
        
        try:
            """定义下载与进度条"""
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
                            chunk = response.read(1024 * 1024)  # 1MB块
                            if not chunk:
                                break
                            file.write(chunk)
                            progress_bar.update(len(chunk))
            
            print(f"\n下载完成: {save_path}")
            
            # 下载完成后自动调用写入功能
            self.write_iso_to_device_prompt(save_path)
            
            return True
            
        except HTTPError as e:
            """常见错误"""
            print(f"HTTP错误: {e.code} - {e.reason}")
        except URLError as e:
            print(f"URL错误: {e.reason}")
        except Exception as e:
            print(f"下载失败: {str(e)}")
        
        return False
    
            # 新增的ISO写入功能
    def _validate_iso_file(self, iso_path: str) -> bool:
        """验证ISO文件是否有效"""
        if not os.path.exists(iso_path):
            print(f"错误：ISO文件不存在 - {iso_path}")
            return False
        if not os.path.isfile(iso_path):
            print(f"错误：不是有效的文件 - {iso_path}")
            return False
        if os.path.getsize(iso_path) < 10 * 1024 * 1024:  # 小于10MB的ISO大概率无效
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
            print(f"\n 操作成功完成！")
            print(f"总耗时: {elapsed_time:.1f}秒 | 平均速度: {iso_size/(1024*1024)/elapsed_time:.1f}MB/s")
            return True
            
        except PermissionError:
            print("\n权限不足！请以管理员/root身份运行此程序")
            return False
        except Exception as e:
            print(f"\n写入失败：{str(e)}")
            return False
    
    def write_iso_to_device_prompt(self, iso_path):
        """提供交互式的ISO写入提示"""
        print("\n" + "="*50)
        print("ISO写入工具")
        print("="*50)
        
        choice = input("\n是否要将ISO写入U盘/移动硬盘制作启动盘？(y/n): ")
        if choice.lower() != 'y':
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
    # ISO写入功能结束
    
    def install_system(self):
        """选择系统"""
        # 初始化变量
        url = None 
        save_path = None

        user_type = input("你想安装哪种系统[windos(w)/linux(l)]:")
        # windows
        if user_type == "w":
            print("正在操作...")
            time.sleep(2)
            print("已选择Windows系统")
            user_windows_type = input("请选择Windows版本[11,10,8.1,7,xp]:")

            if user_windows_type == "11":
                url = windows_11               # windows 11安装
                save_path = "windows_11.iso"
                if not self.win11_check():
                    print("你的系统不能安装win11，配置不足，请访问微软官网")
                    return
                else:
                    print("正在安装Windows 11...")
                
            elif user_windows_type == "10":
                url = windows_10               # windows 10安装
                save_path = "windows_10.iso"
                print("正在安装Windows 10...")

            elif user_windows_type == "8.1":
                url = windows_8_1              # windows 8.1安装
                save_path = "windows_8_1.iso"
                print("正在安装Windows 8.1...")

            elif user_windows_type == "7":
                url = windows_7                # windows 7安装
                save_path = "windows_7.iso"
                print("正在安装Windows 7...")

            elif user_windows_type == "xp":
                url = windows_xp               # windows xp安装
                save_path = "windows_xp.iso"
                print("正在安装Windows XP...")

            else:
                print("error")
                return
            
            
        elif user_type == "l":
            print("正在操作...")
            time.sleep(2)
            print("已选择Linux系统")
            user_linux_type = input("请选择Linux版本[ubuntu(u),arch(a),centos(c)]:")
            if user_linux_type == "u":
                url = ubuntu                    # ubuntu安装
                save_path = "ubuntu.iso"
                print("正在安装Ubuntu...")

            elif user_linux_type == "a":
                url = arch                      # arch安装
                save_path = "arch.iso"
                print("正在安装Arch Linux...")

            elif user_linux_type == "c":
                url = centos                    # centos安装
                save_path = "centos.iso"
                print("正在安装CentOS...")

            else:
                print("error")
                return
            
            # 安装
        if url and save_path:
            self.download_file(url, save_path)
            

if __name__ == "__main__":
    installer = Install()
    installer.install_system()
