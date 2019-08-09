#!/usr/bin/env python
# coding: utf-8

# In[264]:


from netmiko import ConnectHandler
import re
import numpy as np
# import nltk
import os
import string
import random
import re

# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity


# In[354]:


device = ConnectHandler(device_type="cisco_ios", ip="172.16.0.10", username="ehsan", password="ehgh1363", secret="ehgh1363")


# In[125]:


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


# In[352]:


# # identify a numeric range at the end of the command (e.g. <100-200>), convert it to an integer before adding ?
# def genenrate_number_ip(command):
#     if command == 'A.B.C.D': # if it is an ip address
#         ip = "10.10.10.10"
#         return ip
#         pass
    
#     elif command == "<0-999999>.<0-999999>": # if it is an IOS version
#         version = "99.99"
#         return version
#         pass
    
#     elif re.match("<\d*-\d*>", command): # if it a numeric range
#         x = int(command.split(" ")[-1].split('-')[0][1:]) # extract the lower bound the range
#         y = int(command.split(" ")[-1].split('-')[1][:-1]) # extract the upper bound of the range
#         random_number = str(random.randint(x,y)) # generate a random number within the range
#         return random_number


# In[355]:


# ## TEST

# device.enable()
# counter_1 = 0
# for no_layers in range(3):
#     counter_1 += 1
#     if counter_1 == 1:
#         conf_terminal_cmd_layer_1 = []
#         conf_terminal_cmd_layer_1 = device.send_config_set('?')[87:].split('\n')[2:-4] # start from inx 87, remove first line and the last 4 lines (hostname)
#         conf_terminal_cmd_desc_layer_1 = [" ".join(i.split()).split(" ", 1) 
#                                                      for i in conf_terminal_cmd_layer_1]
#     else:
#         exec(f"conf_terminal_cmd_desc_layer_{str(counter_1)} = []") # dyamically create a list name for the respective layer 
#         for cmd_desc_1 in vars()["conf_terminal_cmd_desc_layer_"+str( counter_1-1 )]:
#             counter_2 = 0
#             if counter_1 == 2:
#                 help_cmd_output = device.send_config_set( cmd_desc_1[0]+" ?" "\x03" )[87:].split('\n')[1:-4]
#                 try:
#                     conf_terminal_cmd_desc_layer_2.append([[cmd_desc_1[0] + " " + " ".join(j.split()).split(" ", counter_1-1)[0], 
#                                                                   " ".join(j.split()).split(" ", 1)[1]] 
#                                                                  for j in help_cmd_output if len(" ".join(j.split()).split(" ", counter_1-1)) > counter_1-1])
#                 except IndexError:
#                     pass
            
#             elif counter_1 == 3:
#                 one_conf_terminal_cmd_desc = []
                
#                 if len(cmd_desc_1) == 0: # if layer 2 command does not exist, append and empty list [] for the respective layer 3 index
#                     one_conf_terminal_cmd_desc.append([])
#                     vars()["conf_terminal_cmd_desc_layer_"+str(counter_1)].append([])
#                 else:
#                     for k in cmd_desc_1:
#                         counter_2 += 1
                        
#                         if k[0].split(" ")[-1] == "A.B.C.D" or re.match("<\d*-\d*>", k[0].split(" ")[-1]):
#                             try: # if it is a number range at the end of the command (e.g. <100-200>), convert it to an integer before adding ?
#     #                             print(k[0].split()[:-1][0] + " " + genenrate_number_ip(k[0].split()[-1]) + " ?")
#     #                             print(k[0])
#                                 help_cmd_output = device.send_config_set(k[0].split()[:-1][0] + " " + genenrate_number_ip(k[0].split()[-1]) + " ?" "\x03")[87:].split('\n')[1:-4]
#                                 one_conf_terminal_cmd_desc.append([[k[0] + " " + " ".join(j.split()).split(" ", counter_1-1)[0], 
#                                                                               " ".join(j.split()).split(" ", 1)[1]] 
#                                                                              for j in help_cmd_output if len(" ".join(j.split()).split(" ", counter_1-1)) > counter_1-1])

#         #                     except (ValueError, IndexError) as e:
#                             except TypeError: # if not a range:
#                                 pass
#                         else:
#                             try:
#                                 help_cmd_output = device.send_config_set(k[0]+" ?" "\x03")[87:].split('\n')[1:-4]
#                                 one_conf_terminal_cmd_desc.append([[k[0] + " " + " ".join(j.split()).split(" ", counter_1-1)[0], 
#                                                                           " ".join(j.split()).split(" ", 1)[1]] 
#                                                                          for j in help_cmd_output if len(" ".join(j.split()).split(" ", counter_1-1)) > counter_1-1])


#                             except IndexError:
#                                 pass
#                         if counter_2 == len(cmd_desc_1):
#                             vars()["conf_terminal_cmd_desc_layer_"+str(counter_1)].append(one_conf_terminal_cmd_desc)                     


# In[363]:


conf_terminal_cmd_desc_layer_1[:5]


# In[365]:


conf_terminal_cmd_desc_layer_2[:5]


# In[366]:


conf_terminal_cmd_desc_layer_3[:5]


# In[ ]:


# # Test 2

# device.enable()
# # device.send_config_set('?').split('\n')[4:-4]
# counter_1 = 0
# for no_layers in range(3):
#     counter_1 += 1
#     if counter_1 == 1:
#         conf_terminal_cmd_layer_1 = []
#         conf_terminal_cmd_layer_1 = device.send_config_set('?').split('\n')[4:-4][8:11] # remove first line and the last 2 lines (hostname)
#         conf_terminal_cmd_desc_layer_1 = [" ".join(i.split()).split(" ", 1) 
#                                                      for i in conf_terminal_cmd_layer_1]
#     else:
# #         device.enable()
#         exec(f"conf_terminal_cmd_desc_layer_{str(counter_1)} = []") # dyamically create a list name for the respective layer 
#         for cmd_desc_1 in vars()["conf_terminal_cmd_desc_layer_"+str( counter_1-1 )]:
#             counter_2 = 0
#             if counter_1 == 2:
#                 help_cmd_output = device.send_config_set( cmd_desc_1[0]+" ?" "\x03" )[87:].split('\n')[1:-4]
#                 try:
#                     vars()["conf_terminal_cmd_desc_layer_"+str( counter_1 )].append([[cmd_desc_1[0] + " " + " ".join(j.split()).split(" ", counter_1-1)[0], 
#                                                                   " ".join(j.split()).split(" ", 1)[1]] 
#                                                                  for j in help_cmd_output if len(" ".join(j.split()).split(" ", counter_1-1)) > counter_1-1])
                
#                 except IndexError:
#                     pass
                
#             elif counter_1 == 3:
#                 one_conf_terminal_cmd_desc = []
#                 for k in cmd_desc_1:            
#                     counter_2 += 1
#                     print(k[0])
#                     if k[0].split(" ")[-1] == "A.B.C.D" or re.match("<\d*-\d*>", k[0].split(" ")[-1]):
#                         try: # if it is a number range at the end of the command (e.g. <100-200>), convert it to an integer before adding ?
#     #                             print(k[0].split()[:-1][0] + " " + genenrate_number_ip(k[0].split()[-1]) + " ?")
#     #                             print(k[0])
#                             help_cmd_output = device.send_config_set(k[0].split()[:-1][0] + " " + genenrate_number_ip(k[0].split()[-1]) + " ?" "\x03")[87:].split('\n')[1:-4]
# #                             print(k[0].split()[:-1][0])
# #                             print(genenrate_number_ip(k[0].split()[-1]))
#                             print('1 {}'.format(help_cmd_output))
#                             one_conf_terminal_cmd_desc.append([[k[0] + " " + " ".join(j.split()).split(" ", counter_1-1)[0], 
#                                                                           " ".join(j.split()).split(" ", 1)[1]] 
# #                                                                and [k[0] + " " + " ".join(j.split()).split(" ", counter_1-1)[0], 
# #                                                                           " ".join(j.split()).split(" ", 1)[1]] is not None
# #                                                                else []
#                                                                for j in help_cmd_output
#                                                               if len(" ".join(j.split()).split(" ", counter_1-1)) > counter_1-1 ] and j[0].strip() != "<ctr>")
# #                             print('1 is {}'.format(one_conf_terminal_cmd_desc.append([[k[0] + " " + " ".join(j.split()).split(" ", counter_1-1)[0], 
# #                                                                           " ".join(j.split()).split(" ", 1)[1]] 
# #                                                                          for j in help_cmd_output if len(" ".join(j.split()).split(" ", counter_1-1)) > counter_1-1])))
# #                     except (ValueError, IndexError) as e:
#                         except TypeError: # if not a range:
#                             print('error 1 {}'.format(k[0]))
#                             pass
                    
#                     else:
#                         try:
#                             help_cmd_output = device.send_config_set(k[0]+" ?" "\x03")[87:].split('\n')[1:-4]
#                             print('2 {}'.format(help_cmd_output))
#                             one_conf_terminal_cmd_desc.append([[k[0] + " " + " ".join(j.split()).split(" ", counter_1-1)[0], 
#                                                                       " ".join(j.split()).split(" ", 1)[1]] 
#                                                                      for j in help_cmd_output if len(" ".join(j.split()).split(" ", counter_1-1)) > counter_1-1] and j.strip() != "<ctr>")

# #                             print('2 is {}'.format([[k[0] + " " + " ".join(j.split()).split(" ", counter_1-1)[0], 
# #                                                                       " ".join(j.split()).split(" ", 1)[1]] 
# #                                                                      for j in help_cmd_output if len(" ".join(j.split()).split(" ", counter_1-1)) > counter_1-1]))
#                         except IndexError:
#                             print('error 2 {}'.format(k[0]))
#                             pass
#                     if counter_2 == len(cmd_desc_1):
#                         vars()["conf_terminal_cmd_desc_layer_"+str(counter_1)].append(one_conf_terminal_cmd_desc)                     


# In[ ]:


# device.enable()
# for k in conf_terminal_cmd_desc_layer_2[3]:            
#         counter_2 += 1
# #                     try: # if it is a number range at the end of the command, convert it to an integer before adding ?
#         x = int(k[0].split(" ")[-1].split('-')[0][1:])
#         print(x)
#         y = int(k[0].split(" ")[-1].split('-')[1][:-1])
#         print(k[0].split()[:-1][0])
#         print(y)
#         z = str(1)
#         print(z)
#         help_cmd_output = device.send_config_set(k[0].split()[:-1][0] + " " + z + " ?" "\x03").split('\n')[3:]
#         one_conf_terminal_cmd_desc.append([[k[0] + " " + " ".join(j.split()).split(" ", counter_1-1)[0], 
#                                                       " ".join(j.split()).split(" ", 1)[1]] 
#                                                      for j in help_cmd_output if len(" ".join(j.split()).split(" ", counter_1-1)) > counter_1-1])


# In[83]:


# one_conf_terminal_cmd_desc = []
# device.enable()
# for k in conf_terminal_cmd_desc_layer_2[2][:5]:
# #     try:
#     x = int(k[0].split(" ")[-1].split('-')[0][1:])
#     y = int(k[0].split(" ")[-1].split('-')[1][:-1])
# #                         if type(x) == int and type(y) == int:
#     z = str(random.randint(x,y))
# #     print(k[0].split()[:-1])
#     help_cmd_output = device.send_config_set(k[0].split()[:-1][0] + " " + z + " ?" "\x03").split('\n')[3:]
#     one_conf_terminal_cmd_desc.append([[k[0] + " " + " ".join(j.split()).split(" ", counter_1-1)[0], 
#                                                               " ".join(j.split()).split(" ", 1)[1]] 
#                                                              for j in help_cmd_output if len(" ".join(j.split()).split(" ", counter_1-1)) > counter_1-1])
# #     except:
# #         print(k[0])


# In[ ]:


# ## store output of '?' command in xec mode (in  form of [command, command description]) into a list

# device.enable()
# counter_1 = 0
# for no_layers in range(3):
#     counter_1 += 1
#     if counter_1 == 1:
#         xec_cmd_layer_1 = []
#         xec_cmd_layer_1 = device.send_command("?").split('\n')[2:-2] # remove first line and the last 2 lines (hostname)
#         xec_cmd_desc_layer_1 = [" ".join(i.split()).split(" ", 1) 
#                                                      for i in xec_cmd_layer_1]
    
    
#     else:
#         exec(f"xec_cmd_desc_layer_{str(counter_1)} = []") # dyamically create a list name for the respective layer 
#         for cmd_desc_1 in vars()["xec_cmd_desc_layer_"+str(counter_1-1)]:
#             counter_2 = 0
#             if counter_1 == 2:
#                 help_cmd_output = device.send_command(cmd_desc_1[0]+" ?" "\x03").split('\n')
#                 try:
#                     vars()["xec_cmd_desc_layer_"+str(counter_1)].append([[cmd_desc_1[0] + " " + " ".join(j.split()).split(" ", counter_1-1)[0], 
#                                                                   " ".join(j.split()).split(" ", 1)[1]] 
#                                                                  for j in help_cmd_output if len(" ".join(j.split()).split(" ", counter_1-1)) > counter_1-1])
#                 except IndexError:
#                     pass
            
#             elif counter_1 == 3:
#                 one_xec_cmd_desc = []
#                 for k in cmd_desc_1:            
#                     counter_2 += 1
#                     help_cmd_output = device.send_command(k[0]+" ?" "\x03").split('\n')
#                     try:
#                         one_xec_cmd_desc.append([[k[0] + " " + " ".join(j.split()).split(" ", counter_1-1)[0], 
#                                                                   " ".join(j.split()).split(" ", 1)[1]] 
#                                                                  for j in help_cmd_output if len(" ".join(j.split()).split(" ", counter_1-1)) > counter_1-1])
                    

#                     except IndexError:
#                         pass
#                     if counter_2 == len(cmd_desc_1):
#                         vars()["xec_cmd_desc_layer_"+str(counter_1)].append(one_xec_cmd_desc)                     


# In[356]:


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


# In[ ]:


connect_mongodb_database('mongodb://ehsan:ehgh1363@10.128.0.2:27017/', 'commandsdatabase', 'xeccommands')


# In[15]:


# for i,j in enumerate(xec_cmd_desc_layer_1):
#     print("layer 1 {} and {}".format(i,j))
#     for k, h in enumerate(xec_cmd_desc_layer_2[i]):
#         print("layer 2 {}".format(h))
#         print("layer 3 {}".format([t for t in xec_cmd_desc_layer_3[i][k]]))


# In[24]:


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


# In[30]:


# Insert all commands:descriptions into MongoDB
for i in list_of_dicts:
    mydb.xeccommands.insert_one(i[0])


# In[357]:


# # Conver the list to dict to prepare for MongoDB

# list_of_dicts_conf_terminal = []
# # cmd_dict = {}

# for i, j in enumerate(conf_terminal_cmd_desc_layer_1):
#     try:
#         cmd_dict = [
#             {
#                 "cmd":
#                 {
#                     "name": j[0],
#                     "desc": j[1],
#                     "c1": 
#                     [
#                         {
#                             "_id": str(k+1), 
#                             "name": l[0], 
#                             "desc": l[1],
#                             "c2": 
#                                 [
#                                     {
#                                     "_id": str(m+1), 
#                                     "n": n[0], 
#                                     "d": n[1]
#                                     }
#                                 for m, n in enumerate(conf_terminal_cmd_desc_layer_3[i][k]) if len(l) > 0
#                                 ]

#                         }
#                         for k, l in enumerate(conf_terminal_cmd_desc_layer_2[i]) if len(l) > 0
#                     ]
#                 }
#             }
#         ]
#     #     cmd_dict = {j[0].replace('.', ''):j[1] for j in i}
#         list_of_dicts_conf_terminal.append(cmd_dict)
#     except IndexError:
#         cmd_dict = [
#             {
#                 "cmd":
#                 {
#                     "name": j[0],
#                     "desc": j[1],
#                     "c1": 
#                     [
#                         {
#                             "_id": str(k+1), 
#                             "name": l[0], 
#                             "desc": l[1],

#                         }
#                         for k, l in enumerate(conf_terminal_cmd_desc_layer_2[i]) if len(l) > 0
#                     ]
#                 }
#             }
#         ]
#         list_of_dicts_conf_terminal.append(cmd_dict)


# In[358]:


# # Insert all commands:descriptions into MongoDB
# for i in list_of_dicts_conf_terminal:
#     mydb.confcommands.insert_one(i[0])


# In[ ]:


# a=[{
# "_id": 'ObjectId1',
# "command": {
# 			"name": "command name",
# 			"desc": "command desc",
# 			"sub_command_one": 
# 				[{
# 				"ID": "id1",
# 				"name": "sub command one name",
# 				"desc": "sub command one desc",
# 				"sub_command_two": 
# 					[{
# 					"ID": "id1",
# 					"name": "sub command one name",
# 					"desc": "sub command one desc",
# 					},
# 					{
# 					"ID": "id2",
# 					"name": "sub command one name",
# 					"desc": "sub command one desc"
# 					}]
# 				},		
# 				{
# 				"ID": "id2",
# 				"name": "sub command 1 name",
# 				"desc": "sub command 1 desc",
# 				"sub_command_two": 
# 					{
# 					"ID": "id1",
# 					"name": "sub command 2 name",
# 					"desc": "sub command 2 desc",
# 					"sub_command_three":
# 						{
# 						"ID":"id1",
# 						"name": "sub command 3",
# 						"desc": "sub command 3 desc",
# 						}
# 					}
# 				}]
			
# 			}},
# {"_id": "ObjectId2",
# "command": {
# 			"name": "command name",
# 			"desc": "command desc",
# 			"sub_command_one": "222"
# }}]


# In[5]:


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


# In[17]:


# def automate():
# #     f=open('/home/ehsan_ghoreishi/gns3/yoda/modules/chatbot.txt','r',errors = 'ignore')
# #     raw = desc
# #     raw=f.read()
# #     raw=raw.lower()# converts to lowercase
#     try:
#         nltk.data.find('tokenizers/punkt')
#     except LookupError:
#         nltk.download('punkt')
#     try:
#         nltk.data.find(os.path.join("corpora", 'wordnet'))
#     except LookupError:
#         nltk.download('wordnet') # first-time use only
# #     sent_tokens = nltk.sent_tokenize(raw)# converts to list of sentences 
# #     word_tokens = nltk.word_tokenize(raw)# converts to list of words
#     word_tokens = desc_word
#     sent_tokens = desc_sent

#     lemmer = nltk.stem.WordNetLemmatizer()
#     def LemTokens(tokens):
#         return [lemmer.lemmatize(token) for token in tokens]
#     remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
#     def LemNormalize(text):
#         return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))


#     # Generating response
#     def response(user_response):
#         robo_response=''
#         sent_tokens.append(user_response)
#         TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
#         tfidf = TfidfVec.fit_transform(sent_tokens)
#         vals = cosine_similarity(tfidf[-1], tfidf)
#         idx=vals.argsort()[0][-2]
#         flat = vals.flatten()
#         flat.sort()
#         req_tfidf = flat[-2]
#         if(req_tfidf==0):
#             robo_response=robo_response+"I am sorry! I don't understand you"
#             return robo_response
#         else:
#             robo_response = robo_response+sent_tokens[idx]
#             return robo_response


#     flag=True
#     print("Yoda: My name is Robo. I will answer your queries about Chatbots. If you want to exit, type Bye!")

#     while(flag==True):
#         user_response = input()
#         user_response=user_response.lower()
#         if(user_response!='bye'):
#             if(user_response=='thanks' or user_response=='thank you' ):
#                 flag=False
#                 print("Yoda: You are welcome..")
#         #    else:
#          #       if(greeting(user_response)!=None):
#           #          print("ROBO: "+greeting(user_response))
#             else:
#                 print("Yoda: ",end="")
#                 print(response(user_response))
#                 sent_tokens.remove(user_response)
#         else:
#             flag=False
#             print("Yoda: Bye! take care..")


# In[ ]:




