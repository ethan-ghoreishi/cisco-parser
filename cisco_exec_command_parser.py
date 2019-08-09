#!/usr/bin/env python
# coding: utf-8

from netmiko import ConnectHandler
import re
import numpy as np
# import nltk
import os
import string
import random
import re

device = ConnectHandler(device_type="cisco_ios", ip="", username="", password="", secret="")


## store output of '?' command in xec mode (in  form of [command, command description]) into a list

device.enable()
counter_1 = 0
for no_layers in range(3):
    counter_1 += 1
    if counter_1 == 1:
        xec_cmd_layer_1 = []
        xec_cmd_layer_1 = device.send_command("?").split('\n')[2:-2] # remove first line and the last 2 lines (hostname)
        xec_cmd_desc_layer_1 = [" ".join(i.split()).split(" ", 1) 
                                                     for i in xec_cmd_layer_1]
    
    
    else:
        exec(f"xec_cmd_desc_layer_{str(counter_1)} = []") # dyamically create a list name for the respective layer 
        for cmd_desc_1 in vars()["xec_cmd_desc_layer_"+str(counter_1-1)]:
            counter_2 = 0
            if counter_1 == 2:
                help_cmd_output = device.send_command(cmd_desc_1[0]+" ?" "\x03").split('\n')
                try:
                    vars()["xec_cmd_desc_layer_"+str(counter_1)].append([[cmd_desc_1[0] + " " + " ".join(j.split()).split(" ", counter_1-1)[0], 
                                                                  " ".join(j.split()).split(" ", 1)[1]] 
                                                                 for j in help_cmd_output if len(" ".join(j.split()).split(" ", counter_1-1)) > counter_1-1])
                except IndexError:
                    pass
            
            elif counter_1 == 3:
                one_xec_cmd_desc = []
                for k in cmd_desc_1:            
                    counter_2 += 1
                    help_cmd_output = device.send_command(k[0]+" ?" "\x03").split('\n')
                    try:
                        one_xec_cmd_desc.append([[k[0] + " " + " ".join(j.split()).split(" ", counter_1-1)[0], 
                                                                  " ".join(j.split()).split(" ", 1)[1]] 
                                                                 for j in help_cmd_output if len(" ".join(j.split()).split(" ", counter_1-1)) > counter_1-1])
                    

                    except IndexError:
                        pass
                    if counter_2 == len(cmd_desc_1):
                        vars()["xec_cmd_desc_layer_"+str(counter_1)].append(one_xec_cmd_desc)                     

			
			
def connect_mongodb_database(db_address, db_name, collection_name):
    try:
        myclient = pymongo.MongoClient(db_address) # MongoDB instance running on GC
        print("Connected successfully!!!") 
    except:   
        print("Could not connect to MongoDB") 

    try:
        mydb = myclient[db_name]
        print("Connected to {}".format(db_name))   

        if mydb.collection_name.count() != 0:
            mydb.confcommands.remove()
            print('{} documents removed'.format(mydb.collection_name.count()))
    except:
        print("Could not connect to {}".format(db_name)) 


connect_mongodb_database('', 'commandsdatabase', 'xeccommands')


# Conver the list to dict to prepare for MongoDB

list_of_dicts = []
# cmd_dict = {}

for i, j in enumerate(xec_cmd_desc_layer_1):
    try:
        cmd_dict = [
            {
                "cmd":
                {
                    "name": j[0],
                    "desc": j[1],
                    "c1": 
                    [
                        {
                            "_id": str(k+1), 
                            "name": l[0], 
                            "desc": l[1],
                            "c2": 
                                [
                                    {
                                    "_id": str(m+1), 
                                    "n": n[0], 
                                    "d": n[1]
                                    }
                                for m, n in enumerate(xec_cmd_desc_layer_3[i][k]) if len(l) > 0
                                ]

                        }
                        for k, l in enumerate(xec_cmd_desc_layer_2[i]) if len(l) > 0
                    ]
                }
            }
        ]
    #     cmd_dict = {j[0].replace('.', ''):j[1] for j in i}
        list_of_dicts.append(cmd_dict)
    except IndexError:
        cmd_dict = [
            {
                "cmd":
                {
                    "name": j[0],
                    "desc": j[1],
                    "c1": 
                    [
                        {
                            "_id": str(k+1), 
                            "name": l[0], 
                            "desc": l[1],

                        }
                        for k, l in enumerate(xec_cmd_desc_layer_2[i]) if len(l) > 0
                    ]
                }
            }
        ]
        list_of_dicts.append(cmd_dict)


# Insert all commands:descriptions into MongoDB
for i in list_of_dicts:
    mydb.xeccommands.insert_one(i[0])


desc_list = []
cmd_list = []
for i in mydb.xeccommands.find({}):
    desc_list.append(i["cmd"]["desc"])
    cmd_list.append(i["cmd"]["name"])
    for j in i["cmd"]["c1"]:
        desc_list.append(j["desc"])
        cmd_list.append(j["name"])        
        try:
            for k in j["c2"]:
                desc_list.append(k["d"])
                cmd_list.append(k["n"])
#                 desc_word.append(nltk.word_tokenize(k['d'].lower())[0])
        except KeyError:
            pass
