from datetime import datetime
import json
import os
import pathlib
from time import time, sleep

from discord import Discord


def wr_file(file_name, mode, payload):
    if mode == 'write':
        try:
            with open(file_name, mode='wt', encoding='utf-8') as file:
                json.dump(payload, file, ensure_ascii=False, indent=2)
        except json.decoder.JSONDecodeError:
            sleep(1)
            file_name(file_name, mode, payload)
    elif mode == 'read':
        try:
            with open(file_name, mode='rt', encoding='utf-8') as file:
                if payload == 'json':
                    result = json.load(file)
                elif payload == 'readline':
                    result = file.readlines()
                else:
                    raise ValueError('payload is wrong')
                return result
        except json.decoder.JSONDecodeError:
            sleep(1)
            file_name(file_name, mode, payload)
    else:
        raise ValueError('Mode is wrong')


def check_working():
    """
    動作中のプログラムに関して、今の時間と前回の.logファイルの書き込みを見て正しく動作しているか確認する
    While文で実行
    """
    dir_ = pathlib.Path(os.getcwd())
    logfile_dirs = list(map(str, list(dir_.glob("**/status.json"))))
    for logfile_dir in logfile_dirs:
        logfiles = wr_file(logfile_dir, 'read', 'json')
        for status in logfiles.get("working_status"):
            if status["status"] == "ON":
                latest_working_time = status['latest_working_time']
                if int(time()) - latest_working_time > status['interval']:
                    Discord(
                        channel_name='status',
                        msg=f'''
{"-" * 50}
{datetime.now().strftime("%Y/%m/%d %H:%M")}
{status["name"]} stopped!'''
                            )
                    sleep(3000)


def main():
    try:
        while True:
            try:
                check_working()
                sleep(5)
            except FileNotFoundError:
                pass
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
