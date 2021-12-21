from datetime import datetime
import json
from logging import (
    getLogger, StreamHandler, Formatter, FileHandler, DEBUG,
    INFO
    )
from time import sleep, time


def setup_logger(log_folder, modname=__name__):
    logger = getLogger(modname)
    logger.setLevel(DEBUG)

    sh = StreamHandler()
    sh.setLevel(DEBUG)
    _format = "%(message)s"
    formatter = Formatter(_format)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    fh = FileHandler(log_folder)
    fh.setLevel(INFO)
    fh_formatter = Formatter(_format)
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)
    return logger


class Log:
    def __init__(self, file_name, interval):
        self.interval = interval
        self.file_name = file_name
        self.logging = setup_logger("status.log")
        self.info(f"{self.file_name} start")

    def wr_file(self, file_name, mode, payload):
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
                self.wr_file(file_name, mode, payload)
        else:
            raise ValueError('Mode is wrong')

    def update_json(self, switch='OFF', time_update=False):
        try:
            status = self.wr_file('status.json', 'read', 'json')
            working_statuses = status.get('working_status')
            file_names = []
            for working_status in working_statuses:
                file_names.append(working_status['name'])
            for _ in range(len(working_statuses)):
                if self.file_name in file_names:
                    if self.file_name == working_statuses[_]['name']:
                        working_statuses.pop(_)
                        text = self.wr_file('status.log', 'read', 'readline')
                        if time_update:
                            latest_working_time = int(time())
                        else:
                            latest_working_time = int(
                                text[-1].split(" - ")[0]
                                )
                        update = {
                            "name": self.file_name,
                            "status": switch,
                            "interval": self.interval,
                            "latest_working_time": latest_working_time
                            }
                    else:
                        continue
                else:
                    update = {
                        "name": self.file_name,
                        "status": switch,
                        "interval": self.interval,
                        "latest_working_time": int(time())
                        }
                working_statuses.append(update)
                status = {'working_status': working_statuses}
                self.wr_file('status.json', 'write', status)
        except FileNotFoundError:
            status_list = []
            status_dict = {
                "name": self.file_name,
                "status": switch,
                "interval": self.interval,
                "latest_working_time": int(time())
                }
            status_list.append(status_dict)
            status = {'working_status': status_list}
            self.wr_file('status.json', 'write', status)

    def end(self):
        self.info(msg='end')
        self.update_json('OFF')

    def debug(self, msg):
        text = self.message('DEBUG', msg)
        self.logging.debug(text)

    def info(self, msg):
        text = self.message('INFO', msg)
        self.logging.info(text)

    def warning(self, msg):
        text = self.message('WARNING', msg)
        self.logging.warning(text)

    def message(self, levelname, msg):
        unix_time = int(time())
        jst = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')
        text = f'{unix_time} - {jst} - {levelname} - {msg}'
        self.update_json('ON')
        return text

    def working(self):
        self.update_json('ON', True)
