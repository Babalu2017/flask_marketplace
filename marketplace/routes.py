from email import message
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
        # print(*(d['lat'] for d in response))
        lat = list(d['lat'] for d in response)
        lon = list(d['lon'] for d in response)
        # print(response)
        # print(str(lat[0]))
        # print(str(lon[0]))
        coords = [str(lat[0]), str(lon[0])]
        # print(coords)
        # item_coords = [response["lat"],response["lon"]]
        # print(item_coords)
        mapA = folium.Map(
                    location=["51.5072","0.1276"], zoom_start=8, max_zoom=12 ,  tiles="Stamen Terrain"
                )
        # print(mapA)
        london = folium.map.FeatureGroup()
        london.add_child(folium.CircleMarker(location=coords, radius = 15, color='#00BFFF',
                fill_color='#CD5C5C'))
        london_mrk = mapA.add_child(london)
        # print(london_mrk._repr_html_())
        return london_mrk._repr_html_()
    return dict(folium_map=folium_map)
    
    



    # millard99 = [float(response[0]["lat"]), float(response[0]["lon"])]

    # print(millard99)
    # print(response[0]["lat"])
    # print(response[0]["lon"])

    # london_location = millard99
    # mapA = folium.Map(
    #         location=london_location, zoom_start=8, tiles="Stamen Terrain"
    #     )

    # london = folium.map.FeatureGroup()
    # london.add_child(folium.CircleMarker(location=[51.4877, -0.0319], radius = 20, color='#00BFFF',
    #     fill_color='#CD5C5C'))
    # london_mrk = mapA.add_child(london)
    # london_mrk._repr_html_()


# address = '99 millard road, London'
# url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'

# response = requests.get(url).json()
# millard99 = [float(response[0]["lat"]), float(response[0]["lon"])]

# print(millard99)
# print(response[0]["lat"])
# print(response[0]["lon"])
# # folium map

# london_location = millard99
# mapA = folium.Map(
#         location=london_location, zoom_start=8, tiles="Stamen Terrain"
#     )

# london = folium.map.FeatureGroup()
# london.add_child(folium.CircleMarker(location=[51.4877, -0.0319], radius = 20, color='#00BFFF',
#     fill_color='#CD5C5C'))
# london_mrk = mapA.add_child(london)
# london_mrk._repr_html_()

# print(type(london_mrk._repr_html_()))

@app.route("/")
@login_required
def dashboard():
    current_user_id = current_user.id
    users = current_user.username

    categories = list(Category.query.order_by(Category.id).all())
    itemFunc = list(Item.query.order_by(Item.id).all())
    
    # return render_template("dashboard.html",
    #                        itemFunc=itemFunc, mappa=london_mrk._repr_html_(), categories=categories, users=users, current_user_id=current_user_id)

    return render_template("dashboard.html",
                           itemFunc=itemFunc, categories=categories, users=users, current_user_id=current_user_id)



# @app.route("/map_dashboard")
# def map_dashboard():
#     current_user_id = current_user.id
#     users = current_user.username

#     categories = list(Category.query.order_by(Category.id).all())
#     itemFunc = list(Item.query.order_by(Item.id).all())
#     # creating a map
    
#     return render_template("dashboard.html", mappa=mapA._repr_html_(), itemFunc=itemFunc, categories=categories, users=users, current_user_id=current_user_id)


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
        print(f"Here's your fucking id: {id_cat.id}")

    filter_by_category_id = list(Item.query.order_by(
        Item.id).filter(Item.category_id == id_cat.id).all())
    print(f'here your category: {choesen_cat}')
    print(filter_by_category_id)

    # return render_template("filter_by.html",
    #                        itemFunc=itemFunc, mappa=london_mrk._repr_html_(), categories=categories, filter_by_category_id=filter_by_category_id, users=users, current_user_id=current_user_id)
    return render_template("filter_by.html",
                           itemFunc=itemFunc, categories=categories, filter_by_category_id=filter_by_category_id, users=users, current_user_id=current_user_id)


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
    category_filter = list(Category.query.filter(
        Category.user_id == current_user_id))

    items = list(Item.query.order_by(Item.id).all())
    return render_template("items.html", category_filter=category_filter, items=items, categories=categories, users=users, current_user_id=current_user_id)


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
            new_user = User(username=username, email=email, password=generate_password_hash(
                password, method='sha256'))
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
def categories():  # first function
    print(f"here: {current_user.username}")
    print(f"here: {current_user.id}")
    current_user_id = current_user.id
    users = current_user.username
    itemFunc = list(Item.query.order_by(Item.id).all())

    # users = list(User.query.order_by(User.id).all())
    # categories = list(Category.query.order_by(Category.category_name).all())
    categories = list(Category.query.order_by(Category.id).all())
    category_filter = list(Category.query.filter(
        Category.user_id == current_user_id))
    # print(f"category filtered by user_id: {category_filter[-1].user_id}")
    print(f"category filtered by user_id: {category_filter}")

    # print(f"user_id: {categories}")

    # the first categories(FIRST:categories = SECOND:categories) will be usend inside the html template with jinja notation{{%%}}.The second is the name variable that grab all the categories from the database. It's a list so it can be iterated with a for loop
    return render_template("categories.html", category_filter=category_filter, categories=categories, users=users, itemFunc=itemFunc, current_user_id=current_user_id)


@app.route("/add_category", methods=["GET", "POST"])
@login_required
def add_category():
    current_user_id = current_user.id
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
    return render_template("add_category.html", users=users, categories=categories, current_user_id=current_user_id)


@app.route("/edit_category/<int:any_name_category_id>", methods=["GET", "POST"])
@login_required
def edit_category(any_name_category_id):
    current_user_id = current_user.id
    users = current_user.username
    categoryFunc = Category.query.get_or_404(any_name_category_id)
    if request.method == "POST":
        # category_name1 comes from edit_category templates input name="category_name1"
        categoryFunc.category_name = request.form.get("category_name1")
        db.session.commit()
        # categories comes from the first function see top page line 12
        return redirect(url_for("categories"))
    return render_template("edit_category.html", categoryTemp=categoryFunc, users=users, current_user_id=current_user_id)


@app.route("/delete_category/<int:any_name_category_id>")
@login_required
def delete_category(any_name_category_id):
    categoryFunc = Category.query.get_or_404(any_name_category_id)
    db.session.delete(categoryFunc)
    db.session.commit()
    # categories comes from the first function see top page line 12
    return redirect(url_for("categories"))


app.config['UPLOAD_FOLDER'] = "/Users/francescomiranda/Desktop/flask_market_place/marketplace/static/img/uploads"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route("/add_item", methods=["POST"])
# @login_required
# def upload_image():
#     if 'file' not in request.files:
#         flash('No file part')
#         return redirect(request.url)
#     file = request.files['file']
#     if file.filename == '':
#         flash('No image selected for uploading')
#         return redirect(request.url)
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         #print('upload_image filename: ' + filename )
#         flash('Image successfully uploaded and displayed below')
#         return render_template('items.html', filename=filename)
#     else:
#         flash('Allowed image types are - png, jpg, jpeg, gif')
#         return redirect(request.url)


s3 = boto3.resource('s3',
                    aws_access_key_id=S3_KEY,
                    aws_secret_access_key=S3_SECRET)


# s3.meta.client.upload_file('/Users/francescomiranda/Desktop/flask_market_place/marketplace/static/img/uploads/bac6c92a-01f4-11ed-8e50-acde48001122_post-2.jpg', 'flaskappmarketplace','post-2.jpg')
# s3.meta.client.upload_file('/Users/francescomiranda/Desktop/flask_market_place/marketplace/static/img/uploads/4cc6d31e-01f6-11ed-9627-acde48001122_story-bg.jpg', 'flaskappmarketplace','storu-bg.jpg')
# s3.meta.client.upload_file('/Users/francescomiranda/Desktop/flask_market_place/marketplace/static/img/uploads/5112c5a8-0111-11ed-8aa5-acde48001122_i1.jpg', 'flaskappmarketplace','i1.jpg')

@app.route("/add_item", methods=["GET", "POST"])
@login_required
def add_item():
    current_user_id = current_user.id
    users = current_user.username
    # users = list(User.query.order_by(User.id).all())
    # categories = list(Category.query.order_by(Category.category_name).all())
    categories = list(Category.query.order_by(Category.id).all())

    # now = datetime.now().date()
    now = time.strftime("%Y-%m-%d %H:%M:%S")

    if request.method == "POST":

        # files = request.files.getlist('files[]')
        files = request.files['files']
        print(type(files))
        namefile = files.filename
        print(f'from add_item {files}')
        # for file in files:
        if files and allowed_file(files.filename):
            filename = secure_filename(files.filename)
            print(f"filename_secure: {filename}")
            print(f"filename_secure: {type(filename)}")

            unique_filename = str(uuid.uuid1()) + "_" + filename
            # save on directory we need it to getsize filename
            files.save(unique_filename)
            s3.meta.client.upload_file(
                Bucket=S3_BUCKET,
                Filename=unique_filename,
                Key=unique_filename
            )
            # after we getsize of filename (function that works behind the scene) we delete it from the directory
            os.remove(unique_filename)

            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # save file locally in img/uploads
            # files.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))

            # to_binary_file = ' '.join(map(bin,bytearray(unique_filename,'utf8')))
            # print(file)

            files = unique_filename
            # print(files)
            # print(now)
        flash('File(s) successfully uploaded')

        

        item = Item(
            item_name=request.form.get("item_name"),
            item_description=request.form.get("item_description"),
            location_pickup=request.form.get("location_pickup"),
            category_id=request.form.get("category_id"),
            file_img=f"https://flaskappmarketplace.s3.eu-west-2.amazonaws.com/{unique_filename}",
            post_date=now,
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
    now = time.strftime("%Y-%m-%d %H:%M:%S")

    if request.method == "POST":
        files = request.files['files']
        print(f'from edit_item: {files}')

        if files and allowed_file(files.filename):
            filename = secure_filename(files.filename)
            unique_filename = str(uuid.uuid1()) + "_" + filename
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            # to_binary_file = ' '.join(map(bin,bytearray(unique_filename,'utf8')))
        # print(file)

            files.save(unique_filename)
            s3.meta.client.upload_file(
                Bucket=S3_BUCKET,
                Filename=unique_filename,
                Key=unique_filename
            )
            # after we getsize of filename (function that works behind the scene) we delete it from the directory
            os.remove(unique_filename)
            files = unique_filename
            item.file_img = f"https://flaskappmarketplace.s3.eu-west-2.amazonaws.com/{unique_filename}"

        item.item_name = request.form.get("item_name")
        item.item_description = request.form.get("item_description")
        item.location_pickup = request.form.get("location_pickup")
        item.category_id = request.form.get("category_id")
        # item.file_img = f"https://flaskappmarketplace.s3.eu-west-2.amazonaws.com/{unique_filename}"
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
    # home comes from the first function see top page line 8
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


@app.route("/replay_to_msg")
@login_required
def replay_to_msg():
    users = current_user.username
    return render_template("replay_to_msg.html", users=users)
