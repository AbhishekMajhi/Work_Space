from os import name
from DataBase import  load_db
from tts import speak


def get_permission():
    speak("Please enter the admin password:")
    pas = input("")
    print("pas:", pas)
    cur.execute("SELECT password FROM users WHERE role = 'admin'")
    r_pas = cur.fetchone()
    r_pas = r_pas[0]
    if pas == r_pas:
        # speak("Permission Granted!!")
        return True
    else:
        # speak("sorry,Permission Denied!!!")
        return False

def check_admin():
    # role = "SELECT role form users whrer f_name = u_name(%s)"
	# cur.executemany(role, u_name)
    cur.execute("SELECT f_name FROM users WHERE role= 'admin'")
    ad_name = cur.fetchone()

    if ad_name == None:
        speak("It seems there are no admin account created yet!")
        return False
    else:
        speak("Admin account found!")
        return True

db,cur = load_db()

if __name__ == "__main__":
    user = "UltimateDude"
    print(get_permission())
    # if check_admin():
    #     print("Yes there is a admin so you need his permission")
    