from datetime import datetime, timedelta
import time
import calendar


# option = ['day', 'week', 'month']

def log_file_name(opt='week'):
    now = datetime.now()
    week_day = now.timetuple().tm_wday
    month_day = now.timetuple().tm_mday
    wday, month_range = calendar.monthrange(now.year, now.month)
    if opt == 'day':
        return time.strftime("%Y-%m-%d.txt", now.timetuple())
    if opt == 'week':
        monday = now - timedelta(days=week_day)
        sunday = now + timedelta(days=6 - week_day)
        str_monday = time.strftime("%Y-%m-%d", monday.timetuple())
        str_sunday = time.strftime("%Y-%m-%d", sunday.timetuple())
        return "%s--%s.txt" % (str_monday, str_sunday)
    if opt == 'month':
        month_end_day = now + timedelta(days=(month_range - month_day))
        str_first_day = time.strftime("%Y-%m-01", month_end_day.timetuple())
        str_last_day = time.strftime("%Y-%m-%d", month_end_day.timetuple())
        return "%s--%s.txt" % (str_first_day, str_last_day)


if __name__ == "__main__":
    print(log_file_name('day'))
    print('------------')
    print(log_file_name('week'))
    print('------------')
    print(log_file_name('month'))
