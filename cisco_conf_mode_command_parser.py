#!/usr/bin/env python
# coding: utf-8

# In[9]:


from netmiko import ConnectHandler
import re
import numpy as np
import pymongo

import os
import string
import random
import re


# In[10]:


device = ConnectHandler(device_type="cisco_ios", ip="172.16.0.10", username="ehsan", password="ehgh1363", secret="ehgh1363")


# In[11]:


# identify a numeric range at the end of the command (e.g. <100-200>), convert it to an integer before adding ?
def genenrate_number_ip(command):
    if command == 'A.B.C.D': # if it is an ip address
        ip = "10.10.10.10"
        return ip
        pass
    
    elif command == "<0-999999>.<0-999999>": # if it is an IOS version
        version = "99.99"
        return version
        pass
    
    elif re.match("<\d*-\d*>", command): # if it a numeric range
        x = int(command.split(" ")[-1].split('-')[0][1:]) # extract the lower bound the range
        y = int(command.split(" ")[-1].split('-')[1][:-1]) # extract the upper bound of the range
        random_number = str(random.randint(x,y)) # generate a random number within the range
        return random_number


# In[12]:


# def cleans_command_output(command):
#     command[87:].split('\n')[2:-4]


# In[13]:


device.enable()
counter_1 = 0
for no_layers in range(3):
    counter_1 += 1
    if counter_1 == 1:
        conf_terminal_cmd_layer_1 = []
        conf_terminal_cmd_layer_1 = device.send_config_set('?')[87:].split('\n')[2:-4] # start from inx 87, remove first line and the last 4 lines (hostname)
        conf_terminal_cmd_desc_layer_1 = [" ".join(i.split()).split(" ", 1) 
                                                     for i in conf_terminal_cmd_layer_1]
    else:
        exec(f"conf_terminal_cmd_desc_layer_{str(counter_1)} = []") # dyamically create a list name for the respective layer 
        for cmd_desc_1 in vars()["conf_terminal_cmd_desc_layer_"+str( counter_1-1 )]:
            counter_2 = 0
            if counter_1 == 2:
                help_cmd_output = device.send_config_set( cmd_desc_1[0]+" ?" "\x03" )[87:].split('\n')[1:-4]
                try:
                    conf_terminal_cmd_desc_layer_2.append([[cmd_desc_1[0] + " " + " ".join(j.split()).split(" ", counter_1-1)[0], 
                                                                  " ".join(j.split()).split(" ", 1)[1]] 
                                                                 for j in help_cmd_output if len(" ".join(j.split()).split(" ", counter_1-1)) > counter_1-1])
                except IndexError:
                    pass
            
            elif counter_1 == 3:
                one_conf_terminal_cmd_desc = []
                
                if len(cmd_desc_1) == 0: # if layer 2 command does not exist, append and empty list [] for the respective layer 3 index
                    one_conf_terminal_cmd_desc.append([])
                    vars()["conf_terminal_cmd_desc_layer_"+str(counter_1)].append([])
                else:
                    for k in cmd_desc_1:
                        counter_2 += 1
                        
                        if k[0].split(" ")[-1] == "A.B.C.D" or re.match("<\d*-\d*>", k[0].split(" ")[-1]):
                            try: # if it is a number range at the end of the command (e.g. <100-200>), convert it to an integer before adding ?
                                help_cmd_output = device.send_config_set(k[0].split()[:-1][0] + " " + genenrate_number_ip(k[0].split()[-1]) + " ?" "\x03")[87:].split('\n')[1:-4]
                                one_conf_terminal_cmd_desc.append([[k[0] + " " + " ".join(j.split()).split(" ", counter_1-1)[0], 
                                                                              " ".join(j.split()).split(" ", 1)[1]] 
                                                                             for j in help_cmd_output if len(" ".join(j.split()).split(" ", counter_1-1)) > counter_1-1])

        #                     except (ValueError, IndexError) as e:
                            except TypeError: # if not a range:
                                pass
                        else:
                            try:
                                help_cmd_output = device.send_config_set(k[0]+" ?" "\x03")[87:].split('\n')[1:-4]
                                one_conf_terminal_cmd_desc.append([[k[0] + " " + " ".join(j.split()).split(" ", counter_1-1)[0], 
                                                                          " ".join(j.split()).split(" ", 1)[1]] 
                                                                         for j in help_cmd_output if len(" ".join(j.split()).split(" ", counter_1-1)) > counter_1-1])


                            except IndexError:
                                pass
                        if counter_2 == len(cmd_desc_1):
                            vars()["conf_terminal_cmd_desc_layer_"+str(counter_1)].append(one_conf_terminal_cmd_desc)                     


# In[42]:


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
        return mydb
    except:
        print("Could not connect to {}".format(db_name)) 


# In[46]:


db = connect_mongodb_database('mongodb://ehsan:ehgh1363@10.128.0.2:27017/', 'commandsdatabase', 'confcommands')


# In[16]:


# Conver the list to dict to prepare for MongoDB

list_of_dicts_conf_terminal = []

for i, j in enumerate(conf_terminal_cmd_desc_layer_1):
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
                                for m, n in enumerate(conf_terminal_cmd_desc_layer_3[i][k]) if len(l) > 0
                                ]

                        }
                        for k, l in enumerate(conf_terminal_cmd_desc_layer_2[i]) if len(l) > 0
                    ]
                }
            }
        ]
        list_of_dicts_conf_terminal.append(cmd_dict)
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
                        for k, l in enumerate(conf_terminal_cmd_desc_layer_2[i]) if len(l) > 0
                    ]
                }
            }
        ]
        list_of_dicts_conf_terminal.append(cmd_dict)


# In[49]:


# Insert all commands:descriptions into MongoDB
for i in list_of_dicts_conf_terminal:
    db.confcommands.insert_one(i[0])


# In[ ]:




