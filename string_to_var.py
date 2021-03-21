import sys
import random
import string
import pprint
import json

pp = pprint.PrettyPrinter(indent=4)
colors = ["#75DBFF", "#50FF56", "#FF8D75", "#FF50AD", "#FF9B47"]

class DummyUser:
	def __init__(self, _id, name = None, is_host = False):
		self.name = name if name != None else "John " + ''.join(random.choice(string.ascii_uppercase) for i in range(10))
		self.id = _id
		self.position = "1.1"
		self.color = random.choice(colors)
		self.last_alive = 0

		self.is_host = is_host
		self.is_idle = False
		self.cursor_colored = True
	
	def __str__(self):
		return str({
            "name": self.name,
            "id": self.id,
            "position": self.position,
            "color" : self.color,
            "is_host": self.is_host
        })
class DummyDia:
	def update_host(self, _id):
		return

class X:
	def __init__(self, is_host = False):
		self.user_id = 0
		self._users = {i : DummyUser(i) for i in range(1, 10)}
		self._users[0] = DummyUser(0, "Me", is_host)
		self.username = "John Doe"
		self.is_host = is_host
		self.dialog = DummyDia()
		if self.is_host == False:
			self._users[random.randint(1, 9)].is_host = True

	def get_connection_info(self):
		return {"name" : self.username,
				"broker" : "test_broker",
				"topic" : "test_topic"}
	
	def get_driver(self):
		if self.is_host:
			return 0, "You"
		
		else:
			for i in self._users:
				if self._users[i].is_host == True:
					return i, self._users[i].name
		
		return -1, "null"
	
	def get_users(self):
		return self._users

	def change_host(self, user_id = None):
		if user_id == self.user_id:
			self.be_host()
		elif self.is_host:
			self.be_copilot(user_id)
		elif user_id != None:
			self.other_host(user_id)
		else:
			print("Err: ", user_id, "is not a valid input")

	def be_host(self):
		_id, _ = self.get_driver()

		self.enable_editing()

		self._users[_id].is_host = False 
		self.is_host = self._users[self.user_id].is_host = True

		self.dialog.update_host(self.user_id)

	def be_copilot(self, new_host_id = None):
		self.disable_editing()

		if new_host_id != None:
			self._users[new_host_id].is_host = True 
		self.is_host = self._users[self.user_id].is_host = False

		self.dialog.update_host(new_host_id)

	def other_host(self, new_host_id):
		_id, _ = self.get_driver()

		if _id == new_host_id:
			return
		
		self._users[_id].is_host = False 
		self._users[new_host_id].is_host = True

		self.dialog.update_host(new_host_id)

class UserEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, DummyUser):
            return{
                    "name": o.name,
                    "id": o.id,
                    "position": o.position,
                    "color" : o.color,
                    "is_host": o.is_host
                }
            
        else:
            return super().default(o)

tVal = X(len(sys.argv) > 1 and sys.argv[1] == "host")

while True:
	x = input("Input_id: ")
	if x == "end":
		break
	if x[-1] == "_":
		_id = x.split("_")[0]
		_id = int(_id); flag = True
	else:
		_id = int(x)
		flag = False

	print("Host before change...", end = " ")
	_, usr = tVal.get_driver()
	pp.pprint(usr)
	tVal.change_host(_id)
	print("Host after change...", end = " ")
	if flag:
		pp.pprint(json.dumps(tVal._users, cls = UserEncoder))
	else:
		_, usr = tVal.get_driver()
		pp.pprint(usr)