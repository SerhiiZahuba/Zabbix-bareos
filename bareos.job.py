#! /usr/bin/env python3
import sys
import bareos.bsock
import argparse
import time
import datetime
import re
import yaml
import datetime

configfile = '/etc/zabbix/zabbix_bareos.yml'

with open(configfile, 'r') as ymlfile:
    config = yaml.load(ymlfile, yaml.SafeLoader)

user = config['user']
password = bareos.bsock.Password(config['password'])
host = config.get('host', "localhost")
port = config.get('port', 9101)

def create_console():
    console = bareos.bsock.DirectorConsoleJson(
        address=host, port=port, name=user, password=password
    )
    return console


def last_status(args):
    console = create_console()
    last_job = console.call('llist job="{}" last'.format(args.job))
    print((last_job["jobs"][0]["jobstatus"]))


def last_size(args):
    console = create_console()
    last_job = console.call('llist job="{}" jobstatus=T last'.format(args.job))
    print((last_job["jobs"][0]["jobbytes"]))


def get_time(args):
    console = create_console()
    t = console.call("time")["time"]
    dt = datetime.datetime(
        int(t["year"]),
        int(t["month"]),
        int(t["day"]),
        int(t["hour"]),
        int(t["minute"]),
        int(t["second"]),
    )
    print((int(time.mktime(dt.timetuple()))))


def get_total_jobs(args):
    console = create_console()
    total_jobs = console.call('.sql query="SELECT COUNT(Job) FROM Job;"')
    try:
        if total_jobs["query"][0].get("count"):
            print((total_jobs["query"][0]["count"]))
        else:
            print((total_jobs["query"][0]["count(job)"]))
    except KeyError:
        print((-1))


def get_job_estimate(args):
    console = bareos.bsock.DirectorConsole(
        address=host, port=port, name=user, password=password
    )
    # console.send("estimate job={}".format(args.job))
    estimate = console.call('estimate job="{}"'.format(args.job))
    estimate_str = estimate.decode('utf-8')  # Декодуємо bytes у рядок
    m = re.search("bytes=([0-9,]+)", re.sub(",", "", estimate_str))
    print((int(m.group(1))))


def last_files(args):
    console = create_console()
    last_job = console.call('llist job="{}" last'.format(args.job))
    try:
        print((last_job["jobs"][0]["jobfiles"]))
    except (KeyError, IndexError):
        print("No job files information available.")

def last_backup_level(args):
    console = create_console()
    last_job = console.call('llist job="{}" last'.format(args.job))
    try:
        level = last_job["jobs"][0]["level"]
        # Перевірка рівня резервного копіювання
        if level == "F":
            print("Full")
        elif level == "D":
            print("Diff")
        else:
            print(level)
    except (KeyError, IndexError):
        print("No backup level information available.")

def last_errors(args):
    console = create_console()
    last_job = console.call('llist job="{}" last'.format(args.job))
    try:
        # Отримання значення поля "joberrors"
        errors = last_job["jobs"][0]["joberrors"]
        print(errors)
    except (KeyError, IndexError):
        print("No error information available.")

#from datetime import datetime

def backup_duration(args):
    console = create_console()
    last_job = console.call('llist job="{}" last'.format(args.job))
    try:
        # Отримання часу початку та завершення
        start_time = last_job["jobs"][0]["starttime"]
        end_time = last_job["jobs"][0]["endtime"]

        # Перетворення рядків у datetime-об'єкти
        start = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

        # Обчислення тривалості у секундах
        duration_seconds = (end - start).total_seconds()

        # Виведення тривалості
        print(int(duration_seconds))  # Виведення цілим числом
    except (KeyError, IndexError):
        print("No time information available.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    backup_duration_parser = subparsers.add_parser("backup_duration")
    backup_duration_parser.add_argument("job")
    backup_duration_parser.set_defaults(func=backup_duration)

    last_backup_level_parser = subparsers.add_parser("last_backup_level")
    last_backup_level_parser.add_argument("job")
    last_backup_level_parser.set_defaults(func=last_backup_level)

    last_status_parser = subparsers.add_parser("last_status")
    last_status_parser.add_argument("job")
    last_status_parser.set_defaults(func=last_status)

    last_errors_parser = subparsers.add_parser("last_errors")
    last_errors_parser.add_argument("job")
    last_errors_parser.set_defaults(func=last_errors)

    last_size_parser = subparsers.add_parser("last_size")
    last_size_parser.add_argument("job")
    last_size_parser.set_defaults(func=last_size)

    last_files_parser = subparsers.add_parser("last_files")
    last_files_parser.add_argument("job")
    last_files_parser.set_defaults(func=last_files)

    get_time_parser = subparsers.add_parser("get_time")
    get_time_parser.add_argument("null", nargs="?")
    get_time_parser.set_defaults(func=get_time)

    get_total_jobs_parser = subparsers.add_parser("get_total_jobs")
    get_total_jobs_parser.add_argument("null", nargs="?")
    get_total_jobs_parser.set_defaults(func=get_total_jobs)

    get_job_estimate_parser = subparsers.add_parser("get_job_estimate")
    get_job_estimate_parser.add_argument("job")
    get_job_estimate_parser.set_defaults(func=get_job_estimate)

    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.print_help()
        parser.exit()
