import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import g
from datetime import datetime

DATABASE = '<---YOUR_DataBase_Link--->'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def get_user_by_mail(email):
    cursor = get_db().cursor()
    sql = "SELECT * FROM Users WHERE Email='{0}'".format(email)
    cursor.execute(sql)
    user = cursor.fetchone()
    return user


def get_user_by_id(id):
    cursor = get_db().cursor()
    sql = "SELECT * FROM Users WHERE Id='{0}'".format(int(id))
    cursor.execute(sql)
    user = cursor.fetchone()
    return user


def get_last_user():
    cursor = get_db().cursor()
    sql = "SELECT * FROM Users ORDER BY Id DESC Limit 1"
    cursor.execute(sql)
    product = cursor.fetchone()
    return product


def insert_user(name, email,contact, password):
    hashpass = generate_password_hash(password, method='sha256')
    mycursor = get_db().cursor()
    sql = "INSERT INTO Users (Name, Email, Contact, Password, Type, Status) VALUES ('{0}', '{1}', '{2}', '{3}', 'User', 0)".format(name, email, contact, hashpass)
    mycursor.execute(sql)
    get_db().commit()
    return


def verify_email(id):
    mycursor = get_db().cursor()
    sql = "UPDATE Users SET Status='1' WHERE Id='{0}'".format(int(id))
    mycursor.execute(sql)
    get_db().commit()
    return


def insert_product(name, category, details, others, quantity, price):
    mycursor = get_db().cursor()
    sql = "INSERT INTO Products (Name, Category, Details, Others, Quantity, Price) VALUES " \
          "('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')".format(name, category, details, others, quantity, price)
    mycursor.execute(sql)
    get_db().commit()
    return


def update_product(id ,name, category, details, others, quantity, price):
    mycursor = get_db().cursor()
    sql = "UPDATE Products SET Name='{0}', Category='{1}', Details='{2}', Others='{3}', Quantity='{4}', Price='{5}' " \
          "WHERE Id='{6}'".format(name, category, details, others, quantity, price, int(id))
    mycursor.execute(sql)
    get_db().commit()
    return


def update_product_images_path(path, id):
    mycursor = get_db().cursor()
    sql = "UPDATE Products SET Image='{0}' WHERE Id='{1}'".format(path, int(id))
    mycursor.execute(sql)
    get_db().commit()
    return


def insert_user_oder(User_ID, Products, Price, Address, Payment_Status, Stripe_ID, Contact, Quantity, s_mail):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    mycursor = get_db().cursor()
    sql = "INSERT INTO Orders (User_ID, Date_Time, Products, Price, Address, Payment_Status, Stripe_ID, Contact, Quantity, Stripe_Mail) " \
          "VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}')" \
          "".format(int(User_ID), dt_string, Products, int(Price), Address, Payment_Status, Stripe_ID, Contact, int(Quantity), s_mail)
    mycursor.execute(sql)
    get_db().commit()
    return


def get_all_products():
    cursor = get_db().cursor()
    sql = "SELECT * FROM Products ORDER BY Id DESC"
    cursor.execute(sql)
    products = cursor.fetchall()
    return products


def get_last_product():
    cursor = get_db().cursor()
    sql = "SELECT * FROM Products ORDER BY Id DESC Limit 1"
    cursor.execute(sql)
    product = cursor.fetchone()
    return product


def get_one_product(id):
    cursor = get_db().cursor()
    sql = "SELECT * FROM Products WHERE Id='{0}'".format(int(id))
    cursor.execute(sql)
    product = cursor.fetchone()
    return product


def delete_product(id):
    mycursor = get_db().cursor()
    sql = "DELETE FROM Products WHERE Id='{0}'".format(int(id))
    mycursor.execute(sql)
    get_db().commit()
    return


def get_search_products(search):
    cursor = get_db().cursor()
    sql = "SELECT * FROM Products WHERE Name LIKE '%{0}%' OR Category LIKE '%{0}%' OR Details LIKE '%{0}%' OR Others LIKE '%{0}%'".format(search)
    cursor.execute(sql)
    products = cursor.fetchall()
    return products


def get_last_order():
    cursor = get_db().cursor()
    sql = "SELECT * FROM Orders ORDER BY Id DESC Limit 1"
    cursor.execute(sql)
    product = cursor.fetchone()
    return product


def get_one_order(id):
    cursor = get_db().cursor()
    sql = "SELECT * FROM Orders WHERE Id='{0}'".format(int(id))
    cursor.execute(sql)
    product = cursor.fetchone()
    return product
