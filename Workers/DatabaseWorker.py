import sqlite3

class DatabaseWorker:
    def __init__(self):
        self.db = sqlite3.connect('DB_name.db')
        self.cursor = self.db.cursor()

    def addUser(self, user: dict):
        query = "INSERT INTO vk_users (id"
        values = [user['id']]
        if 'mobile_phone' in user.keys():
            query += ', mobile'
            values.append(user['mobile_phone'])
        if 'home_phone' in user.keys():
            query += ', home'
            values.append(user['home_phone'])

        query += ") VALUES("
        for el in values:
            query += "'" + str(el) + "',"
        query = query[:-1] + ')'

        self.cursor.execute(query)
        self.db.commit()

    def getAllUsers(self):
        self.cursor.execute("SELECT * FROM vk_users")
        return self.cursor.fetchall()

    def makeLink(self, id: str):
        return "https://vk.com/id" + id

    def addPhone(self, id: str, phone: str):
        print("New Telegam with phone: " + phone)
        self.cursor.execute("INSERT INTO phones (phone, link) "
                            "VALUES('" + phone + "', '" + self.makeLink(id) + "')")
        self.db.commit()

    def delteAllUsers(self):
        self.cursor.execute('DELETE FROM vk_users')
        self.db.commit()

