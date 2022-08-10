from marketplace import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    categories = db.relationship("Category", backref='user',cascade="all, delete", lazy=True)
    items = db.relationship("Item", backref="user", cascade="all, delete", lazy=True)
    message = db.relationship("Message", backref="user", cascade="all, delete", lazy=True)


    def __repr__(self):
        return f"<User %r>' % self.id, self.username"

    

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(25), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    items = db.relationship("Item", backref="category", cascade="all, delete", lazy=True)
    

    def __repr__(self):
        return "#{0} - Category: {1} | User_id: {2}".format(
            self.id, self.category_name, self.user_id
        )
        


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(50), nullable=False)
    item_description = db.Column(db.Text, nullable=False)
    location_pickup = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id", ondelete="CASCADE"), nullable=False)
    file_img = db.Column(db.Text, unique=True, nullable=False)
    post_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    

    def __repr__(self):
        return "#{0} - Item: {1}".format(
            self.id, self.item_name
        )


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.Text, nullable=False)
    message = db.Column(db.Text, nullable=False)
    msg_date = db.Column(db.DateTime, nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)    

    def __repr__(self):
        return "#{0} - Message: {1} | Sender_id: {2} | Recipient_id: {3}".format(
            self.id, self.message, self.sender_id, self.recipient_id
        )

    

