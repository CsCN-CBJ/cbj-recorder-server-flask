from datetime import datetime, timedelta


def timeStrToDateObj(timeStr):
    """
    将ddhhmm类型的时间字符串转换为datetime对象, 支持前一周内的日期, 转换失败返回None
    :param timeStr: ddhhmm
    :return: datetime object
    """
    if len(timeStr) != 6:
        return None
    day, hour, minute = int(timeStr[:2]), int(timeStr[2:4]), int(timeStr[4:])

    # 查找前一周有没有符合的日期
    for i in range(7):
        pre = datetime.now() - timedelta(days=i)
        if pre.day == day:
            return datetime(pre.year, pre.month, pre.day, hour, minute)

    return None
