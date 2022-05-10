from UserDBUtils import*
class Users:

    #Name
    def setName(self, name):
        self.name = name
    
    def getName(self):
        return self.name

    # ID
    def setID(self):
        self.id = assignID()

    def getID(self):
        return self.id
    
    # Age
    def setAge(self, age):
        self.age = age
    
    def getAge(self):
        return self.age
    
    # Email
    def setEmail(self, mail):
        self.email = mail
    
    def getEmail(self):
        return self.email

    # Access
    def setAccess(self):
        self.access = getAccess()
    
    def getAccess(self):
        return self.access

    # FaceID
    def setFaceID(self):
        self.faceid = getFaceId()
    
    def getFaceID(self):
        return self.faceid

    def __repr__(self): 
        return "User contents ID: %s \t name: %s \t Email:%s \t age: %s \t faceid: %s \t access: %s " % (self.id, self.name,self.email, self.age, self.faceid, self.access)

def get_user():
    user = Users()
    return user

if __name__ == "__main__":
    name = input("Enter your name: ")
    age = input("Enter your age: ")
    id = assignID()
    faceId = getFaceId()
    access = getAccess()

    u1 = Users()
    u1.setName(name)
    u1.setAge(age)
    u1.setAccess()
    u1.setID()
    u1.setFaceID()

    print(u1)