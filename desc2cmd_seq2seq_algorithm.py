#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pymongo
import numpy as np

import tensorflow as tf
import pickle
from tensorflow.keras import layers , activations , models , preprocessing, utils
import pandas as pd

from gensim.models.keyedvectors import KeyedVectors


try:
    myclient = pymongo.MongoClient("") # MongoDB instance running on GC
    print("Connected successfully!!!") 
except:   
    print("Could not connect to MongoDB") 

try:
    mydb = myclient["commandsdatabase"]
    print("Connected to DB") 
except:
    print("Could not connect to DB")   


# import MongoDB xeccommands collection into command and description lists

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
        

# import MongoDB confcommands collection into command and description lists

for i in mydb.confcommands.find({}):
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


# load word2vec word vectors

# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
# print("loading word2vec model…")
word2vec_model = KeyedVectors.load_word2vec_format("./data/GoogleNews-vectors-negative300.bin", binary=True)
def getVector(str):
    if str in word2vec_model:
        return word2vec_model[str]
    else:
        return None;


tokenizer = preprocessing.text.Tokenizer()
tokenizer.fit_on_texts( desc_list ) 
tokenized_desc_lines = tokenizer.texts_to_sequences( desc_list ) 

length_list = list()
for token_seq in tokenized_desc_lines:
    length_list.append( len( token_seq ))
max_input_length = np.array( length_list ).max()
print( 'Descriptions max length is {}'.format( max_input_length ))

padded_desc_lines = preprocessing.sequence.pad_sequences( tokenized_desc_lines , maxlen=max_input_length , padding='post' )
encoder_input_data = np.array( padded_desc_lines )
print( 'Encoder input data shape -> {}'.format( encoder_input_data.shape ))

desc_dict = tokenizer.word_index
num_desc_tokens = len( desc_dict )+1
print( 'Number of Description tokens = {}'.format( num_desc_tokens))

# create a weight matrix for words in training docs (load word2vec word vectors)
encoder_embedding_matrix = np.zeros((num_desc_tokens, 300))
for word, i in tokenizer.word_index.items():
    embedding_vector = getVector(word)
    if embedding_vector is not None:
        encoder_embedding_matrix[i] = embedding_vector
print("Encoder embedding shape {}".format( encoder_embedding_matrix.shape ))


commands = list()
for cmd in cmd_list:
    commands.append( '<START> ' + cmd + ' <END>' )  

tokenizer = preprocessing.text.Tokenizer()
tokenizer.fit_on_texts( commands ) 
tokenized_cmd_lines = tokenizer.texts_to_sequences( commands ) 

length_list = list()
for token_seq in tokenized_cmd_lines:
    length_list.append( len( token_seq ))
max_output_length = np.array( length_list ).max()
print( 'Command max length is {}'.format( max_output_length ))

padded_cmd_lines = preprocessing.sequence.pad_sequences( tokenized_cmd_lines , maxlen=max_output_length, padding='post' )
decoder_input_data = np.array( padded_cmd_lines )
print( 'Decoder input data shape -> {}'.format( decoder_input_data.shape ))

cmd_dict = tokenizer.word_index
num_cmd_tokens = len( cmd_dict )+1
print( 'Number of Command tokens = {}'.format( num_cmd_tokens))

# create a weight matrix for words in training docs (load word2vec word vectors)
decoder_embedding_matrix = np.zeros((num_cmd_tokens, 300))
for word, i in tokenizer.word_index.items():
    embedding_vector = getVector(word)
    if embedding_vector is not None:
        decoder_embedding_matrix[i] = embedding_vector
print("Dencoder embedding shape {}".format( decoder_embedding_matrix.shape ))


decoder_target_data = list()
for token_seq in tokenized_cmd_lines:
    decoder_target_data.append( token_seq[ 1 : ] ) 
    
padded_cmd_lines = preprocessing.sequence.pad_sequences( decoder_target_data , maxlen=max_output_length, padding='post' )
onehot_cmd_lines = utils.to_categorical( padded_cmd_lines , num_cmd_tokens )
decoder_target_data = np.array( onehot_cmd_lines )
print( 'Decoder target data shape -> {}'.format( decoder_target_data.shape ))


encoder_inputs = tf.keras.layers.Input(shape=( None , ))
encoder_embedding = tf.keras.layers.Embedding( num_desc_tokens, 300 , weights=[encoder_embedding_matrix] )(encoder_inputs)
encoder_outputs , state_h , state_c = tf.keras.layers.LSTM( 300 , return_state=True )( encoder_embedding )
encoder_states = [ state_h , state_c ]

decoder_inputs = tf.keras.layers.Input(shape=( None ,  ))
decoder_embedding = tf.keras.layers.Embedding( num_cmd_tokens, 300 , weights=[decoder_embedding_matrix] )(decoder_inputs)
decoder_lstm = tf.keras.layers.LSTM( 300 , return_state=True , return_sequences=True, recurrent_dropout=0.2)
decoder_outputs , _ , _ = decoder_lstm( decoder_embedding , initial_state=encoder_states )
decoder_dense = tf.keras.layers.Dense( num_cmd_tokens , activation=tf.keras.activations.softmax ) 
output = decoder_dense ( decoder_outputs )

model = tf.keras.models.Model([encoder_inputs, decoder_inputs], output )
model.compile(optimizer=tf.keras.optimizers.Adam(), loss='categorical_crossentropy')

model.summary()


# In[ ]:


model.fit([encoder_input_data , decoder_input_data], decoder_target_data, batch_size=50, epochs=15 ) 
model.save( 'model.h5' ) 


def make_inference_models():
    
    encoder_model = tf.keras.models.Model(encoder_inputs, encoder_states)
    
    decoder_state_input_h = tf.keras.layers.Input(shape=( 300,))
    decoder_state_input_c = tf.keras.layers.Input(shape=( 300 ,))
    
    decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]
    
    decoder_outputs, state_h, state_c = decoder_lstm(
        decoder_embedding , initial_state=decoder_states_inputs)
    decoder_states = [state_h, state_c]
    decoder_outputs = decoder_dense(decoder_outputs)
    decoder_model = tf.keras.models.Model(
        [decoder_inputs] + decoder_states_inputs,
        [decoder_outputs] + decoder_states)
    
    return encoder_model , decoder_model


def str_to_tokens( sentence : str ):
    words = sentence.lower().split()
    tokens_list = list()
    for word in words:
        tokens_list.append( desc_dict[ word ] ) 
    return preprocessing.sequence.pad_sequences( [tokens_list] , maxlen=max_input_length , padding='post')


enc_model , dec_model = make_inference_models()

enc_model.save( 'enc_model.h5' ) 
dec_model.save( 'dec_model.h5' ) 
model.save( 'model.h5' ) 

for epoch in range( encoder_input_data.shape[0] ):
    states_values = enc_model.predict( str_to_tokens( input( 'Enter eng sentence : ' ) ) )
    #states_values = enc_model.predict( encoder_input_data[ epoch ] )
    empty_target_seq = np.zeros( ( 1 , 1 ) )
    empty_target_seq[0, 0] = cmd_dict['start']
    stop_condition = False
    decoded_translation = ''
    while not stop_condition :
        dec_outputs , h , c = dec_model.predict([ empty_target_seq ] + states_values )
        sampled_word_index = np.argmax( dec_outputs[0, -1, :] )
        sampled_word = None
        for word , index in cmd_dict.items() :
            if sampled_word_index == index :
                decoded_translation += ' {}'.format( word )
                sampled_word = word
        
        if sampled_word == 'end' or len(decoded_translation.split()) > max_output_length:
            stop_condition = True
            
        empty_target_seq = np.zeros( ( 1 , 1 ) )  
        empty_target_seq[ 0 , 0 ] = sampled_word_index
        states_values = [ h , c ] 

    print( decoded_translation )


converter = tf.lite.TFLiteConverter.from_keras_model_file( 'model.h5' )
converter.allow_custom_ops=True
buffer = converter.convert()
open( 'model.tflite' , 'wb' ).write( buffer )


