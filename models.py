from database import users_collection

class User:
    def __init__(self, email, password, confirm_password):
        self.email = email
        self.password = password
        self.confirm_password = confirm_password

    def save_to_db(self):
        user = {"email": self.email, "password": self.password}
        users_collection.insert_one(user)