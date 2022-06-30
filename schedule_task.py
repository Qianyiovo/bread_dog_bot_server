import schedule
import shutil
import time


def backup():
    """
    每天备份一次数据库
    :return:
    """
    now_time = time.strftime("%Y-%m-%d", time.localtime())
    open(f"backups//{now_time}.sqlite3.bak", "w")
    shutil.copyfile("db.sqlite3", f"backups//{now_time}.sqlite3.bak")
    print("备份成功")


schedule.every().day.do(backup)

while True:
    schedule.run_pending()
    time.sleep(1)
