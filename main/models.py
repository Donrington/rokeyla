from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

db = SQLAlchemy()

class Admin(db.Model):
    __tablename__ = 'admins'
    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_pic = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    theme_preference = db.Column(db.String(10), nullable=True)  # New field
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Password hashing methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Admin {self.username}>"


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)  # Added unique constraint
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True)
    facebook_id = db.Column(db.String(255), nullable=True)
    google_id = db.Column(db.String(255), nullable=True)
    theme = db.Column(db.String(10), nullable=False, default='light')
    language = db.Column(db.String(10), nullable=False, default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    two_factor_auth = db.Column(db.Boolean, nullable=False, default=False)
    data_sharing = db.Column(db.Boolean, nullable=False, default=True)
    email_notifications = db.Column(db.Boolean, nullable=False, default=True)
    sms_notifications = db.Column(db.Boolean, nullable=False, default=False)

    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    cart = db.relationship('Cart', backref='user', uselist=False, lazy=True, cascade='all, delete-orphan')
    wishlist = db.relationship('Wishlist', backref='user', lazy=True, cascade='all, delete-orphan')

class Category(db.Model):
    __tablename__ = 'categories'
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to self
    parent = db.relationship('Category', remote_side=[category_id], backref='subcategories')

    products = db.relationship('Product', backref='category', lazy=True)




class Product(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    sizes = db.Column(db.String(255), nullable=True)
    colors = db.Column(db.String(255), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)

    images = db.relationship('ProductImage', backref='product', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', back_populates='product', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('CartItem', back_populates='product', lazy=True, cascade='all, delete-orphan')
    wishlists = db.relationship('Wishlist', backref='product', lazy=True, cascade='all, delete-orphan')

    @property
    def size_list(self):
        if self.sizes:
            return self.sizes.split(',')
        return []

    @property
    def color_list(self):
        if self.colors:
            return self.colors.split(',')
        return []





class ProductImage(db.Model):
    __tablename__ = 'product_images'
    image_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)




class OrderStatus(Enum):
    PENDING = 'Pending'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'
    CANCELLED = 'Cancelled'


class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    order_status = db.Column(db.String(50), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    cancel_request = db.Column(db.Boolean, default=False)  # New field for cancellation request

    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='order', lazy=True, cascade='all, delete-orphan')


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    size = db.Column(db.String(50), nullable=True)  # Add size
    color = db.Column(db.String(50), nullable=True)  # Add color
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', back_populates='order_items')


class Cart(db.Model):
    __tablename__ = 'cart'
    cart_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cart_items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')


class CartItem(db.Model):
    __tablename__ = 'cart_items'
    cart_item_id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.cart_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    size = db.Column(db.String(10), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', back_populates='cart_items')



class Payment(db.Model):
    __tablename__ = 'payments'
    payment_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)


class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    wishlist_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)




class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)  # Link to user
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.admin_id'), nullable=True)  # Link to admin (optional)
    message = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(50), nullable=False)  # e.g., 'fas fa-user', 'fas fa-shopping-cart'
    time = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('activities', lazy=True))
    admin = db.relationship('Admin', backref=db.backref('admin_activities', lazy=True))

    def __repr__(self):
        return f"<Activity {self.message}>"


class Message(db.Model):
    __tablename__ = 'messages'
    message_id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('admins.admin_id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    sender = db.relationship('Admin', backref=db.backref('sent_messages', lazy=True))
    receiver = db.relationship('User', backref=db.backref('messages', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f"<Message {self.subject} from Admin {self.sender_id} to User {self.receiver_id}>"




# models.py

class Notification(db.Model):
    __tablename__ = 'notifications'
    notification_id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.admin_id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), nullable=True)  # URL to link to when clicked
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    icon = db.Column(db.String(50), nullable=True)  # FontAwesome icon class

    admin = db.relationship('Admin', backref=db.backref('notifications', lazy='dynamic'))




class Coupon(db.Model):
    __tablename__ = 'coupons'

    coupon_id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)  # Unique coupon code
    discount_value = db.Column(db.Float, nullable=False)  # Discount amount or percentage
    discount_type = db.Column(db.Enum('percentage', 'fixed', name='discount_type'), nullable=False)  # Type of discount
    minimum_order_value = db.Column(db.Float, nullable=True)  # Minimum order value for the coupon to be valid
    max_discount = db.Column(db.Float, nullable=True)  # Maximum discount for percentage-based coupons
    usage_limit = db.Column(db.Integer, nullable=True)  # How many times the coupon can be used
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Add this field
    usage_count = db.Column(db.Integer, default=0)  # Current usage count
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Start date of the coupon

    end_date = db.Column(db.DateTime, nullable=True)  # End date of the coupon
    is_active = db.Column(db.Boolean, default=True)  # Whether the coupon is active

    def is_valid(self):
        """
        Check if the coupon is valid based on its start date, end date, usage limit, and active status.
        """
        if not self.is_active:
            return False
        if self.start_date and self.start_date > datetime.utcnow():
            return False
        if self.end_date and self.end_date < datetime.utcnow():
            return False
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        return True
    def increment_usage(self):
        """
        Increment the usage count of the coupon and persist to the database.
        """
        if self.usage_limit is None or self.usage_count < self.usage_limit:
            self.usage_count += 1
            db.session.add(self)  # Add the coupon object to the session
            db.session.commit()   # Commit changes to the database


    def __repr__(self):
        return f"<Coupon {self.code} | {self.discount_value} {self.discount_type}>"


class Ad(db.Model):
    __tablename__ = 'ads'
    ad_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)  # HTML content for the ad
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Add any other fields you need




class NewsletterSubscriber(db.Model):
    __tablename__ = 'newsletter_subscribers'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)