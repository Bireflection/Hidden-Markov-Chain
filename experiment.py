import numpy as np
import pandas as pd
import mysql.connector as conn
from sqlalchemy import create_engine
import pymysql

import findspark
findspark.init()
from pyspark import SparkContext, SparkConf
from pyspark.sql import SQLContext
sc = SparkContext.getOrCreate()


sqlEngine = create_engine('mysql+pymysql://root:lab5212@db', pool_recycle=3600)
dbConnection = sqlEngine.connect()

malware_df = pd.read_sql("select * from malware.malware", dbConnection)

# pd.set_option('display.expand_frame_repr', False)

botnet_ip = malware_df["Botnet_IP"].values.tolist()


import os
path = 'logs'
# path = 'logstest'
files= os.listdir(path)
log_df = pd.DataFrame()
for file in files: #遍历文件夹
     if not os.path.isdir(file):
        try:
#             print("file loaded: "+ path + "/" + file)
            tmp_df = pd.read_csv(path + "/" + file, delim_whitespace=True)
            tmp_df["file"] = file
            log_df = log_df.append(tmp_df, ignore_index=True)
        except:
            print("Error: load data for file " + file)
print(log_df)
log_df["label"] = np.where(log_df["SrcAddr"].isin(botnet_ip) | log_df["DstAddr"].isin(botnet_ip), 1, 0)
print(log_df.info())

path = 'logs2'
# path = 'logstest2'
files= os.listdir(path)
log_oneway_df = pd.DataFrame(columns = ['number', 'time', 'SrcAddr', 'DstAddr', 'Proto', 'Bytes', 'Sport', 'Dport'])
print(log_oneway_df)
for file in files: #遍历文件夹
     if not os.path.isdir(file):
        try:
#             print("file loaded: "+ path + "/" + file)
            # TODO: fix 4 ip in one line
            tmp_df = pd.read_csv(path + "/" + file, sep=",", header=None, error_bad_lines=False)
            tmp_df.columns = ['number', 'time', 'SrcAddr', 'DstAddr', 'Proto', 'Bytes', 'Sport', 'Dport']
#             print(tmp_df)
            tmp_df["file"] = file
            log_oneway_df = log_oneway_df.append(tmp_df, ignore_index=True)
#             break
        except:
            print("Error: load data for file " + file)
log_oneway_df["label"] = np.where(log_oneway_df["SrcAddr"].isin(botnet_ip) | log_oneway_df["DstAddr"].isin(botnet_ip), 1, 0)
print(log_oneway_df.info())

log_oneway_df[['SrcAddr', 'Proto', 'DstAddr', 'Sport', 'Dport', 'file']] \
  = log_oneway_df[['SrcAddr', 'Proto', 'DstAddr', 'Sport', 'Dport', 'file']].astype(str)

dirMap = dict()

for index, row in log_oneway_df.iterrows():
    obj = row['SrcAddr'] + ',' + row['DstAddr']
    if(obj in dirMap):
        continue
    else:
        dirMap[obj] = 1
        dirMap[row['DstAddr'] + ',' + row['SrcAddr']] = -1

print(dirMap)

pre_df = log_oneway_df.copy()
def assign_obj(df):
#     type(name)
    name = df.SrcAddr + ',' + df.DstAddr
#     print(name)
    return name if dirMap[name] == 1 else df.DstAddr+','+df.SrcAddr
# pre_df['obj'] = assign_obj(pre_df['SrcAddr'].astype(str), pre_df['DstAddr'].astype(str))
# pre_df['obj'] = pre_df['SrcAddr'].astype(str) + ',' + pre_df['DstAddr'].astype(str)
# pre_df[dirMap[pre_df.obj.to_string()]==-1, obj]  = pre_df['DstAddr'].astype(str) + ',' + pre_df['SrcAddr'].astype(str)
# pre_df['data'] = pre_df['Bytes'] if dirMap[pre_df['obj'].to_string()] == 1  else -1 * pre_df['Bytes']
# pre_obj['obj'] = dirMap[pre_obj['obj']] == 1 ? pre_obj['obj'] : pre_obj['DstAddr'].astype(str) + ',' + pre_obj['SrcAddr'].astype(str)
def assign_data(df):
    name = df.SrcAddr + ',' + df.DstAddr
#     print(name)
    return df.Bytes if dirMap[name] == 1 else -1 * df.Bytes

pre_df['obj'] = pre_df.apply(assign_obj, axis=1)
pre_df['data'] = pre_df.apply(assign_data, axis=1)

pre_df[['obj', 'SrcAddr', 'Proto', 'DstAddr', 'Sport', 'Dport', 'file']] \
  = pre_df[['obj', 'SrcAddr', 'Proto', 'DstAddr', 'Sport', 'Dport', 'file']].astype(str)
# pre_df[['data', 'label']] = pre_df[['data', 'label']].astype(int)
pre_df[['time']] = pre_df[['time']].astype(float)
# convert one way dataframe to rdd
pre_rdd = SQLContext(sc).createDataFrame(pre_df[['data', 'obj', 'label', 'time']]).rdd
pre_rdd.count()

input_rdd = pre_rdd\
    .map(lambda p: ((p.obj, p.label), [[p.data, p.time]]))\
    .reduceByKey(lambda a, b: a+b)
input_rdd.count()

capacity = 5
def genSignMap(): 
    alphabet = [chr(i) for i in range(97,123)]
    signMap = dict()
    i = 0
    for l1 in alphabet:
        for l2 in alphabet:
            signMap[-1600 + capacity * i] = l1 + l2
            i += 1
            if(i * capacity > 3200):
                return signMap
            
signMap = genSignMap()
print(signMap)
def serializeData(row):
    header = row[0]
    dataSeq = row[1]
    seq = []
    for d in dataSeq:
        try:
            tmp = int(d[0] / capacity)
            factor = tmp if d[0] < 0 else tmp + 1
            sign = signMap[factor * capacity]
            seq.append(sign)
        except:
            print("Error data: " + str(d[0]))
    return (header, seq)
    
seq_rdd = pre_rdd\
    .filter(lambda p: p.label < 2)\
    .map(lambda p: ((p.obj, p.label), [[p.data, p.time]]))\
    .reduceByKey(lambda a, b: a+b)\
    .map(serializeData)

# seq_rdd.map(lambda p: (p[0], "".join(p[1]))).filter(lambda p: p[0][1]==1).take(30)


import os
# gene seq max length
length = 50

seq_list = seq_rdd.map(lambda p: (p[0][0] + "," + str(p[0][1]), "".join(p[1]))).collect()
data_dir = "ProfileHMM/data/exp/"
if not os.path.isdir(data_dir):
    os.makedirs(data_dir)
# seq_list = seq_list[:5]
with open(data_dir + "train_" + str(length) + ".fasta", 'a+') as f:
    for d in seq_list:
        f.write(">" + d[0] + "\n")
        tmp = d[1]
        if len(tmp) >= length:
            tmp = tmp[ : length]
        else:
            for i in range(length - len(tmp)):
                tmp += "-"
        if len(tmp) != length:
            print(len(tmp))
            print(length)
            print("\nERROR data length!")
            sys.exit(0)
        f.write(tmp + "\n")
print("Save data Successfully!")
