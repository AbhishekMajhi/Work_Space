# main table format....
'''
 f_name | age | sex | role | face | password
--------+-----+-----+------+------+---------+------
'''


import psycopg2

# checked!
def load_db(load = True):
	print("connecting to Database...")
	db = psycopg2.connect(database = "galvin", user = 'alice', password = 'dude',host='127.0.0.1')
	print('connected into database...')
	#Setting auto commit false
	db.autocommit = True
	# create cursor object
	cur = db.cursor()

	return db, cur

# checked!
def insert_user(data,db,cur): # here data is a list containing all the data needed to create a user
	ins_st = "INSERT INTO users (f_name, age, sex, role, password, face) VALUES(%s, %s, %s, %s, %s, %s)"
	cur.executemany(ins_st,data)
	# commit changes
	db.commit()
	print("user registred!!")

# Checked!
def fetch_all_users(cur):
	cur.execute('''SELECT * FROM users''')
	records = cur.fetchall()

	return records

# Checked!
def fetch_user(data,cur): # here data may be face vec or password
	if '[' in data: # means its a fave vec
		cur.execute('''SELECT * FROM users WHERE face = %s''',(data,))
		record = cur.fetchone()  # record contains the info about that user and its a tuple
		return record
	else:  # its a password
		cur.execute('''SELECT * FROM users WHERE password = %s''',(data,))
		record = cur.fetchone()  # record contains the info about that user and its a tuple
		return record
def get_face_encodings(cur):
	db = {}
	cur.execute('''SELECT f_name,face FROM users''')
	record = cur.fetchall()
	record = dict(record)
	print(type(record))
	return record

# Checked!
def delete_account(user, cur):  # delete current user account
	cur.execute("DELETE FROM users WHERE f_name = %s",(user,))
	print("Your account has been deleted")




############ Test area ###########
if __name__ == "__main__":
	db, cur = load_db(load = True)
	data = [('Ultimateddude', 21, 'm', 'user','154516151','[10,0,8,79,75608,90720,9]')]
	# insert_user(data, db, cur)
	
	delete_account("UltimateDude", cur)
	# usr = "Shadow"
	# # print(type(data))
	# delete_account(usr,cur)
	# get_face_encodings(cur)
	# records = get_face_encodings(cur)
	# for name,face in records.items():
	# 	print(name, face)
	# db.close()




