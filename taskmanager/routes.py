from lib2to3.pgen2 import driver
from flask import render_template, request, redirect, url_for
from taskmanager import app, db
from taskmanager.models import Category, Task



@app.route("/")
def home():
    categories = list(Category.query.order_by(Category.category_name).all())
    tasksFunc = list(Task.query.order_by(Task.id).all())
    return render_template("tasks.html", tasksTemplate=tasksFunc, categories = categories)
    # return render_template("tasks.html", tasksTemplate=tasksFunc)




 
 

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

@app.route("/add_task", methods=["GET", "POST"])
def add_task():
    categories = list(Category.query.order_by(Category.category_name).all())
    if request.method == "POST":
        task = Task(
            task_name=request.form.get("task_name"),
            task_description=request.form.get("task_description"),
            is_urgent=bool(True if request.form.get("is_urgent") else False),
            due_date=request.form.get("due_date"),
            category_id=request.form.get("category_id")
        )
        db.session.add(task)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_task.html", categories=categories)

@app.route("/edit_task/<int:any_task_id>", methods=["GET", "POST"])
def edit_task(any_task_id):
    taskFunc = Task.query.get_or_404(any_task_id)
    categories = list(Category.query.order_by(Category.category_name).all())
    if request.method == "POST":
        taskFunc.name = request.form.get("task_name")
        taskFunc.description = request.form.get("task_description")
        taskFunc.is_urgent = bool(True if request.form.get("is_urgent") else False)
        taskFunc.due_date = request.form.get("due_date")
        taskFunc.category_id = request.form.get("category_id")
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit_task.html", task=taskFunc, categories=categories)

@app.route("/delete_task/<int:any_task_id>")
def delete_task(any_task_id):
    taskFunc = Task.query.get_or_404(any_task_id)
    db.session.delete(taskFunc)
    db.session.commit()
    return redirect(url_for("home")) #home comes from the first function see top page line 8