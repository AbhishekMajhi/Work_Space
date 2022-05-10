from Users import get_user
# from UserDBUtils import*
import numpy as np
import pandas as pd

u1 = get_user()

db = pd.read_pickle("UserDB.pkl")

def create_db():
    cols = ["IDs", "name","age","Email","FaceID","Access"]
    db = pd.DataFrame(data = {}, columns=cols)
    return db
def insert(db):
    name = input("Enter your name: ")
    age = input("Enter your age: ")
    mail = input("Enter your mail address: ")
    # faceId = getFaceId()
    # access = getAccess()

    
    u1.setName(name)
    u1.setID()
    u1.setAge(age)
    u1.setEmail(mail)
    u1.setFaceID()
    u1.setAccess()
    # print(u1)

    db.loc[db.shape[0]] = [u1.getID(), u1.getName(), u1.getAge(),u1.getEmail(),u1.getFaceID(), u1.getAccess()]
    print("Data added!!")
    db.to_pickle("UserDB.pkl")


def register_user():
    insert(db)
    return u1
# def update_user(db, id):
#     try:
#         usr = db[db['IDs'] == id]
#     except:
#         print("This id does not exist!!")
    
#     print("What do you wanna update:")
#     print("1. Name 2. Age 3. Email 4. Access")
#     ch = input("Input here: ")
#     if ch == 1:
#         ip = input("Enter the new name: ")
#         usr['name'] = ip

        



u1 = register_user()
print(u1)
print("###########################################################")
print(db)
