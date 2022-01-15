import numpy as np

# who_is_it fun
def who_is_it(image_path, database, model,img_to_encoding):
    """
    Arguments:
    image_path -- path to an image
    database -- database containing image encodings along with the name of the person on the image
    model -- your Inception model instance in Keras
    
    Returns:
    min_dist -- the minimum distance between image_path encoding and the encodings from the database
    identity -- string, the name prediction for the person on image_path
    """
    
    #Compute the target "encoding" for the image, by using img_to_encoding()
    encoding = img_to_encoding(image_path,model)
    
    ## Now find the closest encoding 
    
    # Initializing "min_dist" to a large value, say 100
    # min_dist = 100
    data = {
        'min_dist':100,
        'identity':None
    }
    # Loop over the database dictionary's names and encodings.
    for (name, db_enc) in database.items():
        
        # Compute L2 distance between the target "encoding" and the current db_enc from the database.
        dist = np.linalg.norm(encoding-db_enc)

        # If this distance is less than the min_dist, then set min_dist to dist, and identity to name.
        if dist<data["min_dist"]:
            data["min_dist"] = dist
            data["identity"] = name
    
    if data["min_dist"] > 0.7:
        print("Not in the database.")
    else:
        print ("it's " + str(data["identity"]) + ", the distance is " + str(data["min_dist"]))
        
    return data

# def create_db(model,img_to_encoding):
#     database = {}
#     database["danielle"] = img_to_encoding("images/danielle.png", model)
#     database["younes"] = img_to_encoding("images/younes.jpg", model)
#     database["tian"] = img_to_encoding("images/tian.jpg", model)
#     database["andrew"] = img_to_encoding("images/andrew.jpg", model)
#     database["kian"] = img_to_encoding("images/kian.jpg", model)
#     database["dan"] = img_to_encoding("images/dan.jpg", model)
#     database["sebastiano"] = img_to_encoding("images/sebastiano.jpg", model)
#     database["bertrand"] = img_to_encoding("images/bertrand.jpg", model)
#     database["kevin"] = img_to_encoding("images/kevin.jpg", model)
#     database["felix"] = img_to_encoding("images/felix.jpg", model)
#     database["benoit"] = img_to_encoding("images/benoit.jpg", model)
#     database["arnaud"] = img_to_encoding("images/arnaud.jpg", model)
#     #database["abhishek"] = img_to_encoding("/images/abhishek.jpg", FRmodel)
#     return database

def get_img_encoding(name, img, model,img_to_encoding):
    database = {}
    database[name] = img_to_encoding(img,model)
    return database[name]