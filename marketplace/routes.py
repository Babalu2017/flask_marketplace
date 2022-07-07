import os
import pwd
import getpass
from flask import render_template, request, redirect, url_for, flash, session
from marketplace import app, db
from marketplace.models import Category, Item, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

@app.route("/")
@login_required
def dashboard():
    current_user_id = current_user.id
    users = current_user.username
    categories = list(Category.query.order_by(Category.id).all())
    itemFunc = list(Item.query.order_by(Item.id).all())

    return render_template("dashboard.html", 
    itemFunc=itemFunc, categories = categories, users=users, current_user_id=current_user_id)


@app.route("/home")
@login_required
def home():
    current_user_id = current_user.id
    users = current_user.username
    # print(f"here: {current_user.username}")
    # print(f"here: {current_user.id}")

    # users = list(User.query.order_by(User.id))
    # categories = list(Category.query.order_by(Category.category_name).all())  
    categories = list(Category.query.order_by(Category.id).all())
    category_filter = list(Category.query.filter(Category.user_id == current_user_id))

    itemFunc = list(Item.query.order_by(Item.id).all())
    return render_template("items.html", category_filter=category_filter, itemFunc=itemFunc, categories = categories, users=users, current_user_id=current_user_id)


# Authentication
@app.route('/login', methods=["GET", "POST"])
def login():
    users = list(User.query.order_by(User.id).all())
    # data = request.form
    # print(data)
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        


        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                # flash('Logged in successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for("dashboard"))
            else:
                flash('Incorrect password, try again', category='error_login')
        else:
            flash('Email does not exist.', category='error_login')
    return render_template("login.html", users=users)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))
    # return render_template("login.html")

@app.route('/sign-up', methods=["GET", "POST"])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        password1 = request.form.get('password2')
    
        user_email = User.query.filter_by(email=email).first()
        user_name = User.query.filter_by(username=username).first()         
            
        if user_email:
            flash('Email already exists !', category='error')
        elif len(username) < 5:
            flash('Username must be greater than 4 characters.', category='error')
        elif user_name:
            flash('Username already exsist.', category='error')
        elif len(email) < 7:
            flash('Email must be greater than 6 characters.', category='error')
        elif password != password1:
            flash('Password don\'t match.', category='error')
        elif len(password) < 5:
            flash('Password must contain at least 5 characters', category='error')
        else:
            new_user = User(username=username, email=email, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            # flash('Account created!', category='success')
            return redirect(url_for("dashboard"))
            # send form to database

    return render_template("sign_up.html")
# End Auth

@app.route("/categories")
@login_required
def categories(): #first function
    print(f"here: {current_user.username}")
    print(f"here: {current_user.id}")
    current_user_id = current_user.id
    users = current_user.username
    itemFunc = list(Item.query.order_by(Item.id).all())

    # users = list(User.query.order_by(User.id).all())
    # categories = list(Category.query.order_by(Category.category_name).all())
    categories = list(Category.query.order_by(Category.id).all())
    category_filter = list(Category.query.filter(Category.user_id == current_user_id))
    # print(f"category filtered by user_id: {category_filter[-1].user_id}")
    print(f"category filtered by user_id: {category_filter}")

    # print(f"user_id: {categories}")

    return render_template("categories.html", category_filter=category_filter, categories = categories, users=users, itemFunc=itemFunc, current_user_id=current_user_id) # the first categories(FIRST:categories = SECOND:categories) will be usend inside the html template with jinja notation{{%%}}.The second is the name variable that grab all the categories from the database. It's a list so it can be iterated with a for loop


@app.route("/add_category", methods=["GET", "POST"])
@login_required
def add_category():
    users = current_user.username
    categories = list(Category.query.order_by(Category.id).all())

    # users = list(User.query.order_by(User.id).all())
    if request.method == "POST":
        category = Category(
            category_name=request.form.get("category_name"),
            user_id=current_user.id
        )
        db.session.add(category)
        db.session.commit()
        return redirect(url_for("categories"))
    return render_template("add_category.html", users=users, categories=categories)

@app.route("/edit_category/<int:any_name_category_id>", methods=["GET", "POST"])
@login_required
def edit_category(any_name_category_id):
    users = current_user.username
    categoryFunc = Category.query.get_or_404(any_name_category_id)
    if request.method == "POST":
        categoryFunc.category_name = request.form.get("category_name1") # category_name1 comes from edit_category templates input name="category_name1"
        db.session.commit()
        return redirect(url_for("categories")) #categories comes from the first function see top page line 12
    return render_template("edit_category.html", categoryTemp=categoryFunc, users=users)

@app.route("/delete_category/<int:any_name_category_id>")
@login_required
def delete_category(any_name_category_id):
    categoryFunc = Category.query.get_or_404(any_name_category_id)
    db.session.delete(categoryFunc)
    db.session.commit()
    return redirect(url_for("categories")) #categories comes from the first function see top page line 12

@app.route("/add_item", methods=["GET", "POST"])
@login_required
def add_item():
    current_user_id = current_user.id
    users = current_user.username
    # users = list(User.query.order_by(User.id).all())
    # categories = list(Category.query.order_by(Category.category_name).all())
    categories = list(Category.query.order_by(Category.id).all())

    if request.method == "POST":
        item = Item(
            item_name=request.form.get("item_name"),
            item_description=request.form.get("item_description"),
            is_urgent=bool(True if request.form.get("is_urgent") else False),
            due_date=request.form.get("due_date"),
            category_id=request.form.get("category_id"),
            user_id=current_user.id

        )
        db.session.add(item)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_item.html", categories=categories, users=users, current_user_id=current_user_id)

@app.route("/edit_item/<int:any_item_id>", methods=["GET", "POST"])
@login_required
def edit_item(any_item_id):
    users = current_user.username
    item = Item.query.get_or_404(any_item_id)
    # categories = list(Category.query.order_by(Category.category_name).all())
    categories = list(Category.query.order_by(Category.id).all())

    if request.method == "POST":
        item.item_name = request.form.get("item_name")
        item.item_description = request.form.get("item_description")
        item.is_urgent = bool(True if request.form.get("is_urgent") else False)
        item.due_date = request.form.get("due_date")
        item.category_id = request.form.get("category_id")
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit_item.html", item=item, categories=categories, users=users)

@app.route("/delete_item/<int:any_item_id>")
@login_required
def delete_item(any_item_id):
    itemFunc = Item.query.get_or_404(any_item_id)
    db.session.delete(itemFunc)
    db.session.commit()
    return redirect(url_for("home")) #home comes from the first function see top page line 8