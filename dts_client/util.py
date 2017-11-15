from datetime import datetime


def unix_time_to_human(unixtime):
    '''
    :param unixtime: unix timestamp
    :type unixtime: int
    :rtype: string
    '''
    return datetime.fromtimestamp(unixtime).strftime('%Y-%M-%D %H:%M:%S')
