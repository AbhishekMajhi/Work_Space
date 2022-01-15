## Imports
from transformers import AutoTokenizer,AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd 

## Load Sentence Transformer Model
def load_sentence_model():
    checkpoint = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    tokenizer = AutoTokenizer.from_pretrained(checkpoint)
    model = AutoModel.from_pretrained(checkpoint)
    return model, tokenizer

#Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


## Read Command Embeddings
cols = ["sentences","labels",'encodings']
data = pd.read_pickle("commands_V2.pkl")

## Method to return Command Embeddinds
def get_encoding(sentence):
  encoded_input = tokenizer(sentence, padding=True, truncation=True, return_tensors='pt')
  # Compute token embeddings
  with torch.no_grad():
      model_output = model(**encoded_input)
  # Return encoding
  encoding_output =  mean_pooling(model_output, encoded_input['attention_mask'])
  encoding_output = encoding_output.reshape(1, -1)
  return encoding_output

## Get the similarity score
def similarity_score(sentence):
  encoded_output = get_encoding(sentence)
  scores = []
  for i in range(len(data)):
    score = cosine_similarity(data["encodings"][i], encoded_output)
    scores.append(score)
    command_idx = np.argmax(scores)
    label = data["labels"][command_idx]
  return command_idx,label  # Returning command index in dataset and label for that input command


## Testing
if __name__ == "__main__":
    model, tokenizer = load_sentence_model()
    while(1):
        ip = input("Enter a command sir:: ")
        if ip == "done":
            break
        else:
            print(similarity_score(ip))
    exit(1)


# Comment this part while testing
# Production
if __name__ != "__main__":
    model, tokenizer = load_sentence_model()


######## Working like a charm 😱😱😱😱😱😱😱  ##########