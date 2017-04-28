import yaml
import os
import sys
import datetime, random

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)


def load_yaml(filename):
    """
    load a yaml file.

    :param str filename: a yaml filename

    :returns dict: parsed yaml data
    """
    # confDir = os.path.abspath('./conf')
    # fileDir = os.path.dirname(os.path.realpath(__file__))

    confParentPath = os.path.abspath("..")
    filePath = os.path.join(confParentPath, filename)

    with open(filePath, 'r') as stream:
        data = yaml.load(stream)
    return data


def write_yaml(filename, data):
    confParentPath = os.path.abspath("..")
    filePath = os.path.join(confParentPath, filename)

    with open(filePath, 'w') as stream:
        yaml.dump(data, stream, default_flow_style=False)


def convertTodatetime(time):
    year = str(time)[0:4]
    month = str(time)[5:7]
    day = str(time)[8:10]
    hour = str(time)[11:13]
    minue = str(time)[14:16]
    second = str(time)[17:19]
    return datetime.datetime(int(year), int(month), int(day), int(hour), int(minue), int(second))
