import subprocess, time, sys, os

def run_sentinel():
    print("🛰️ [Sentinel] 哨兵監控啟動。正在確保 Ariel 系統運行穩定...")
    while True:
        # 啟動主程式
        process = subprocess.Popen([sys.executable, "ariel_main.py"])
        process.wait()
        
        # 規範第 1 章：異常重啟機制
        if process.returncode != 0:
            print(f"⚠️ 偵測到核心崩潰 (碼: {process.returncode})。5秒後啟動自癒復原...")
            time.sleep(5)
        else:
            print("✅ 系統正常維護重啟中...")
            time.sleep(2)

if __name__ == "__main__":
    run_sentinel()
