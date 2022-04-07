# This Python file uses the following encoding: utf-8
import os.path
import sys
import time

import properties
import wcdapp as wdcd_app
import logging
import argparse
import UIFrames.crash_handle
from PyQt5.QtCore import QEvent


global ch
global app


def exception_hook(exctype, value, traceback):
    global ch
    ch = UIFrames.crash_handle.CrashHandle(exctype, value, traceback)
    ch.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--no-crash-handler', help='Disable the crash handler.', action='store_true')
    parser.add_argument('-d', '--dev', help="Enable developers' features.", action='store_true')
    parser.add_argument('-e', '--experiment-feature', help='Enable some experiment feature', action='store_true')
    parser.add_argument('-t', '--no-theme', help='Disable theme', action='store_true')
    parser.add_argument('-p', '--no-plugins', help='Disable plugins', action='store_true')

    for i in (properties.profile_prefix, properties.plugins_prefix, properties.cache_prefix, properties.log_root):
        if not os.path.exists(i):
            os.mkdir(i)

    arg = parser.parse_args()
    dated_file_handler = logging.FileHandler(time.strftime(properties.log_file_fmt, time.localtime(time.time())),
                                             mode='w')
    latest_file_handler = logging.FileHandler(properties.latest_log_file_fmt, mode='w')
    debug_file_handler = logging.FileHandler(properties.debug_log_file_fmt, mode='w')
    debug_file_handler.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()

    if arg.dev:
        arg.no_crash_handler = True
        arg.experiment_feature = True
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)

    if not arg.no_crash_handler:
        sys.excepthook = exception_hook

    logging.basicConfig(level=logging.INFO,
                        format=properties.log_styles,
                        datefmt=properties.datefmt,
                        handlers=(console_handler, dated_file_handler, latest_file_handler, debug_file_handler))
    logger = logging.getLogger(__name__)
    logger.info('Welcome to W-DesktopCountdown %s.', properties.version)
    app = wdcd_app.WDesktopCD([], logger, arg)
    app.sig_phase2_triggered.emit()
    exit_code = app.exec_()  # 启动事件循环
    logging.info('bye! (return code is %s)', exit_code)
    sys.exit(exit_code)
