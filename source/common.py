#-*- coding: utf-8 -*-
import pandas as pd
import yaml
import os, sys

parentPath = os.path.abspath("..")
if parentPath not in sys.path:
    sys.path.insert(0, parentPath)
data_path = os.path.abspath("data")

def load_yaml(filename):
    """
    load a yaml file.

    :param str filename: a yaml filename

    :returns dict: parsed yaml data
    """
    # confDir = os.path.abspath('./conf')
    # fileDir = os.path.dirname(os.path.realpath(__file__))


    filePath = os.path.join(data_path , filename)

    with open(filePath, 'r') as stream:
        data = yaml.load(stream)
    return data


def write_yaml(filename, data):
    confParentPath = os.path.abspath("..")
    filePath = os.path.join(data_path, filename)
    with open(filePath, 'w') as stream:
        yaml.dump(data, stream, default_flow_style=False)

def get_data_file_path(file_name):
	full_file_name = "%s/data/%s" % (os.path.dirname(os.path.abspath(__file__)),file_name)
	return full_file_name


def save_stock_data(df, file_name):
    new_file_name = get_data_file_path(file_name)
    df.to_pickle(new_file_name)

def load_stock_data(file_name):
	new_file_name = get_data_file_path(file_name)
	df = pd.read_pickle(new_file_name)
	return df

def get_data_list():
    dataList = []
    dataPath = os.path.abspath("data")
    # print(dataPath)
    for i in os.listdir(dataPath):
        # print(i)
        dataList.append(i)
    return dataList


def get_df_from_file(code, start, end):
    dir_list = get_data_list()
    name = [name for name in dir_list if code in name]
    df = load_stock_data(name[0])
    # print(df.describe())
    df_range = df[start:end]
    return df_range


