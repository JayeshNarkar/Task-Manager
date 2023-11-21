from tabulate import tabulate
import sys
import sqlite3
import os

users=[]
classes={}
current_user=""

class task_manager:
    def __init__(self,name,password):
        self.name=name
        self.password=password
        self.tasks=[] #task should look like [{"task":Task,"priority":Priority,"due_date":Date},{}]
        self.completed_tasks=0
        self.pending_tasks=0
        db_file_name = f"{name}.db"
        if os.path.exists(db_file_name):
            user_file = sqlite3.connect(db_file_name)
            c = user_file.cursor()
            c.execute("SELECT task, priority, due_date FROM tasks")
            rows = c.fetchall()
            for row in rows:
                task = {"task": row[0], "priority": row[1], "due_date": row[2]}
                self.tasks.append(task)
            user_file.close()
        else:
            user_file = sqlite3.connect(db_file_name)
            c = user_file.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS tasks
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT, priority TEXT, due_date DATE)''')
            user_file.commit()
            user_file.close()

    def __str__(self):
        db_file_name = f"{self.name}.db"
        user_file = sqlite3.connect(db_file_name)
        c = user_file.cursor()
        c.execute("SELECT id, task, priority, due_date FROM tasks")
        rows = c.fetchall()
        user_file.close()
        tasks = []
        for row in rows:
            self.pending_tasks=self.pending_tasks+1
            tasks.append({"ID": row[0], "Task": row[1], "Priority": row[2], "Due Date": row[3]})
        tasks.sort(key=lambda x: {'high': 1, 'medium': 2, 'low': 3}[x['Priority']])
        return tabulate(tasks, headers="keys", tablefmt="heavy_grid")

    def add_task(self,task):
        self.tasks.append(task)
        db_file_name = f"{self.name}.db"
        user_file = sqlite3.connect(db_file_name)
        c = user_file.cursor()
        c.execute("INSERT INTO tasks (task, priority, due_date) VALUES (?, ?, ?)",
                  (task['task'], task['priority'], task['due_date']))
        user_file.commit()
        user_file.close()

    def remove_task(self,task_name):
        self.tasks = [task for task in self.tasks if task['task'] != task_name]
        db_file_name = f"{self.name}.db"
        user_file = sqlite3.connect(db_file_name)
        c = user_file.cursor()
        c.execute("DELETE FROM tasks WHERE task=?", (task_name,))
        user_file.commit()
        user_file.close()

    def reschedule_task(self, task_name, new_due_date):
        for task in self.tasks:
            if task['task'] == task_name:
                task['due_date'] = new_due_date
                db_file_name = f"{self.name}.db"
                user_file = sqlite3.connect(db_file_name)
                c = user_file.cursor()
                c.execute("UPDATE tasks SET due_date=? WHERE task=?",
                          (new_due_date, task_name))
                user_file.commit()
                user_file.close()
                break
            else:
                print("Task does not exist")
                return

    def mark_as_done(self,task):
        global classes
        global current_user
        self.pending_tasks=self.pending_tasks-1
        self.completed_tasks=self.completed_tasks+1
        classes[current_user].remove_task(task)

    @property
    def stats(self):
        db_file_name = f"{self.name}.db"
        user_file = sqlite3.connect(db_file_name)
        c = user_file.cursor()
        c.execute("SELECT COUNT(*) FROM tasks")
        pending_tasks = c.fetchone()[0]
        user_file.close()
        self.pending_tasks = pending_tasks
        table = [["Category", "Count"],
                 ["Tasks Completed", self.completed_tasks],
                 ["Pending Tasks", self.pending_tasks]]
        return tabulate(table, tablefmt="outline")

def main():
    global current_user
    global classes
    global users
    options_user = {
            1: add_user,
            2: remove_user,
            3: authenticator
        }
    while True:
        try:
            option = option_menu_user()
        except ValueError:
            continue;
        if option == 3:
            options_user[option]()
            break;
        elif option in options_user:
            options_user[option]()
            continue;
        else:
            sys.exit("Thanks for visiting!")
    options_tm={
            1: add_task,
            2: remove_task,
            3: mark_as_done,
            4: reschedule_task,
            5: display_stats,
            6: display_all_tasks
    }
    while True:
        option1=option_menu_task_manager()
        if option1 in options_tm:
            options_tm[option1]()
            continue;
        else:
            sys.exit("Thanks for visiting!")

def authenticator():
    username = input("Enter Username: ").capitalize()
    db_file_name = f"users.db"
    trys=0
    if os.path.exists(db_file_name):
        user_file = sqlite3.connect(db_file_name)
        c = user_file.cursor()
        c.execute("SELECT name, password FROM users")
        rows = c.fetchall()
        for row in rows:
            if row[0] == username:
                while True:
                    password = input("Enter Password: ")
                    if row[1] == password:
                        global current_user
                        current_user = username
                        print("Login successful!")
                        user_file.close()
                        global classes
                        classes[f'{username}']=task_manager(username,password)
                        return
                    elif trys>1:
                        sys.exit("Too many incorrect trys")
                    else:
                        user_file.close()
                        print("Incorrect password.")
                        trys+=1
                        continue
    print("Username does not exist.")
    return


def option_menu_user():
    menu= [
        {"Option_No.":1, "Option":"Add User"},
        {"Option_No.":2, "Option":"Remove User"},
        {"Option_No.":3, "Option":"Sign in to an existing account"},
        {"Option_No.":"Default", "Option":"Exit"}
    ]
    print(tabulate(menu, headers="keys", tablefmt="heavy_outline"))
    return int(input("Enter option: "))

def option_menu_task_manager():
    menu= [
        {"Option_No.":1, "Option":"Add task"},
        {"Option_No.":2, "Option":"Remove task"},
        {"Option_No.":3, "Option":"Mark task as done"},
        {"Option_No.":4, "Option":"Reschedule task"},
        {"Option_No.":5, "Option":"Display stats for tasks completed"},
        {"Option_No.":"6", "Option":"Display All tasks"},
        {"Option_No.":"Default", "Option":"Exit"}
    ]
    print(tabulate(menu, headers="keys", tablefmt="heavy_grid"))
    return int(input("Enter option:"))

def add_user():
    while True:
            name=input("Enter name for the user: ").capitalize()
            if len(name)<5:
                print("Enter a longer name")
                continue
            password=input("Enter a secure password: ")
            if len(password)<5:
                continue
            break
    global users
    global classes
    classes[f'{name}']=task_manager(name,password)
    users.append({'name':name,'password':password})
    user_file = sqlite3.connect('users.db')
    c=user_file.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, password TEXT)''')
    c.execute("INSERT INTO users (name, password) VALUES (?, ?)", (name, password))
    user_file.commit()
    user_file.close()

def remove_user():
    global classes
    global users
    ip = input("Enter Username: ").capitalize()
    db_file_name=f"{ip}.db"
    if os.path.exists(db_file_name):
        user_file = sqlite3.connect('users.db')
        c = user_file.cursor()
        c.execute("DELETE FROM users WHERE name=?", (ip,))
        user_file.commit()
        user_file.close()
        os.remove(db_file_name)
    else:
        print("Username does not exist")

def add_task():
    global classes
    global current_user
    Task=input("Enter name of task: ")
    Priority=input("Enter priority for the task: ").lower()
    Date=input("Enter due date: ")
    dict_task={"task":Task,"priority":Priority,"due_date":Date}
    classes[current_user].add_task(dict_task)

def remove_task():
    global classes
    global current_user
    Task=input("Enter task to remove: ")
    classes[current_user].remove_task(Task)

def mark_as_done():
    global classes
    global current_user
    Task=input("Enter task to mark as done: ")
    classes[current_user].mark_as_done(Task)

def reschedule_task():
    global classes
    global current_user
    Task=input("Enter name of task: ")
    new_date=input("Enter new due date for the task: ")
    classes[current_user].reschedule_task(Task, new_date)

def display_stats():
    global classes
    global current_user
    print(classes[current_user].stats)

def display_all_tasks():
    global classes
    global current_user
    print(classes[current_user])

def unused_fun(i):
    return i

def unused_fun1(j):
    return j

if __name__=="__main__":
    main()