from tensorflow.keras.models import load_model
import nltk
import numpy as np



def read_glove_vecs(glove_file):
    with open(glove_file, 'r',encoding='utf-8') as f:
        words = set()
        word_to_vec_map = {}
        for line in f:
            line = line.strip().split()
            curr_word = line[0]
            words.add(curr_word)
            word_to_vec_map[curr_word] = np.array(line[1:], dtype=np.float64)

        i = 1
        words_to_index = {}
        index_to_words = {}
        for w in sorted(words):
            words_to_index[w] = i
            index_to_words[i] = w
            i = i + 1
    return words_to_index, index_to_words, word_to_vec_map


def load_requirments():
    print('loading please wait....')

    word_to_index, index_to_word, word_to_vec_map = read_glove_vecs('glove.6B.200d.txt')
    ultimate_galvin_model = load_model('Ultimate_Dude_Model.h5')

    print('done!!')
    return word_to_index, index_to_word, word_to_vec_map,ultimate_galvin_model

def sentences_to_indices(X, word_to_index, max_len):
    """
    Converts an array of sentences (strings) into an array of indices corresponding to words in the sentences.
    The output shape should be such that it can be given to `Embedding()` (described in Figure 4).

    Arguments:
    X -- array of sentences (strings), of shape (m, 1)
    word_to_index -- a dictionary containing the each word mapped to its index
    max_len -- maximum number of words in a sentence. You can assume every sentence in X is no longer than this.

    Returns:
    X_indices -- array of indices corresponding to words in the sentences from X, of shape (m, max_len)
    """

    m = X.shape[0]                                   # number of training examples
    tokenizer = nltk.tokenize.TreebankWordTokenizer()
    ### START CODE HERE ###
    # Initialize X_indices as a numpy matrix of zeros and the correct shape (≈ 1 line)
    X_indices = np.zeros((m,max_len))
    #print(X1_indices)
    for i in range(m):                               # loop over training examples

        # Convert the ith training sentence in lower case and split is into words. You should get a list of words.
        sentence_words =tokenizer.tokenize(X[i])

        # Initialize j to 0
        j = 0

        # Loop over the words of sentence_words
        for w in sentence_words:
            # Set the (i,j)th entry of X_indices to the index of the correct word.
            try:
                X_indices[i, j] = word_to_index[w]
            except:
                continue
            # Increment j to j + 1
            j = j + 1
    return X_indices

def identify(command,word_to_index,ultimate_galvin_model):

    maxLen = 11
    test_sen = np.array([command])
    sen_idx = sentences_to_indices(test_sen,word_to_index,maxLen)
    cmd_label = np.argmax(ultimate_galvin_model.predict(sen_idx))

    return cmd_label

def free_res(word_to_index, index_to_word, word_to_vec_map):
    del word_to_index
    del word_to_vec_map
    del index_to_word


word_to_index, index_to_word, word_to_vec_map,ultimate_galvin_model = load_requirments()
voice_data = 'how will be the cloud'
label = identify(voice_data,word_to_index,ultimate_galvin_model)
print("label:",label)


