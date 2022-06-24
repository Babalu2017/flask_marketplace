from flask import render_template, request, redirect, url_for
from taskmanager import app, db
from taskmanager.models import Category, Task



@app.route("/")
def home():
    return render_template("tasks.html")

@app.route("/categories") 
def categories(): #first function
    categories_added = list(Category.query.order_by(Category.category_name).all())
    return render_template("categories.html", categoriesTemplate=categories_added) # categoriesTemplate will be usend inside the html template with jinja notation{{%%}}.It's a list so it can be iterated with a for loop

@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = Category(category_name=request.form.get("category_name"))
        db.session.add(category)
        db.session.commit()
        return redirect(url_for("categories"))
    return render_template("add_category.html")

@app.route("/edit_category/<int:any_name_category_id>", methods=["GET", "POST"])
def edit_category(any_name_category_id):
    categoryFunc = Category.query.get_or_404(any_name_category_id)
    if request.method == "POST":
        categoryFunc.category_name = request.form.get("category_name1") # category_name1 comes from edit_category templates input name="category_name1"
        db.session.commit()
        return redirect(url_for("categories")) #categories comes from the first function see top page line 12
    return render_template("edit_category.html", categoryTemp=categoryFunc)

@app.route("/delete_category/<int:any_name_category_id>")
def delete_category(any_name_category_id):
    categoryFunc = Category.query.get_or_404(any_name_category_id)
    db.session.delete(categoryFunc)
    db.session.commit()
    return redirect(url_for("categories")) #categories comes from the first function see top page line 12