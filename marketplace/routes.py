import os, boto3, json, botocore
import uuid
from flask import render_template, request, redirect, url_for, flash, session
from marketplace import S3_KEY, S3_SECRET, app, db, S3_BUCKET
from marketplace.models import Category, Item, Message, User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import requests
import urllib.parse
import time
import psycopg2
import psycopg2.extras
import folium

from flask_login import login_user, login_required, logout_user, current_user


@app.context_processor
def utility_processor():
    def folium_map(loc_address):
        url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(loc_address) +'?format=json'
        response = requests.get(url).json()
        lat = list(d['lat'] for d in response)
        lon = list(d['lon'] for d in response)
        coords = [str(lat[0]), str(lon[0])]
        mapA = folium.Map(
                    location=["51.5072","0.1276"], zoom_start=8, max_zoom=12 ,  tiles="Stamen Terrain"
                )
        london = folium.map.FeatureGroup()
        london.add_child(folium.CircleMarker(location=coords, radius = 15, color='#00BFFF',
                fill_color='#CD5C5C'))
        london_mrk = mapA.add_child(london)
        return london_mrk._repr_html_()
    return dict(folium_map=folium_map)
    
    



@app.route("/")
@login_required
def dashboard():
    current_user_id = current_user.id
    users = current_user.username

    categories = list(Category.query.order_by(Category.id).all())
    itemFunc = list(Item.query.order_by(Item.id).all())
    
    return render_template("dashboard.html",
                           itemFunc=itemFunc, categories=categories, users=users, current_user_id=current_user_id)




@app.route("/filter_by")
@login_required
def filter_by():
    current_user_id = current_user.id
    users = current_user.username
    categories = list(Category.query.order_by(Category.id).all())

    itemFunc = list(Item.query.order_by(Item.id).all())
    choesen_cat = request.args.get('type')
    filter_by_category_name = list(Category.query.order_by(
        Category.id).filter(Category.category_name == choesen_cat).all())
    for id_cat in filter_by_category_name:
        print(f"Here's your id: {id_cat.id}")

    filter_by_category_id = list(Item.query.order_by(
        Item.id).filter(Item.category_id == id_cat.id).all())
    print(f'here your category: {choesen_cat}')
    print(filter_by_category_id)

    return render_template("filter_by.html", choesen_cat=choesen_cat,
                           itemFunc=itemFunc, categories=categories, filter_by_category_id=filter_by_category_id, users=users, current_user_id=current_user_id)


@app.route("/home")
@login_required
def home():
    current_user_id = current_user.id
    users = current_user.username
    categories = list(Category.query.order_by(Category.id).all())
    category_filter = list(Category.query.filter(
        Category.user_id == current_user_id))

    items = list(Item.query.order_by(Item.id).all())
    return render_template("items.html", category_filter=category_filter, items=items, categories=categories, users=users, current_user_id=current_user_id)


# Authentication
@app.route('/login', methods=["GET", "POST"])
def login():
    users = list(User.query.order_by(User.id).all())
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
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
            new_user = User(username=username, email=email, password=generate_password_hash(
                password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for("dashboard"))

    return render_template("sign_up.html")


@app.route("/categories")
@login_required
def categories():  
    print(f"here: {current_user.username}")
    print(f"here: {current_user.id}")
    current_user_id = current_user.id
    users = current_user.username
    itemFunc = list(Item.query.order_by(Item.id).all())

    categories = list(Category.query.order_by(Category.id).all())
    category_filter = list(Category.query.filter(
        Category.user_id == current_user_id))
    print(f"category filtered by user_id: {category_filter}")


    return render_template("categories.html", category_filter=category_filter, categories=categories, users=users, itemFunc=itemFunc, current_user_id=current_user_id)


@app.route("/add_category", methods=["GET", "POST"])
@login_required
def add_category():
    current_user_id = current_user.id
    users = current_user.username
    categories = list(Category.query.order_by(Category.id).all())

    if request.method == "POST":
        category = Category(
            category_name=request.form.get("category_name"),
            user_id=current_user.id
        )
        db.session.add(category)
        db.session.commit()
        return redirect(url_for("categories"))
    return render_template("add_category.html", users=users, categories=categories, current_user_id=current_user_id)


@app.route("/edit_category/<int:any_name_category_id>", methods=["GET", "POST"])
@login_required
def edit_category(any_name_category_id):
    current_user_id = current_user.id
    users = current_user.username
    categoryFunc = Category.query.get_or_404(any_name_category_id)
    if request.method == "POST":
        categoryFunc.category_name = request.form.get("category_name1")
        db.session.commit()
        return redirect(url_for("categories"))
    return render_template("edit_category.html", categoryTemp=categoryFunc, users=users, current_user_id=current_user_id)


@app.route("/delete_category/<int:any_name_category_id>")
@login_required
def delete_category(any_name_category_id):
    categoryFunc = Category.query.get_or_404(any_name_category_id)
    db.session.delete(categoryFunc)
    db.session.commit()
    return redirect(url_for("categories"))


app.config['UPLOAD_FOLDER'] = "/Users/francescomiranda/Desktop/flask_market_place/marketplace/static/img/uploads"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

s3 = boto3.resource('s3',
                    aws_access_key_id=S3_KEY,
                    aws_secret_access_key=S3_SECRET)


@app.route("/add_item", methods=["GET", "POST"])
@login_required
def add_item():
    current_user_id = current_user.id
    users = current_user.username
    categories = list(Category.query.order_by(Category.id).all())

    now = time.strftime("%Y-%m-%d %H:%M:%S")

    if request.method == "POST":

        files = request.files['files']
        print(type(files))
        namefile = files.filename
        print(f'from add_item {files}')
        if files and allowed_file(files.filename):
            filename = secure_filename(files.filename)
            print(f"filename_secure: {filename}")
            print(f"filename_secure: {type(filename)}")

            unique_filename = str(uuid.uuid1()) + "_" + filename
            files.save(unique_filename)
            s3.meta.client.upload_file(
                Bucket=S3_BUCKET,
                Filename=unique_filename,
                Key=unique_filename
            )
            os.remove(unique_filename)
            files = unique_filename
            
        postcode = request.form.get("location_pickup")
        pcode = postcode.replace(" ","")
        if len(pcode) <=4:
            flash('You must insert a valid postcode !', category='error')
        elif len(pcode)>=9:
            flash('You must insert a valid postcode !', category='error')
        elif pcode.isalpha():
             flash('You must insert a valid postcode !', category='error')
        elif pcode.isdigit():
            flash('You must insert a valid postcode !', category='error')
        else:
            post_code = pcode.upper()
            item = Item(
            item_name=request.form.get("item_name"),
            item_description=request.form.get("item_description"),
            location_pickup=post_code,
            category_id=request.form.get("category_id"),
            file_img=f"https://flaskappmarketplace.s3.eu-west-2.amazonaws.com/{unique_filename}",
            post_date=now,
            user_id=current_user.id
        )
            flash('Item successfully listed')
            db.session.add(item)
            db.session.commit()
            return redirect(url_for("home"))
            
        
    
    return render_template("add_item.html", categories=categories, users=users, current_user_id=current_user_id)


@app.route("/edit_item/<int:any_item_id>", methods=["GET", "POST"])
@login_required
def edit_item(any_item_id):
    users = current_user.username
    item = Item.query.get_or_404(any_item_id)
    categories = list(Category.query.order_by(Category.id).all())
    now = time.strftime("%Y-%m-%d %H:%M:%S")

    if request.method == "POST":
        files = request.files['files']
        print(f'from edit_item: {files}')

        if files and allowed_file(files.filename):
            filename = secure_filename(files.filename)
            unique_filename = str(uuid.uuid1()) + "_" + filename

            files.save(unique_filename)
            s3.meta.client.upload_file(
                Bucket=S3_BUCKET,
                Filename=unique_filename,
                Key=unique_filename
            )
            os.remove(unique_filename)
            files = unique_filename
            item.file_img = f"https://flaskappmarketplace.s3.eu-west-2.amazonaws.com/{unique_filename}"

        item.item_name = request.form.get("item_name")
        item.item_description = request.form.get("item_description")
        item.location_pickup = request.form.get("location_pickup")
        item.category_id = request.form.get("category_id")
        item.post_date = now
        item.user_id = current_user.id
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit_item.html", item=item, categories=categories, users=users)


@app.route("/delete_item/<int:any_item_id>")
@login_required
def delete_item(any_item_id):
    itemFunc = Item.query.get_or_404(any_item_id)
    db.session.delete(itemFunc)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/inbox")
@login_required
def inbox():
    users_list = list(User.query.order_by(User.id).all())
    messages_list = list(Message.query.order_by(Message.id).all())
    current_user_id = current_user.id
    users = current_user.username
    return render_template("msgs_box.html", current_user_id=current_user_id, users=users, messages_list=messages_list, users_list=users_list )


@app.route("/read_message/<int:any_message_id>")
@login_required
def read_msg(any_message_id):
    users_list = list(User.query.order_by(User.id).all())
    read_message = Message.query.get_or_404(any_message_id)
    users = current_user.username
    return render_template("read_msg.html", users=users, read_message=read_message, users_list=users_list)


@app.route("/new_message", methods=["GET", "POST"])
@login_required
def new_msg():
    users_list = list(User.query.order_by(User.id).all())
    current_user_id = current_user.id
    users = current_user.username
    now = time.strftime("%Y-%m-%d %H:%M:%S")

    if request.method == "POST":
        flash('Message successfully sent')

        message = Message(
            subject=request.form.get("subject"),
            message=request.form.get("message"),
            msg_date=now,
            sender_id=current_user_id,
            recipient_id=request.form.get("recipient_id")
        )

        db.session.add(message)
        db.session.commit()
        return redirect(url_for("inbox"))
    return render_template("new_message.html", users=users, users_list=users_list)


@app.route("/replay_to_msg/<int:any_message_id>", methods=["GET", "POST"])
@login_required
def replay_to_msg(any_message_id):
    users_list = list(User.query.order_by(User.id).all())
    replay_message = Message.query.get_or_404(any_message_id)
    users = current_user.username
    current_user_id = current_user.id
    now = time.strftime("%Y-%m-%d %H:%M:%S")

    if request.method == "POST":
        for user in users_list:
            if user.id == replay_message.sender_id:
                replay_msg = Message(
                    subject = request.form.get("subject"),
                    message = request.form.get("message"),
                    msg_date = now,
                    sender_id = current_user_id,
                    recipient_id = user.id
                )
                db.session.add(replay_msg)
                db.session.commit()
                return redirect(url_for("inbox"))
    return render_template("replay_to_msg.html", users=users, replay_message=replay_message, users_list=users_list)


@app.route("/delete_message/<int:any_msg_id>")
@login_required
def delete_message(any_msg_id):
    message = Message.query.get_or_404(any_msg_id)
    db.session.delete(message)
    db.session.commit()
    return redirect(url_for("inbox"))
