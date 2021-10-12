from flask import Flask, request, render_template, session, redirect, url_for, flash, jsonify
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import os
import stripe
import json
import Mail

stripe.api_key = '<---YOUR_SECRET_STRIPE_API_KEY--->'


import db_operatoins

app = Flask(__name__)

app.config['SECRET_KEY'] = '<---YOUR_SECRET_FORM_KEY--->'


@app.route('/')
@app.route('/index')
def index():
    products = db_operatoins.get_all_products()
    user = None
    if 'user' in session:
        user = session['user']

    if len(products) > 6:
        products = products[:6]

    return render_template('index.html', user=user, products=products)


@app.route('/sales')
def sales():
    search = request.args.get('search')
    if search != None:
        products = db_operatoins.get_search_products(search)
    else:
        products = db_operatoins.get_all_products()
    user = None
    if 'user' in session:
        user = session['user']

    return render_template('sales.html', user=user, products=products)


@app.route('/about')
def about():
    user = None
    if 'user' in session:
        user = session['user']

    return render_template('about.html', user=user)


@app.route('/contact')
def contact():
    user = None
    if 'user' in session:
        user = session['user']

    return render_template('contact.html', user=user)


@app.route('/product')
def product():
    products = db_operatoins.get_all_products()
    edit_id = request.args.get('id')
    edit_product = None
    if edit_id != None:
        edit_product = db_operatoins.get_one_product(edit_id)
    if 'admin' in session:
        return render_template('admin_products.html', admin=session['admin'], products=products, edit_product=edit_product )
    else:
        return redirect(url_for('login'))


@app.route('/product_details')
def product_details():
    edit_id = request.args.get('id')

    if edit_id is None:
        return redirect(url_for('sales'))

    edit_product = None
    if edit_id != None:
        edit_product = db_operatoins.get_one_product(edit_id)

    user = None
    if 'user' in session:
        user = session['user']

    return render_template('product_details.html',user=user,edit_product=edit_product)


@app.route('/product_order')
def product_order():
    edit_id = request.args.get('id')

    user = None
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']

    if edit_id is None:
        return redirect(url_for('sales'))

    edit_product = None
    if edit_id != None:
        edit_product = db_operatoins.get_one_product(edit_id)


    return render_template('product_order.html', user=user, edit_product=edit_product)


@app.route('/order_details')
def order_details():
    order_id = request.args.get('id')

    user = None
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']

    if order_id is None:
        return redirect(url_for('sales'))

    order = db_operatoins.get_one_order(order_id)

    return render_template('order_details.html', user=user, order=order)


@app.route('/charge_order', methods=['POST'])
def charge_order():
    token = request.form['stripeToken']
    email = request.form['stripeEmail']
    address = request.form['address']
    contact = request.form['contact']
    quantity = request.form['wanted']
    product_id = request.form['product_id']

    product = db_operatoins.get_one_product(product_id)

    price = int(product[6])

    order = stripe.Charge.create(
        amount=price,
        currency="usd",
        source=token,
        description="Order Created",
    )

    user = session['user']
    db_operatoins.insert_user_oder(user[0], product[0], price, address, 'Paid', order.stripe_id, contact, quantity, email)

    order = db_operatoins.get_last_order()

    Mail.send_order_Mail(email, 'Your Order is Placed Successfully.', order)

    return redirect(url_for('order_details', id=order[0]))


@app.route('/insert_product', methods=['POST'])
def insert_product():
    name = request.form['name']
    category = request.form['category']
    details = request.form['details']
    others = request.form['others']
    quantity = request.form['qunatity']
    price = request.form['price']

    db_operatoins.insert_product(name, category, details, others, quantity, price)
    last_product = db_operatoins.get_last_product()

    files = request.files.getlist('img')

    images_path = []
    for index, file in enumerate(files):
        filename = secure_filename(file.filename)
        if filename != '':
            if not os.path.exists('static/product_images/' + str(last_product[0])):
                os.makedirs('static/product_images/' + str(last_product[0]))
            filename, file_extension = os.path.splitext(filename)
            file.save(os.path.join('static/product_images/' + str(last_product[0]), str(index+1) + file_extension))
            images_path.append('static/product_images/' + str(last_product[0]) + '/' + str(index+1) + file_extension)

    db_operatoins.update_product_images_path(','.join(images_path), last_product[0])

    flash('Product Inserted Successfully!')
    return redirect(url_for('product'))


@app.route('/update_product', methods=['POST'])
def update_product():
    id = request.form['id']
    name = request.form['name']
    category = request.form['category']
    details = request.form['details']
    others = request.form['others']
    quantity = request.form['qunatity']
    price = request.form['price']

    db_operatoins.update_product(id, name, category, details, others, quantity, price)

    flash('Product Updated Successfully!')
    return redirect(url_for('product'))



@app.route('/delete_product', methods=['GET'])
def delete_product():
    id = request.args.get('id')
    if id != None:
        db_operatoins.delete_product(id)
    flash('Product Deleted Successfully!')
    return redirect(url_for('product'))


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/verify_user', methods=['GET'])
def verify_user():
    user_id = request.args.get('id')

    if user_id is None:
        flash('Broken Link, Account not Found')
        return redirect(url_for('login'))

    user = db_operatoins.get_user_by_id(user_id)
    if user[7] == 1:
        flash('Email is already Verified.')
        return redirect(url_for('login'))

    db_operatoins.verify_email(user_id)
    flash('Email is Verified Successfully.')
    return redirect(url_for('login'))



@app.route('/signup_user', methods=['POST'])
def signup_user():
    name = request.form['name']
    email = request.form['email']
    contact = request.form['contact']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        flash('Password and Confirm Password are Not Same!')
        return redirect(url_for('signup'))

    if db_operatoins.get_user_by_mail(email) != None:
        flash('Email Already Exists!')
        return redirect(url_for('signup'))

    db_operatoins.insert_user(name, email, contact, password)

    user = db_operatoins.get_last_user()

    Mail.send_verify_Mail(email, 'Verify your Email First.', user[0])

    flash('Please Check your Email for Confirmation!')
    return redirect(url_for('login'))


@app.route('/contact_us', methods=['POST'])
def contact_us():
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']

    Mail.sendMail_contactus(subject, 'Name: {0}\nEmail: {1}\nMessage: {2}'.format(name, email, message))
    flash('We received your Message Successfully, We will get back to you shortly.')
    return redirect(url_for('contact'))


@app.route('/login_user', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']

    user = db_operatoins.get_user_by_mail(email)
    if user == None:
        flash('Email/Password is not Correct!')
        return redirect(url_for('login'))

    if check_password_hash(user[5], password) and user[7] == 0:
        flash('Please confirm your Email First!')
        return redirect(url_for('login'))

    if check_password_hash(user[5], password) and user[6] == 'Admin':
        session['admin'] = user
        return redirect(url_for('product'))

    if check_password_hash(user[5], password) and user[6] == 'User':
        session['user'] = user
        return redirect(url_for('index'))

    flash('Email/Password is not Correct!')
    return redirect(url_for('login'))


@app.route('/logout', methods=['GET'])
def logout():
    if 'user' in session:
        session.pop('user', None)

    return redirect(url_for('login'))


@app.route('/admin_logout', methods=['GET'])
def admin_logout():
    if 'admin' in session:
        session.pop('admin', None)

    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)