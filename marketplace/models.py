from enum import unique
from marketplace import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    # schema for the User model
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    categories = db.relationship("Category", backref='user',cascade="all, delete", lazy=True)
    items = db.relationship("Item", backref="user", cascade="all, delete", lazy=True)

    def __repr__(self):
        # return '<User %r>' % self.id, self.username
        return f"<User %r>' % self.id, self.username"

    

class Category(db.Model):
    # schema for the Category model
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(25), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    items = db.relationship("Item", backref="category", cascade="all, delete", lazy=True)
    

    def __repr__(self):
        # __repr__ to represent itself in the form of a string
        # return f"Category: {self.id, self.category_name, self.user_id,}"
        
        return "#{0} - Category: {1} | User_id: {2}".format(
            self.id, self.category_name, self.user_id
        )
        


class Item(db.Model):
    # schema for the Item model
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(50), nullable=False)
    item_description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id", ondelete="CASCADE"), nullable=False)
    file_img = db.Column(db.Text, unique=True, nullable=False)
    post_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    

    def __repr__(self):
        # __repr__ to represent itself in the form of a string
        return "#{0} - Item: {1}".format(
            self.id, self.item_name
        )
    

