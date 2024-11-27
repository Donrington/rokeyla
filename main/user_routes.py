from PIL import Image
import json, os
import io
import stripe
from os.path import basename
import random
import requests
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from functools import wraps
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from flask import * 
from flask_babel import Babel
from flask_socketio import SocketIO, emit, join_room, leave_room
from markupsafe import escape
import re 
from flask_dance.contrib.google import google
from flask_dance.contrib.facebook import facebook
from pathlib import Path
from flask_wtf.csrf import CSRFProtect, generate_csrf
from main import *
from main.forms import *
from main.models import *
from flask_login import login_required
from main.models import db
from sqlalchemy import func,desc  
from datetime import datetime, timedelta
from decimal import Decimal
import pytz


socketio = SocketIO(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('user/404.html', pagename='Page Not Found | Rokeyla Store'), 404

# Your existing login_required decorator
def login_required(f):
    @wraps(f)
    def login_check(*args, **kwargs):
        if session.get("logged_in") is not None:
            return f(*args, **kwargs)
        else:
            flash("Access Denied")
            return redirect(url_for('login'))
    return login_check

# Existing routes
@app.route('/')
def index():
    # Fetch featured products
    featured_products = Product.query.filter_by(is_featured=True).order_by(Product.created_at.desc()).limit(4).all()

    # Fetch newest products
    newest_products = Product.query.order_by(Product.created_at.desc()).limit(4).all()

    # Check if the user is logged in
    logged_in = session.get('logged_in', False)
    username = session.get('username') if logged_in else None
    form = NewsletterForm()
    # Fetch ad content from the database (assuming you have an Ad model)
    ad = Ad.query.filter_by(active=True).order_by(Ad.created_at.desc()).first()
    ad_content = ad.content if ad else None

    return render_template(
        'user/index.html',
        pagename='Rokeyla - Your Signature of Style | Luxury Fashion Brands',
        featured_products=featured_products,
        newest_products=newest_products,
        logged_in=logged_in,
        username=username,
        ad_content=ad_content,
        form=form
    )




@app.route('/about/')
def about():
    return render_template('user/about.html', pagename='About us | Rokeyla')

@app.route('/menshop/')
def men():
    # Fetch the "Men" parent category; ensure it exists in your database
    men_category = Category.query.filter_by(category_name='Men').first()
    form = NewsletterForm()
    if not men_category:
        flash('Men category not found.', 'danger')
        return redirect(url_for('index'))
    
    # Fetch all subcategory IDs under "Men"
    subcategories = Category.query.filter_by(parent_id=men_category.category_id).all()
    subcategory_ids = [subcategory.category_id for subcategory in subcategories]
    
    # Include the parent category ID if you have products directly under "Men" (optional)
    # If products are only under subcategories, you can omit this
    # category_ids = subcategory_ids + [men_category.category_id]
    category_ids = subcategory_ids  # Assuming products are only under subcategories
    
    # Fetch products under the "Men" category and its subcategories
    products = Product.query.filter(Product.category_id.in_(subcategory_ids)).order_by(Product.created_at.desc()).all()
    
    # Fetch best sellers (define your own logic, e.g., top-selling, most viewed, etc.)
    # Here, we'll just take the latest 5 products as an example
    best_sellers = Product.query.filter(Product.category_id.in_(subcategory_ids)).order_by(Product.created_at.desc()).limit(5).all()
    
    # Define a background image specific to Men's Shop (optional)
    background_image = 'images/mens_background.jpg'  # Ensure this image exists in 'static/images/'
    
    return render_template(
        'user/men.html',
        pagename='Rokeyla Men Shop | Rokeyla',
        products=products,
        best_sellers=best_sellers,
        background_image=background_image,
        men_category=men_category, form=form
    )

@app.route('/womenshop/')
def women():
    # Fetch the "Women" parent category
    women_category = Category.query.filter_by(category_name='Women').first()
    form = NewsletterForm() 
    if not women_category:
        flash('Women category not found.', 'danger')
        return redirect(url_for('index'))
    
    # Fetch all subcategory IDs under "Women"
    subcategories = Category.query.filter_by(parent_id=women_category.category_id).all()
    subcategory_ids = [subcategory.category_id for subcategory in subcategories]
    
    # Fetch products under the "Women" category and its subcategories
    products = Product.query.filter(Product.category_id.in_(subcategory_ids)).order_by(Product.created_at.desc()).all()
    

    page = request.args.get('page', 1, type=int)
    per_page = 12  # Number of products per page

    # Fetch products with pagination
    products_paginated = Product.query.filter(Product.category_id.in_(subcategory_ids))\
        .order_by(Product.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    # Fetch best sellers (modify logic as per your criteria)
    best_sellers = Product.query.filter(Product.category_id.in_(subcategory_ids)).order_by(Product.created_at.desc()).limit(5).all()
    
    # Define a background image specific to Women's Shop (optional)
    background_image = 'images/womens_background.jpg'  # Ensure this image exists in 'static/images/'
    
    return render_template(
        'user/women.html',
        pagename='Rokeyla Women Shop | Rokeyla',
        products=products_paginated.items,
        best_sellers=best_sellers,
        background_image=background_image,
        women_category=women_category,  # Pass women_category to the template
        pagination=products_paginated, # Pass women_category to the template
        form=form
    )


@app.route('/accessories/')
def accessories():
    # Fetch the "Accessories" parent category; ensure it exists in your database
    accessories_category = Category.query.filter_by(category_name='Accessories').first()
    form = NewsletterForm()
    if not accessories_category:
        flash('Accessories category not found.', 'danger')
        return redirect(url_for('index'))
    
    # Fetch all subcategory IDs under "Accessories"
    subcategories = Category.query.filter_by(parent_id=accessories_category.category_id).all()
    subcategory_ids = [subcategory.category_id for subcategory in subcategories]
    
    # Include the parent category ID if you have products directly under "Accessories" (optional)
    # If products are only under subcategories, you can omit this
    # category_ids = subcategory_ids + [accessories_category.category_id]
    category_ids = subcategory_ids  # Assuming products are only under subcategories
    
    # Fetch products under the "Accessories" category and its subcategories
    products = Product.query.filter(Product.category_id.in_(subcategory_ids)).order_by(Product.created_at.desc()).all()
    
    # Fetch best sellers (define your own logic, e.g., top-selling, most viewed, etc.)
    # Here, we'll just take the latest 5 products as an example
    best_sellers = Product.query.filter(Product.category_id.in_(subcategory_ids)).order_by(Product.created_at.desc()).limit(5).all()
    
    # Define a background image specific to Accessories Shop (optional)
    background_image = 'images/accessories_background.jpg'  # Ensure this image exists in 'static/images/'
    
    return render_template(
        'user/accessories.html',  # Replace 'men.html' with the 'accessories.html' template
        pagename='Rokeyla Accessories Shop | Rokeyla',
        products=products,
        best_sellers=best_sellers,
        background_image=background_image,
        accessories_category=accessories_category, form=form
    )


@app.route('/contact/')
def contact():
    form = NewsletterForm()
    return render_template('user/contact.html', pagename='Contact Us | Rokeyla', form=form)


@app.route('/product/<int:product_id>/')
def product_details(product_id):
    form = NewsletterForm()
    # Query the product from the database
    product = Product.query.get_or_404(product_id)
    
    # Fetch related products (optional)
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.product_id != product.product_id
    ).limit(3).all()
    
    return render_template(
        'user/productdetails.html',
        product=product,
        related_products=related_products,
        pagename=f'{product.product_name} | Rokeyla', form=form
    )
@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Form validation
        if not username or not email or not password or not confirm_password:
            flash('Please fill out all fields.')
            return render_template('user/register.html', pagename='Sign Up | Rokeyla')

        if password != confirm_password:
            flash('Passwords do not match.')
            return render_template('user/register.html', pagename='Sign Up | Rokeyla')

        # Check if username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            if existing_user.username == username:
                flash('Username already taken.')
            else:
                flash('An account with this email already exists.')
            return render_template('user/register.html', pagename='Sign Up | Rokeyla')

        # Hash the password
        password_hash = generate_password_hash(password)

        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )

        try:
            # Add user to the database
            db.session.add(new_user)
            db.session.commit()  # Commit to generate user_id

            # Add notification
            notification = Notification(
                admin_id=1,  # Adjust admin_id if necessary
                message=f'New user registered: {new_user.username}',
                link=url_for('admin_users', user_id=new_user.user_id),
                icon='fas fa-user-plus'
            )
            db.session.add(notification)

            # Send welcome message
            welcome_message = Message(
                sender_id=1,  # Default admin ID
                receiver_id=new_user.user_id,  # Newly created user's ID
                subject="Welcome to Rokeyla!",
                content="Welcome to Rokeyla! We're thrilled to have you on board. Explore our collections and find your style!"
            )
            db.session.add(welcome_message)

            # Commit both notification and message
            db.session.commit()

            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            print(f"Error: {e}")
            return render_template('user/register.html', pagename='Sign Up | Rokeyla')

    # Render registration form
    return render_template('user/register.html', pagename='Sign Up | Rokeyla')



@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = NewsletterForm()
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password')

        # Form validation
        if not email or not password:
            flash('Please fill out all fields.')
            return render_template('user/login.html', pagename='Sign In | Rokeyla')

        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            # Debug: Print the user's username
            print(f"User's username: {user.username}")

            # Set session variables
            session['logged_in'] = True
            session['user_id'] = user.user_id
            session['username'] = user.username  # Ensure 'username' is set here
            flash('You are now logged in.')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.')
            return render_template('user/login.html', pagename='Sign In | Rokeyla', form=form)
    else:
        # Render login form
        return render_template('user/login.html', pagename='Sign In | Rokeyla', form=form)


# New routes
@app.route('/dashboard/')
@login_required
def dashboard():
    user_id = session.get('user_id')
    user = User.query.options(joinedload(User.orders)).get(user_id)

    # Fetch total orders
    total_orders = len(user.orders)

    # Fetch new unread messages
    new_messages = Message.query.filter_by(receiver_id=user_id, is_read=False).count()
    unread_message_count = Message.query.filter_by(receiver_id=user_id, is_read=False).count()

    # Fetch wishlist items count
    wishlist_items = Wishlist.query.filter_by(user_id=user_id).count()

    # Fetch recent orders (limit to 5)
    recent_orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).limit(5).all()

    # Fetch recommended products (e.g., products from the same category as user's last order)
    recommended_products = Product.query.order_by(Product.created_at.desc()).limit(3).all()

    # Generate recent activity
    recent_activity = get_recent_activity(user_id)[:6]

    # Render the dashboard template with the fetched data
    return render_template(
        'user/dashboard.html',
        pagename='Dashboard | Rokeyla',
        user=user,
        total_orders=total_orders,
        unread_message_count=unread_message_count,
        new_messages=new_messages,
        wishlist_items=wishlist_items,
        recent_orders=recent_orders,
        recommended_products=recommended_products,
        recent_activity=recent_activity  # Pass recent_activity to template
    )


@app.route('/mark_notifications_read', methods=['POST'])
@login_required
def mark_notifications_read():
    user_id = session.get('user_id')
    
    # Mark all unread messages as read
    unread_messages = Message.query.filter_by(receiver_id=user_id, is_read=False).all()
    for message in unread_messages:
        message.is_read = True
    
    # Commit the changes
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error marking notifications as read: {e}")
        return jsonify({'status': 'error'}), 500

    return jsonify({'status': 'success'}), 200


def get_recent_activity(user_id):
    activities = []

    # Recent messages
    recent_messages = Message.query.filter_by(receiver_id=user_id).order_by(Message.created_at.desc()).limit(5).all()
    for message in recent_messages:
        activities.append({
            'icon': 'fas fa-envelope',
            'message': f"You received a message: {message.subject}",
            'time': message.created_at.strftime('%b %d, %Y at %I:%M %p'),
            'timestamp': message.created_at  # For sorting
        })

    # Recent orders
    recent_orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).limit(5).all()
    for order in recent_orders:
        activities.append({
            'icon': 'fas fa-shopping-cart',
            'message': f"You placed an order #{order.order_id} totaling ${order.total_amount}",
            'time': order.created_at.strftime('%b %d, %Y at %I:%M %p'),
            'timestamp': order.created_at
        })

    # Recent wishlist additions
    recent_wishlist = Wishlist.query.filter_by(user_id=user_id).order_by(Wishlist.created_at.desc()).limit(5).all()
    for wishlist_item in recent_wishlist:
        product = Product.query.get(wishlist_item.product_id)
        activities.append({
            'icon': 'fas fa-heart',
            'message': f"You added {product.product_name} to your wishlist",
            'time': wishlist_item.created_at.strftime('%b %d, %Y at %I:%M %p'),
            'timestamp': wishlist_item.created_at
        })

    # Additional activities can be added here

    # Sort activities by timestamp (most recent first)
    activities.sort(key=lambda x: x['timestamp'], reverse=True)

    return activities


# Define allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Configuration for file uploads

@app.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    recent_activity = get_recent_activity(user_id)
    unread_message_count = Message.query.filter_by(receiver_id=user_id, is_read=False).count()

    # List of countries
    
    # Full list of countries
    countries = [
        {'name': 'Afghanistan', 'iso2': 'AF'},
        {'name': 'Albania', 'iso2': 'AL'},
        {'name': 'Algeria', 'iso2': 'DZ'},
        {'name': 'Andorra', 'iso2': 'AD'},
        {'name': 'Angola', 'iso2': 'AO'},
        {'name': 'Antigua and Barbuda', 'iso2': 'AG'},
        {'name': 'Argentina', 'iso2': 'AR'},
        {'name': 'Armenia', 'iso2': 'AM'},
        {'name': 'Australia', 'iso2': 'AU'},
        {'name': 'Austria', 'iso2': 'AT'},
        {'name': 'Azerbaijan', 'iso2': 'AZ'},
        {'name': 'Bahamas', 'iso2': 'BS'},
        {'name': 'Bahrain', 'iso2': 'BH'},
        {'name': 'Bangladesh', 'iso2': 'BD'},
        {'name': 'Barbados', 'iso2': 'BB'},
        {'name': 'Belarus', 'iso2': 'BY'},
        {'name': 'Belgium', 'iso2': 'BE'},
        {'name': 'Belize', 'iso2': 'BZ'},
        {'name': 'Benin', 'iso2': 'BJ'},
        {'name': 'Bhutan', 'iso2': 'BT'},
        {'name': 'Bolivia', 'iso2': 'BO'},
        {'name': 'Bosnia and Herzegovina', 'iso2': 'BA'},
        {'name': 'Botswana', 'iso2': 'BW'},
        {'name': 'Brazil', 'iso2': 'BR'},
        {'name': 'Brunei', 'iso2': 'BN'},
        {'name': 'Bulgaria', 'iso2': 'BG'},
        {'name': 'Burkina Faso', 'iso2': 'BF'},
        {'name': 'Burundi', 'iso2': 'BI'},
        {'name': 'Cabo Verde', 'iso2': 'CV'},
        {'name': 'Cambodia', 'iso2': 'KH'},
        {'name': 'Cameroon', 'iso2': 'CM'},
        {'name': 'Canada', 'iso2': 'CA'},
        {'name': 'Central African Republic', 'iso2': 'CF'},
        {'name': 'Chad', 'iso2': 'TD'},
        {'name': 'Chile', 'iso2': 'CL'},
        {'name': 'China', 'iso2': 'CN'},
        {'name': 'Colombia', 'iso2': 'CO'},
        {'name': 'Comoros', 'iso2': 'KM'},
        {'name': 'Costa Rica', 'iso2': 'CR'},
        {'name': 'Croatia', 'iso2': 'HR'},
        {'name': 'Cuba', 'iso2': 'CU'},
        {'name': 'Cyprus', 'iso2': 'CY'},
        {'name': 'Czech Republic', 'iso2': 'CZ'},
        {'name': 'Denmark', 'iso2': 'DK'},
        {'name': 'Djibouti', 'iso2': 'DJ'},
        {'name': 'Dominica', 'iso2': 'DM'},
        {'name': 'Dominican Republic', 'iso2': 'DO'},
        {'name': 'Ecuador', 'iso2': 'EC'},
        {'name': 'Egypt', 'iso2': 'EG'},
        {'name': 'El Salvador', 'iso2': 'SV'},
        {'name': 'Equatorial Guinea', 'iso2': 'GQ'},
        {'name': 'Eritrea', 'iso2': 'ER'},
        {'name': 'Estonia', 'iso2': 'EE'},
        {'name': 'Eswatini', 'iso2': 'SZ'},
        {'name': 'Ethiopia', 'iso2': 'ET'},
        {'name': 'Fiji', 'iso2': 'FJ'},
        {'name': 'Finland', 'iso2': 'FI'},
        {'name': 'France', 'iso2': 'FR'},
        {'name': 'Gabon', 'iso2': 'GA'},
        {'name': 'Gambia', 'iso2': 'GM'},
        {'name': 'Georgia', 'iso2': 'GE'},
        {'name': 'Germany', 'iso2': 'DE'},
        {'name': 'Ghana', 'iso2': 'GH'},
        {'name': 'Greece', 'iso2': 'GR'},
        {'name': 'Grenada', 'iso2': 'GD'},
        {'name': 'Guatemala', 'iso2': 'GT'},
        {'name': 'Guinea', 'iso2': 'GN'},
        {'name': 'Guinea-Bissau', 'iso2': 'GW'},
        {'name': 'Guyana', 'iso2': 'GY'},
        {'name': 'Haiti', 'iso2': 'HT'},
        {'name': 'Honduras', 'iso2': 'HN'},
        {'name': 'Hungary', 'iso2': 'HU'},
        {'name': 'Iceland', 'iso2': 'IS'},
        {'name': 'India', 'iso2': 'IN'},
        {'name': 'Indonesia', 'iso2': 'ID'},
        {'name': 'Iran', 'iso2': 'IR'},
        {'name': 'Iraq', 'iso2': 'IQ'},
        {'name': 'Ireland', 'iso2': 'IE'},
        {'name': 'Israel', 'iso2': 'IL'},
        {'name': 'Italy', 'iso2': 'IT'},
        {'name': 'Jamaica', 'iso2': 'JM'},
        {'name': 'Japan', 'iso2': 'JP'},
        {'name': 'Jordan', 'iso2': 'JO'},
        {'name': 'Kazakhstan', 'iso2': 'KZ'},
        {'name': 'Kenya', 'iso2': 'KE'},
        {'name': 'Kiribati', 'iso2': 'KI'},
        {'name': 'Kuwait', 'iso2': 'KW'},
        {'name': 'Kyrgyzstan', 'iso2': 'KG'},
        {'name': 'Laos', 'iso2': 'LA'},
        {'name': 'Latvia', 'iso2': 'LV'},
        {'name': 'Lebanon', 'iso2': 'LB'},
        {'name': 'Lesotho', 'iso2': 'LS'},
        {'name': 'Liberia', 'iso2': 'LR'},
        {'name': 'Libya', 'iso2': 'LY'},
        {'name': 'Liechtenstein', 'iso2': 'LI'},
        {'name': 'Lithuania', 'iso2': 'LT'},
        {'name': 'Luxembourg', 'iso2': 'LU'},
        {'name': 'Madagascar', 'iso2': 'MG'},
        {'name': 'Malawi', 'iso2': 'MW'},
        {'name': 'Malaysia', 'iso2': 'MY'},
        {'name': 'Maldives', 'iso2': 'MV'},
        {'name': 'Mali', 'iso2': 'ML'},
        {'name': 'Malta', 'iso2': 'MT'},
        {'name': 'Marshall Islands', 'iso2': 'MH'},
        {'name': 'Mauritania', 'iso2': 'MR'},
        {'name': 'Mauritius', 'iso2': 'MU'},
        {'name': 'Mexico', 'iso2': 'MX'},
        {'name': 'Micronesia', 'iso2': 'FM'},
        {'name': 'Moldova', 'iso2': 'MD'},
        {'name': 'Monaco', 'iso2': 'MC'},
        {'name': 'Mongolia', 'iso2': 'MN'},
        {'name': 'Montenegro', 'iso2': 'ME'},
        {'name': 'Morocco', 'iso2': 'MA'},
        {'name': 'Mozambique', 'iso2': 'MZ'},
        {'name': 'Myanmar (Burma)', 'iso2': 'MM'},
        {'name': 'Namibia', 'iso2': 'NA'},
        {'name': 'Nauru', 'iso2': 'NR'},
        {'name': 'Nepal', 'iso2': 'NP'},
        {'name': 'Netherlands', 'iso2': 'NL'},
        {'name': 'New Zealand', 'iso2': 'NZ'},
        {'name': 'Nicaragua', 'iso2': 'NI'},
        {'name': 'Niger', 'iso2': 'NE'},
        {'name': 'Nigeria', 'iso2': 'NG'},
        {'name': 'North Korea', 'iso2': 'KP'},
        {'name': 'North Macedonia', 'iso2': 'MK'},
        {'name': 'Norway', 'iso2': 'NO'},
        {'name': 'Oman', 'iso2': 'OM'},
        {'name': 'Pakistan', 'iso2': 'PK'},
        {'name': 'Palau', 'iso2': 'PW'},
        {'name': 'Panama', 'iso2': 'PA'},
        {'name': 'Papua New Guinea', 'iso2': 'PG'},
        {'name': 'Paraguay', 'iso2': 'PY'},
        {'name': 'Peru', 'iso2': 'PE'},
        {'name': 'Philippines', 'iso2': 'PH'},
        {'name': 'Poland', 'iso2': 'PL'},
        {'name': 'Portugal', 'iso2': 'PT'},
        {'name': 'Qatar', 'iso2': 'QA'},
        {'name': 'Romania', 'iso2': 'RO'},
        {'name': 'Russia', 'iso2': 'RU'},
        {'name': 'Rwanda', 'iso2': 'RW'},
        {'name': 'Saint Kitts and Nevis', 'iso2': 'KN'},
        {'name': 'Saint Lucia', 'iso2': 'LC'},
        {'name': 'Saint Vincent and the Grenadines', 'iso2': 'VC'},
        {'name': 'Samoa', 'iso2': 'WS'},
        {'name': 'San Marino', 'iso2': 'SM'},
        {'name': 'Sao Tome and Principe', 'iso2': 'ST'},
        {'name': 'Saudi Arabia', 'iso2': 'SA'},
        {'name': 'Senegal', 'iso2': 'SN'},
        {'name': 'Serbia', 'iso2': 'RS'},
        {'name': 'Seychelles', 'iso2': 'SC'},
        {'name': 'Sierra Leone', 'iso2': 'SL'},
        {'name': 'Singapore', 'iso2': 'SG'},
        {'name': 'Slovakia', 'iso2': 'SK'},
        {'name': 'Slovenia', 'iso2': 'SI'},
        {'name': 'Solomon Islands', 'iso2': 'SB'},
        {'name': 'Somalia', 'iso2': 'SO'},
        {'name': 'South Africa', 'iso2': 'ZA'},
        {'name': 'South Korea', 'iso2': 'KR'},
        {'name': 'South Sudan', 'iso2': 'SS'},
        {'name': 'Spain', 'iso2': 'ES'},
        {'name': 'Sri Lanka', 'iso2': 'LK'},
        {'name': 'Sudan', 'iso2': 'SD'},
        {'name': 'Suriname', 'iso2': 'SR'},
        {'name': 'Sweden', 'iso2': 'SE'},
        {'name': 'Switzerland', 'iso2': 'CH'},
        {'name': 'Syria', 'iso2': 'SY'},
        {'name': 'Taiwan', 'iso2': 'TW'},
        {'name': 'Tajikistan', 'iso2': 'TJ'},
        {'name': 'Tanzania', 'iso2': 'TZ'},
        {'name': 'Thailand', 'iso2': 'TH'},
        {'name': 'Timor-Leste', 'iso2': 'TL'},
        {'name': 'Togo', 'iso2': 'TG'},
        {'name': 'Tonga', 'iso2': 'TO'},
        {'name': 'Trinidad and Tobago', 'iso2': 'TT'},
        {'name': 'Tunisia', 'iso2': 'TN'},
        {'name': 'Turkey', 'iso2': 'TR'},
        {'name': 'Turkmenistan', 'iso2': 'TM'},
        {'name': 'Tuvalu', 'iso2': 'TV'},
        {'name': 'Uganda', 'iso2': 'UG'},
        {'name': 'Ukraine', 'iso2': 'UA'},
        {'name': 'United Arab Emirates', 'iso2': 'AE'},
        {'name': 'United Kingdom', 'iso2': 'GB'},
        {'name': 'United States', 'iso2': 'US'},
        {'name': 'Uruguay', 'iso2': 'UY'},
        {'name': 'Uzbekistan', 'iso2': 'UZ'},
        {'name': 'Vanuatu', 'iso2': 'VU'},
        {'name': 'Vatican City', 'iso2': 'VA'},
        {'name': 'Venezuela', 'iso2': 'VE'},
        {'name': 'Vietnam', 'iso2': 'VN'},
        {'name': 'Yemen', 'iso2': 'YE'},
        {'name': 'Zambia', 'iso2': 'ZM'},
        {'name': 'Zimbabwe', 'iso2': 'ZW'},
    ]

    # Sort countries by name
    countries.sort(key=lambda x: x['name'])


    if request.method == 'POST':
        # Get form data
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        user.address = request.form.get('address')
        user.city = request.form.get('city')
        user.state = request.form.get('state')
        user.country = request.form.get('country')
        user.postal_code = request.form.get('postal_code')

        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"profile_{user.user_id}_{filename}"
                file_path = os.path.join(app.config['USER_PROFILE_PATH'], filename)
           
                # Ensure directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                # Save file to server
                file.save(file_path)

                # Construct relative path for database
                relative_path = f"uploads/{filename}"
                user.profile_pic = relative_path
            elif file.filename != '':
                flash('Invalid file type. Allowed types are png, jpg, jpeg, gif, webp.')
                return render_template('user/profile.html', user=user, countries=countries,
                                       unread_message_count=unread_message_count, recent_activity=recent_activity,
                                       pagename='Profile | Rokeyla')

        # Validate required fields
        if not user.email:
            flash('Email is required.')
            return render_template('user/profile.html', user=user, countries=countries,
                                   unread_message_count=unread_message_count, recent_activity=recent_activity,
                                   pagename='Profile | Rokeyla')

        # Update database
        try:
            db.session.commit()
            flash('Your profile has been updated.')
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile. Please try again.')
            return render_template('user/profile.html', user=user, countries=countries,
                                   unread_message_count=unread_message_count, recent_activity=recent_activity,
                                   pagename='Profile | Rokeyla')
    else:
        # Render profile template
        return render_template('user/profile.html', user=user, countries=countries,
                               unread_message_count=unread_message_count, recent_activity=recent_activity,
                               pagename='Profile | Rokeyla')



@app.route('/orders/')
@login_required
def orders():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    recent_activity = get_recent_activity(user_id)
    unread_message_count = Message.query.filter_by(receiver_id=user_id, is_read=False).count()

    # Fetch the user's orders
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()

    # Include product names for each order
    order_data = []
    for order in orders:
        products = [
            item.product.product_name
            for item in OrderItem.query.filter_by(order_id=order.order_id).join(Product).all()
        ]
        order_data.append({
            'order_id': order.order_id,
            'created_at': order.created_at.strftime('%Y-%m-%d'),
            'order_status': order.order_status,
            'total_amount': float(order.total_amount),
            'products': products  # Include product names as a list
        })

    # Calculate order summaries
    total_orders = len(orders)
    pending_orders = sum(1 for order in orders if order.order_status == 'Pending')
    shipped_orders = sum(1 for order in orders if order.order_status == 'Shipped')
    delivered_orders = sum(1 for order in orders if order.order_status == 'Delivered')

    return render_template(
        'user/orders.html',
        pagename='Your Orders | Rokeyla',
        user=user,
        orders=order_data,  # Pass the updated data structure
        total_orders=total_orders,
        pending_orders=pending_orders,
        shipped_orders=shipped_orders,
        delivered_orders=delivered_orders,
        unread_message_count=unread_message_count,
        recent_activity=recent_activity
    )
@app.route('/request_cancel/<int:order_id>', methods=['POST'])
@login_required
def request_cancel(order_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to request a cancellation.', 'danger')
        return redirect(url_for('login'))

    user = User.query.get_or_404(user_id)
    order = Order.query.filter_by(order_id=order_id, user_id=user_id).first_or_404()

    if order.order_status in ['Delivered', 'Cancelled']:
        flash("You cannot cancel this order.", "danger")
        return redirect(url_for('orders'))

    try:
        order.cancel_request = True
        db.session.commit()

        # Create a notification for the admin
        notification = Notification(
            admin_id=1,  # Adjust admin_id if necessary
            message=f'User {user.username} requested to cancel order #{order.order_id}',
            link=url_for('admin_order_details', order_id=order.order_id),
            icon='fas fa-ban',
            created_at=datetime.utcnow(),
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()

        flash("Your cancellation request has been sent to the admin.", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error requesting cancellation: {e}")  # Log the error for debugging
        flash("An error occurred while processing your request. Please try again.", "danger")
    return redirect(url_for('orders'))



@app.context_processor
def utility_processor():
    def product_in_wishlist(product_id):
        user_id = session.get('user_id')
        if not user_id:
            return False
        return Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first() is not None
    return dict(product_in_wishlist=product_in_wishlist)




@app.route('/settings/')
def settings():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    recent_activity = get_recent_activity(user_id)
    unread_message_count = Message.query.filter_by(receiver_id=user_id, is_read=False).count()
    return render_template('user/settings.html', pagename='Settings | Rokeyla', user=user,  unread_message_count=unread_message_count, recent_activity=recent_activity)



@app.route('/update_language', methods=['POST'])
@login_required
def update_language():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    new_language = request.form.get('language')
    if new_language:
        user.language = new_language
        db.session.commit()
        flash('Language preference updated.')
    else:
        flash('Please select a language.')
    return redirect(url_for('settings'))
    

@app.route('/update_theme', methods=['POST'])
@login_required
def update_theme():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    new_theme = request.form.get('theme')
    if new_theme in ['light', 'dark']:
        user.theme = new_theme
        db.session.commit()
        flash('Theme preference updated.')
    else:
        flash('Invalid theme selected.')
    return redirect(url_for('settings'))


@app.route('/connect_facebook')
@login_required  # Use your custom login check if not using Flask-Login
def connect_facebook():
    if not facebook.authorized:
        return redirect(url_for('facebook.login'))
    resp = facebook.get('/me?fields=id,name,email')
    if not resp.ok:
        flash('Failed to fetch user info from Facebook.')
        return redirect(url_for('settings'))
    user_info = resp.json()
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to connect accounts.')
        return redirect(url_for('login'))
    user = User.query.get_or_404(user_id)
    user.facebook_id = user_info['id']
    db.session.commit()
    flash('Facebook account connected.')
    return redirect(url_for('settings'))


@app.route('/connect_google')
@login_required  # Use your custom login check if not using Flask-Login
def connect_google():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get('/oauth2/v1/userinfo')
    if not resp.ok:
        flash('Failed to fetch user info from Google.')
        return redirect(url_for('settings'))
    user_info = resp.json()
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to connect accounts.')
        return redirect(url_for('login'))
    user = User.query.get_or_404(user_id)
    user.google_id = user_info['id']
    db.session.commit()
    flash('Google account connected.')
    return redirect(url_for('settings'))



@app.route('/disconnect_facebook', methods=['POST'])
@login_required  # Use your custom login check if not using Flask-Login
def disconnect_facebook():
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to disconnect accounts.')
        return redirect(url_for('login'))
    user = User.query.get_or_404(user_id)
    user.facebook_id = None
    db.session.commit()
    flash('Facebook account disconnected.')
    return redirect(url_for('settings'))



@app.route('/disconnect_google', methods=['POST'])
@login_required  # Use your custom login check if not using Flask-Login
def disconnect_google():
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to disconnect accounts.')
        return redirect(url_for('login'))
    user = User.query.get_or_404(user_id)
    user.google_id = None
    db.session.commit()
    flash('Google account disconnected.')
    return redirect(url_for('settings'))


@app.context_processor
def inject_user():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return {'user': user}
    return {}


@app.route('/logout/')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))


@app.route('/order/<int:order_id>/')
@login_required
def order_details(order_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('User not logged in.', 'danger')
        return redirect(url_for('login'))

    order = Order.query.filter_by(order_id=order_id, user_id=user_id).first_or_404()

    # Fetch order items with related product details
    order_items = OrderItem.query.filter_by(order_id=order.order_id).join(Product).all()
    recent_activity = get_recent_activity(user_id)
    unread_message_count = Message.query.filter_by(receiver_id=user_id, is_read=False).count()

    # Prepare data for the template
    order_data = {
        'order_id': order.order_id,
        'created_at': order.created_at.strftime('%B %d, %Y'),
        'order_status': order.order_status,
        'payment_method': order.payment_method,
        'shipping_address': order.shipping_address,
        'total_amount': float(order.total_amount),
        'order_items': []  # Changed from 'items' to 'order_items'
    }

    for item in order_items:
        product = item.product
        image_url = product.images[0].image_url if product.images else 'placeholder.jpg'
        order_data['order_items'].append({
            'product_name': product.product_name,
            'size': item.size,
            'color': item.color,
            'price': float(item.price),
            'quantity': item.quantity,
            'subtotal': float(item.price) * item.quantity,
            'image_url': image_url
        })

    return render_template('user/order_details.html', order=order_data,  unread_message_count=unread_message_count, recent_activity=recent_activity, pagename=f'Order #{order.order_id} | Rokeyla')


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('User ID not found in session.')
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(user_id)
    cart = user.cart

    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()

    selected_size = request.form.get('selected_size')
    selected_color = request.form.get('selected_color')
    quantity = int(request.form.get('quantity', 1))

    # Ensure size and color are selected
    if not selected_size or not selected_color:
        flash('Please select a size and color.', 'danger')
        return redirect(url_for('product_details', product_id=product_id))

    # Check if the item is already in the cart with the same size and color
    cart_item = CartItem.query.filter_by(
        cart_id=cart.cart_id,
        product_id=product_id,
        size=selected_size,
        color=selected_color
    ).first()

    if cart_item:
        # If item exists, increment quantity
        cart_item.quantity += quantity
    else:
        # Add new item to cart
        cart_item = CartItem(
            cart_id=cart.cart_id,
            product_id=product_id,
            quantity=quantity,
            size=selected_size,
            color=selected_color
        )
        db.session.add(cart_item)

    db.session.commit()
    flash('Item added to cart.', 'success')
    return redirect(url_for('cart'))

@app.route('/wishlist/')
@login_required
def wishlist():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    recent_activity = get_recent_activity(user_id)
    unread_message_count = Message.query.filter_by(receiver_id=user_id, is_read=False).count()
    # Fetch the user's wishlist items with associated product details
    wishlist_items = db.session.query(Wishlist, Product).join(Product, Wishlist.product_id == Product.product_id).filter(Wishlist.user_id == user_id).all()

    return render_template(
        'user/wishlist.html',
        pagename='Your Wishlist | Rokeyla',
        user=user,
        wishlist_items=wishlist_items,
        unread_message_count=unread_message_count,
        recent_activity=recent_activity
    )


@app.route('/add_to_wishlist', methods=['POST'])
@login_required
def add_to_wishlist():
    user_id = session.get('user_id')
    product_id = request.form.get('product_id')

    # Check if the product is already in the wishlist
    existing_item = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing_item:
        return jsonify({'message': 'Product is already in your wishlist.'}), 200

    # Add the product to the wishlist
    new_wishlist_item = Wishlist(user_id=user_id, product_id=product_id)
    db.session.add(new_wishlist_item)
    db.session.commit()

    return jsonify({'message': 'Product added to wishlist.'}), 200

@app.route('/remove_from_wishlist', methods=['POST'])
@login_required
def remove_from_wishlist():
    user_id = session.get('user_id')
    product_id = request.form.get('product_id')

    # Remove the product from the wishlist
    wishlist_item = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    if wishlist_item:
        db.session.delete(wishlist_item)
        db.session.commit()
        return jsonify({'message': 'Product removed from wishlist.'}), 200
    else:
        return jsonify({'message': 'Product not found in your wishlist.'}), 404




@app.route('/cart/', methods=['GET', 'POST'])
@login_required
def cart():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    form = NewsletterForm()
    # Fetch the user's cart
    cart = user.cart
    if not cart:
        # If the user doesn't have a cart, create one
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()

    # Fetch cart items for the user's cart
    cart_items = cart.cart_items

    # Calculate subtotal and total
    cart_subtotal = sum(item.product.price * item.quantity for item in cart_items)
    cart_total = cart_subtotal  # Initialize cart_total as cart_subtotal

    # Apply coupon if it exists
    coupon_code = session.get('coupon_code')
    discount = Decimal('0')  # Initialize discount as a Decimal
    if coupon_code:
        coupon = Coupon.query.filter_by(code=coupon_code).first()
        if coupon and coupon.is_valid():
            if coupon.discount_type == 'percentage':
                # Convert discount_value to Decimal using string conversion
                discount_value = Decimal(str(coupon.discount_value))
                discount = (discount_value / Decimal('100')) * cart_subtotal
                if coupon.max_discount:
                    # Convert max_discount to Decimal using string conversion
                    max_discount = Decimal(str(coupon.max_discount))
                    discount = min(discount, max_discount)
            elif coupon.discount_type == 'fixed':
                # Convert discount_value to Decimal using string conversion
                discount = Decimal(str(coupon.discount_value))
            cart_total -= discount  # Apply the discount
            cart_total = max(cart_total, Decimal('0'))  # Ensure the total isn't negative

    return render_template(
        'user/cart.html',
        cart_items=cart_items,
        cart_subtotal=cart_subtotal,
        cart_total=cart_total,
        discount=discount,
        coupon_code=coupon_code,form=form
    )


@app.route('/update_cart', methods=['POST'])
@login_required
def update_cart():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    cart = user.cart

    if not cart:
        flash('Your cart is empty.')
        return redirect(url_for('cart'))

    try:
        # Update quantities from form data
        for key, value in request.form.items():
            if key.startswith('quantity_'):
                # Extract product_id, size, and color from the input name
                _, product_id, size, color = key.split('_')
                product_id = int(product_id)
                size = size
                color = color
                quantity = int(value)

                # Update the quantity in the cart
                cart_item = CartItem.query.filter_by(
                    cart_id=cart.cart_id,
                    product_id=product_id,
                    size=size,
                    color=color
                ).first()
                if cart_item:
                    if quantity > 0:
                        cart_item.quantity = quantity
                    else:
                        db.session.delete(cart_item)
        db.session.commit()
        flash('Cart updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating the cart.', 'danger')
        print(f"Error: {e}")

    return redirect(url_for('cart'))


@app.route('/remove_from_cart/<int:product_id>/<string:size>/<string:color>', methods=['POST'])
@login_required
def remove_from_cart(product_id, size, color):
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    cart = user.cart

    if not cart:
        flash('Your cart is empty.')
        return redirect(url_for('cart'))

    try:
        # Find the cart item and remove it
        cart_item = CartItem.query.filter_by(
            cart_id=cart.cart_id,
            product_id=product_id,
            size=size,
            color=color
        ).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
            flash('Item removed from cart.', 'success')
        else:
            flash('Item not found in cart.', 'warning')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while removing the item.', 'danger')
        print(f"Error: {e}")

    return redirect(url_for('cart'))





    db.session.commit()
    flash('Item added to cart.')
    return redirect(url_for('product_detail', product_id=product_id))



@app.route('/apply_coupon', methods=['POST'])
@login_required
def apply_coupon():
    coupon_code = request.form.get('coupon_code')
    coupon = Coupon.query.filter_by(code=coupon_code).first()

    if not coupon or not coupon.is_valid():
        flash("Invalid or expired coupon.", "danger")
        return redirect(url_for('cart'))

    # Increment usage count
    coupon.increment_usage()
    db.session.commit()  # Persist changes to the database

    session['coupon_code'] = coupon.code
    flash(f"Coupon '{coupon.code}' applied successfully!", "success")
    return redirect(url_for('checkout'))


@app.context_processor
def inject_cart_item_count():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        if user and hasattr(user, 'cart') and user.cart:
            # Safely sum the quantities of items in the user's cart
            cart_item_count = sum(item.quantity for item in user.cart.cart_items)
            return {'cart_item_count': cart_item_count}
    return {'cart_item_count': 0}



@app.route('/messages')
@login_required
def messages():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    recent_activity = get_recent_activity(user_id)
    unread_message_count = Message.query.filter_by(receiver_id=user_id, is_read=False).count()

    
    # Fetch the user's messages
    messages = user.messages
    
    # Mark all unread messages as read
    for message in messages:
        if not message.is_read:
            message.is_read = True
    
    # Commit the changes to the database
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error marking messages as read: {e}")
        flash('An error occurred while updating the messages status.', 'danger')
    
    # Render the messages page
    return render_template('user/messages.html', messages=messages, unread_message_count=unread_message_count, recent_activity=recent_activity)


@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)

    # Fetch user data
    shipping_address = request.form.get('shipping_address')
    payment_method = request.form.get('payment_method')
    order_items_data = request.form.getlist('order_items')  # Assuming order items come as a list of dictionaries

    # Validate input
    if not shipping_address or not payment_method or not order_items_data:
        flash("Please provide all required details.", "danger")
        return redirect(url_for('cart'))

    try:
        # Calculate total amount
        order_total = 0
        order_items = []
        for item in order_items_data:
            product_id = item.get('product_id')
            quantity = int(item.get('quantity', 0))
            product = Product.query.get_or_404(product_id)

            if product.stock_quantity < quantity:
                flash(f"Not enough stock for {product.product_name}.", "danger")
                return redirect(url_for('cart'))

            price = float(product.price)
            order_total += price * quantity
            order_items.append({
                'product_id': product_id,
                'quantity': quantity,
                'price': price
            })

        # Create the new order
        new_order = Order(
            user_id=user_id,
            total_amount=order_total,
            shipping_address=shipping_address,
            payment_method=payment_method,
            order_status="Pending"
        )
        db.session.add(new_order)
        db.session.commit()

        # Add order items
        for item in order_items:
            new_order_item = OrderItem(
                order_id=new_order.order_id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                price=item['price']
            )
            db.session.add(new_order_item)

            # Reduce stock
            product = Product.query.get(item['product_id'])
            product.stock_quantity -= item['quantity']

        db.session.commit()

        # Create a notification for the admin
        notification = Notification(
            admin_id=1,  # Adjust admin_id if necessary
            message=f"New order placed: Order #{new_order.order_id} by {user.username}",
            link=url_for('admin_user_orders', order_id=new_order.order_id),
            icon='fas fa-shopping-cart',
            created_at=datetime.utcnow(),
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()

        flash('Order placed successfully!', 'success')
        return redirect(url_for('order_confirmation', order_id=new_order.order_id))

    except Exception as e:
        db.session.rollback()
        print(f"Error placing order: {e}")  # Log the error for debugging
        flash('An error occurred while placing your order. Please try again.', 'danger')
        return redirect(url_for('cart'))







from decimal import Decimal


@app.route('/checkout/', methods=['GET', 'POST'])
@login_required
def checkout():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    form = NewsletterForm()

    # Fetch the user's cart
    cart = user.cart
    if not cart or not cart.cart_items:
        flash('Your cart is empty.')
        return redirect(url_for('cart'))

    cart_items = cart.cart_items

    # Calculate subtotal and total
    cart_subtotal = sum(item.product.price * item.quantity for item in cart_items)
    cart_total = cart_subtotal

    # Apply coupon if exists
    coupon_code = session.get('coupon_code')
    discount = Decimal('0')
    if coupon_code:
        coupon = Coupon.query.filter_by(code=coupon_code).first()
        if coupon and coupon.is_valid():
            if coupon.discount_type == 'percentage':
                discount_value = Decimal(str(coupon.discount_value))
                discount = (discount_value / Decimal('100')) * cart_subtotal
                if coupon.max_discount:
                    max_discount = Decimal(str(coupon.max_discount))
                    discount = min(discount, max_discount)
            elif coupon.discount_type == 'fixed':
                discount = Decimal(str(coupon.discount_value))
            cart_total -= discount
            cart_total = max(cart_total, Decimal('0'))

    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        country = request.form.get('country')
        postal_code = request.form.get('postal_code')
        payment_method = request.form.get('payment_method')  # Get payment method from button

        # Validate required fields
        if not all([first_name, last_name, email, phone, address, city, state, country, postal_code, payment_method]):
            flash('Please fill out all required fields.', 'danger')
            return redirect(url_for('checkout'))

        # Create shipping address string
        shipping_address = f"{first_name} {last_name}\n{address}\n{city}, {state}, {postal_code}\n{country}"

        # Process the order
        try:
            # Calculate total amount
            order_total = cart_total

            # Create new order
            new_order = Order(
                user_id=user_id,
                total_amount=order_total,
                shipping_address=shipping_address,
                payment_method=payment_method,
                order_status=OrderStatus.PENDING.value
            )
            db.session.add(new_order)
            db.session.commit()

            # Add order items and adjust stock at product level
            for item in cart_items:
                # Check if product has sufficient stock
                if item.product.stock_quantity < item.quantity:
                    flash(f"Insufficient stock for {item.product.product_name}. Available: {item.product.stock_quantity}, Requested: {item.quantity}", 'danger')
                    return redirect(url_for('cart'))

                # Reduce stock
                item.product.stock_quantity -= item.quantity

                # Create order item
                new_order_item = OrderItem(
                    order_id=new_order.order_id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=item.product.price,
                    size=item.size,
                    color=item.color
                )
                db.session.add(new_order_item)

            # Clear the cart
            CartItem.query.filter_by(cart_id=cart.cart_id).delete()

            # Remove coupon code from session
            session.pop('coupon_code', None)

            db.session.commit()

            # Create a notification for the admin
            notification = Notification(
                admin_id=1,  # Adjust admin_id if necessary
                message=f'New order placed: Order #{new_order.order_id}',
                link=url_for('admin_user_orders', order_id=new_order.order_id),
                icon='fas fa-shopping-cart'
            )
            db.session.add(notification)
            db.session.commit()

            # Redirect to the appropriate payment gateway
            if payment_method == 'Paystack':
                return redirect(url_for('initiate_paystack_payment', order_id=new_order.order_id))
            elif payment_method == 'Stripe':
                return redirect(url_for('create_checkout_session', order_id=new_order.order_id))
            else:
                flash('Unsupported payment method selected.', 'danger')
                return redirect(url_for('checkout'))

        except Exception as e:
            db.session.rollback()
            print(f"Error placing order: {e}")
            flash('An error occurred while placing your order. Please try again.', 'danger')
            return redirect(url_for('checkout'))

    else:
        # Pre-fill the billing details with user's profile data
        billing_details = {
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'email': user.email or '',
            'phone': user.phone or '',
            'address': user.address or '',
            'city': user.city or '',
            'state': user.state or '',
            'country': user.country or '',
            'postal_code': user.postal_code or '',
        }

        # Full list of countries (ISO2 codes and names)
        countries = [
            {'name': 'Afghanistan', 'iso2': 'AF'},
            {'name': 'Albania', 'iso2': 'AL'},
            {'name': 'Algeria', 'iso2': 'DZ'},
            {'name': 'Andorra', 'iso2': 'AD'},
            {'name': 'Angola', 'iso2': 'AO'},
            {'name': 'Antigua and Barbuda', 'iso2': 'AG'},
            {'name': 'Argentina', 'iso2': 'AR'},
            {'name': 'Armenia', 'iso2': 'AM'},
            {'name': 'Australia', 'iso2': 'AU'},
            {'name': 'Austria', 'iso2': 'AT'},
            {'name': 'Azerbaijan', 'iso2': 'AZ'},
            {'name': 'Bahamas', 'iso2': 'BS'},
            {'name': 'Bahrain', 'iso2': 'BH'},
            {'name': 'Bangladesh', 'iso2': 'BD'},
            {'name': 'Barbados', 'iso2': 'BB'},
            {'name': 'Belarus', 'iso2': 'BY'},
            {'name': 'Belgium', 'iso2': 'BE'},
            {'name': 'Belize', 'iso2': 'BZ'},
            {'name': 'Benin', 'iso2': 'BJ'},
            {'name': 'Bhutan', 'iso2': 'BT'},
            {'name': 'Bolivia', 'iso2': 'BO'},
            {'name': 'Bosnia and Herzegovina', 'iso2': 'BA'},
            {'name': 'Botswana', 'iso2': 'BW'},
            {'name': 'Brazil', 'iso2': 'BR'},
            {'name': 'Brunei', 'iso2': 'BN'},
            {'name': 'Bulgaria', 'iso2': 'BG'},
            {'name': 'Burkina Faso', 'iso2': 'BF'},
            {'name': 'Burundi', 'iso2': 'BI'},
            {'name': 'Cabo Verde', 'iso2': 'CV'},
            {'name': 'Cambodia', 'iso2': 'KH'},
            {'name': 'Cameroon', 'iso2': 'CM'},
            {'name': 'Canada', 'iso2': 'CA'},
            {'name': 'Central African Republic', 'iso2': 'CF'},
            {'name': 'Chad', 'iso2': 'TD'},
            {'name': 'Chile', 'iso2': 'CL'},
            {'name': 'China', 'iso2': 'CN'},
            {'name': 'Colombia', 'iso2': 'CO'},
            {'name': 'Comoros', 'iso2': 'KM'},
            {'name': 'Costa Rica', 'iso2': 'CR'},
            {'name': 'Croatia', 'iso2': 'HR'},
            {'name': 'Cuba', 'iso2': 'CU'},
            {'name': 'Cyprus', 'iso2': 'CY'},
            {'name': 'Czech Republic', 'iso2': 'CZ'},
            {'name': 'Denmark', 'iso2': 'DK'},
            {'name': 'Djibouti', 'iso2': 'DJ'},
            {'name': 'Dominica', 'iso2': 'DM'},
            {'name': 'Dominican Republic', 'iso2': 'DO'},
            {'name': 'Ecuador', 'iso2': 'EC'},
            {'name': 'Egypt', 'iso2': 'EG'},
            {'name': 'El Salvador', 'iso2': 'SV'},
            {'name': 'Equatorial Guinea', 'iso2': 'GQ'},
            {'name': 'Eritrea', 'iso2': 'ER'},
            {'name': 'Estonia', 'iso2': 'EE'},
            {'name': 'Eswatini', 'iso2': 'SZ'},
            {'name': 'Ethiopia', 'iso2': 'ET'},
            {'name': 'Fiji', 'iso2': 'FJ'},
            {'name': 'Finland', 'iso2': 'FI'},
            {'name': 'France', 'iso2': 'FR'},
            {'name': 'Gabon', 'iso2': 'GA'},
            {'name': 'Gambia', 'iso2': 'GM'},
            {'name': 'Georgia', 'iso2': 'GE'},
            {'name': 'Germany', 'iso2': 'DE'},
            {'name': 'Ghana', 'iso2': 'GH'},
            {'name': 'Greece', 'iso2': 'GR'},
            {'name': 'Grenada', 'iso2': 'GD'},
            {'name': 'Guatemala', 'iso2': 'GT'},
            {'name': 'Guinea', 'iso2': 'GN'},
            {'name': 'Guinea-Bissau', 'iso2': 'GW'},
            {'name': 'Guyana', 'iso2': 'GY'},
            {'name': 'Haiti', 'iso2': 'HT'},
            {'name': 'Honduras', 'iso2': 'HN'},
            {'name': 'Hungary', 'iso2': 'HU'},
            {'name': 'Iceland', 'iso2': 'IS'},
            {'name': 'India', 'iso2': 'IN'},
            {'name': 'Indonesia', 'iso2': 'ID'},
            {'name': 'Iran', 'iso2': 'IR'},
            {'name': 'Iraq', 'iso2': 'IQ'},
            {'name': 'Ireland', 'iso2': 'IE'},
            {'name': 'Israel', 'iso2': 'IL'},
            {'name': 'Italy', 'iso2': 'IT'},
            {'name': 'Jamaica', 'iso2': 'JM'},
            {'name': 'Japan', 'iso2': 'JP'},
            {'name': 'Jordan', 'iso2': 'JO'},
            {'name': 'Kazakhstan', 'iso2': 'KZ'},
            {'name': 'Kenya', 'iso2': 'KE'},
            {'name': 'Kiribati', 'iso2': 'KI'},
            {'name': 'Kuwait', 'iso2': 'KW'},
            {'name': 'Kyrgyzstan', 'iso2': 'KG'},
            {'name': 'Laos', 'iso2': 'LA'},
            {'name': 'Latvia', 'iso2': 'LV'},
            {'name': 'Lebanon', 'iso2': 'LB'},
            {'name': 'Lesotho', 'iso2': 'LS'},
            {'name': 'Liberia', 'iso2': 'LR'},
            {'name': 'Libya', 'iso2': 'LY'},
            {'name': 'Liechtenstein', 'iso2': 'LI'},
            {'name': 'Lithuania', 'iso2': 'LT'},
            {'name': 'Luxembourg', 'iso2': 'LU'},
            {'name': 'Madagascar', 'iso2': 'MG'},
            {'name': 'Malawi', 'iso2': 'MW'},
            {'name': 'Malaysia', 'iso2': 'MY'},
            {'name': 'Maldives', 'iso2': 'MV'},
            {'name': 'Mali', 'iso2': 'ML'},
            {'name': 'Malta', 'iso2': 'MT'},
            {'name': 'Marshall Islands', 'iso2': 'MH'},
            {'name': 'Mauritania', 'iso2': 'MR'},
            {'name': 'Mauritius', 'iso2': 'MU'},
            {'name': 'Mexico', 'iso2': 'MX'},
            {'name': 'Micronesia', 'iso2': 'FM'},
            {'name': 'Moldova', 'iso2': 'MD'},
            {'name': 'Monaco', 'iso2': 'MC'},
            {'name': 'Mongolia', 'iso2': 'MN'},
            {'name': 'Montenegro', 'iso2': 'ME'},
            {'name': 'Morocco', 'iso2': 'MA'},
            {'name': 'Mozambique', 'iso2': 'MZ'},
            {'name': 'Myanmar (Burma)', 'iso2': 'MM'},
            {'name': 'Namibia', 'iso2': 'NA'},
            {'name': 'Nauru', 'iso2': 'NR'},
            {'name': 'Nepal', 'iso2': 'NP'},
            {'name': 'Netherlands', 'iso2': 'NL'},
            {'name': 'New Zealand', 'iso2': 'NZ'},
            {'name': 'Nicaragua', 'iso2': 'NI'},
            {'name': 'Niger', 'iso2': 'NE'},
            {'name': 'Nigeria', 'iso2': 'NG'},
            {'name': 'North Korea', 'iso2': 'KP'},
            {'name': 'North Macedonia', 'iso2': 'MK'},
            {'name': 'Norway', 'iso2': 'NO'},
            {'name': 'Oman', 'iso2': 'OM'},
            {'name': 'Pakistan', 'iso2': 'PK'},
            {'name': 'Palau', 'iso2': 'PW'},
            {'name': 'Panama', 'iso2': 'PA'},
            {'name': 'Papua New Guinea', 'iso2': 'PG'},
            {'name': 'Paraguay', 'iso2': 'PY'},
            {'name': 'Peru', 'iso2': 'PE'},
            {'name': 'Philippines', 'iso2': 'PH'},
            {'name': 'Poland', 'iso2': 'PL'},
            {'name': 'Portugal', 'iso2': 'PT'},
            {'name': 'Qatar', 'iso2': 'QA'},
            {'name': 'Romania', 'iso2': 'RO'},
            {'name': 'Russia', 'iso2': 'RU'},
            {'name': 'Rwanda', 'iso2': 'RW'},
            {'name': 'Saint Kitts and Nevis', 'iso2': 'KN'},
            {'name': 'Saint Lucia', 'iso2': 'LC'},
            {'name': 'Saint Vincent and the Grenadines', 'iso2': 'VC'},
            {'name': 'Samoa', 'iso2': 'WS'},
            {'name': 'San Marino', 'iso2': 'SM'},
            {'name': 'Sao Tome and Principe', 'iso2': 'ST'},
            {'name': 'Saudi Arabia', 'iso2': 'SA'},
            {'name': 'Senegal', 'iso2': 'SN'},
            {'name': 'Serbia', 'iso2': 'RS'},
            {'name': 'Seychelles', 'iso2': 'SC'},
            {'name': 'Sierra Leone', 'iso2': 'SL'},
            {'name': 'Singapore', 'iso2': 'SG'},
            {'name': 'Slovakia', 'iso2': 'SK'},
            {'name': 'Slovenia', 'iso2': 'SI'},
            {'name': 'Solomon Islands', 'iso2': 'SB'},
            {'name': 'Somalia', 'iso2': 'SO'},
            {'name': 'South Africa', 'iso2': 'ZA'},
            {'name': 'South Korea', 'iso2': 'KR'},
            {'name': 'South Sudan', 'iso2': 'SS'},
            {'name': 'Spain', 'iso2': 'ES'},
            {'name': 'Sri Lanka', 'iso2': 'LK'},
            {'name': 'Sudan', 'iso2': 'SD'},
            {'name': 'Suriname', 'iso2': 'SR'},
            {'name': 'Sweden', 'iso2': 'SE'},
            {'name': 'Switzerland', 'iso2': 'CH'},
            {'name': 'Syria', 'iso2': 'SY'},
            {'name': 'Taiwan', 'iso2': 'TW'},
            {'name': 'Tajikistan', 'iso2': 'TJ'},
            {'name': 'Tanzania', 'iso2': 'TZ'},
            {'name': 'Thailand', 'iso2': 'TH'},
            {'name': 'Timor-Leste', 'iso2': 'TL'},
            {'name': 'Togo', 'iso2': 'TG'},
            {'name': 'Tonga', 'iso2': 'TO'},
            {'name': 'Trinidad and Tobago', 'iso2': 'TT'},
            {'name': 'Tunisia', 'iso2': 'TN'},
            {'name': 'Turkey', 'iso2': 'TR'},
            {'name': 'Turkmenistan', 'iso2': 'TM'},
            {'name': 'Tuvalu', 'iso2': 'TV'},
            {'name': 'Uganda', 'iso2': 'UG'},
            {'name': 'Ukraine', 'iso2': 'UA'},
            {'name': 'United Arab Emirates', 'iso2': 'AE'},
            {'name': 'United Kingdom', 'iso2': 'GB'},
            {'name': 'United States', 'iso2': 'US'},
            {'name': 'Uruguay', 'iso2': 'UY'},
            {'name': 'Uzbekistan', 'iso2': 'UZ'},
            {'name': 'Vanuatu', 'iso2': 'VU'},
            {'name': 'Vatican City', 'iso2': 'VA'},
            {'name': 'Venezuela', 'iso2': 'VE'},
            {'name': 'Vietnam', 'iso2': 'VN'},
            {'name': 'Yemen', 'iso2': 'YE'},
            {'name': 'Zambia', 'iso2': 'ZM'},
            {'name': 'Zimbabwe', 'iso2': 'ZW'},
        ]

        # Sort countries by name
        countries.sort(key=lambda x: x['name'])

        return render_template(
            'user/checkout.html',
            cart_items=cart_items,
            cart_subtotal=cart_subtotal,
            cart_total=cart_total,
            discount=discount,
            billing_details=billing_details,
            coupon_code=coupon_code,
            countries=countries,
            pagename='Checkout | Rokeyla',
            form=form
        )


@app.route('/subscribe', methods=['POST'])
def subscribe():

    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    form = NewsletterForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        # Check if email is already subscribed
        if NewsletterSubscriber.query.filter_by(email=email).first():
            flash('You are already subscribed!', 'info')
        else:
            new_subscriber = NewsletterSubscriber(email=email)
            db.session.add(new_subscriber)
            db.session.commit()
            flash('Thank you for subscribing!', 'success')
    else:
        flash('Please enter a valid email address.', 'error')
    return redirect(url_for('index'))



@app.context_processor
def inject_footer_categories():
    categories = Category.query.all()
    footer_categories = random.sample(categories, min(len(categories), 4))
    return dict(footer_categories=footer_categories)
@app.route('/create-checkout-session', methods=['POST'])

@app.route('/create-checkout-session/<int:order_id>', methods=['GET', 'POST'])
@login_required
def create_checkout_session(order_id):
    """Route to create a Stripe checkout session"""
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    order = Order.query.get_or_404(order_id)

    # Prepare line items based on the order
    order_items = OrderItem.query.filter_by(order_id=order_id).all()
    line_items = []
    for item in order_items:
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.product.product_name,
                    'description': item.product.description,
                },
                'unit_amount': int(item.price * 100),  # Convert dollars to cents
            },
            'quantity': item.quantity,
        })

    try:
        # Create Stripe Checkout Session
        stripe_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('payment_success', order_id=order_id, _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('payment_cancel', _external=True),
        )
        return redirect(stripe_session.url, code=303)
    except Exception as e:
        flash('An error occurred while creating the payment session. Please try again.', 'danger')
        print(f"Stripe error: {e}")
        return redirect(url_for('checkout'))



@app.route('/payment-success/<int:order_id>', methods=['GET'])
@login_required
def payment_success(order_id):
    session_id = request.args.get('session_id')
    if not session_id:
        flash('Invalid payment session.', 'danger')
        return redirect(url_for('checkout'))

    # Retrieve Stripe session
    stripe_session = stripe.checkout.Session.retrieve(session_id)

    if stripe_session.payment_status == 'paid':
        try:
            # Update order status to 'Paid'
            order = Order.query.get_or_404(order_id)
            order.order_status = 'Paid'
            db.session.commit()

            flash('Payment successful! Your order has been placed.', 'success')
            return redirect(url_for('order_confirmation', order_id=order_id))
        except Exception as e:
            db.session.rollback()
            print(f"Error processing order: {e}")
            flash('An error occurred while processing your order.', 'danger')
            return redirect(url_for('cart'))
    else:
        flash('Payment not successful.', 'danger')
        return redirect(url_for('cart'))



@app.route('/payment-cancel', methods=['GET'])
@login_required
def payment_cancel():
    flash('Payment was canceled. Your cart is still available.', 'warning')
    return redirect(url_for('cart'))



# Paystack Initialization
PAYSTACK_SECRET_KEY = app.config['PAYSTACK_SECRET_KEY']
PAYSTACK_CALLBACK_URL = app.config['PAYSTACK_CALLBACK_URL']

@app.route('/checkout/paystack/<int:order_id>', methods=['GET'])
@login_required
def initiate_paystack_payment(order_id):
    """Route to initiate payment with Paystack"""
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    order = Order.query.get_or_404(order_id)

    # Calculate total amount in kobo (Paystack uses kobo for currency)
    total_amount = int(order.total_amount * 100)

    # Create a payment session on Paystack
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "email": user.email,
        "amount": total_amount,
        "callback_url": PAYSTACK_CALLBACK_URL,
    }

    try:
        response = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
        result = response.json()

        if result.get("status"):
            authorization_url = result["data"]["authorization_url"]

            # Save payment reference for verification later
            session["paystack_reference"] = result["data"]["reference"]
            session["order_id"] = order_id  # Save order ID in session
            return redirect(authorization_url)

        flash("Unable to initiate payment. Please try again.", "danger")
        return redirect(url_for('checkout'))
    except Exception as e:
        flash(f"Payment initiation failed: {str(e)}", "danger")
        return redirect(url_for('checkout'))



@app.route('/payment/verify', methods=['GET'])
@login_required
def verify_paystack_payment():
    """Route to verify Paystack payment"""
    reference = request.args.get("reference")
    if not reference:
        flash("Payment reference is missing.", "danger")
        return redirect(url_for('checkout'))

    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}

    try:
        response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
        result = response.json()

        if result.get("status") and result["data"]["status"] == "success":
            # Payment was successful
            flash("Payment was successful!", "success")

            # Update order status to 'Paid'
            order_id = session.get('order_id')
            order = Order.query.get_or_404(order_id)
            order.order_status = 'Paid'
            db.session.commit()

            # Clear session data
            session.pop('paystack_reference', None)
            session.pop('order_id', None)

            return redirect(url_for('order_confirmation', order_id=order_id))
        else:
            flash("Payment verification failed. Please try again.", "danger")
            return redirect(url_for('checkout'))
    except Exception as e:
        flash(f"Payment verification failed: {str(e)}", "danger")
        return redirect(url_for('checkout'))




@app.route('/submit_checkout', methods=['POST'])
@login_required
def submit_checkout():
    # Get the payment method from the form
    payment_method = request.form.get('payment_method')

    if not payment_method:
        flash('Payment method not found. Please select a payment method.', 'danger')
        return redirect(url_for('checkout'))

    # Redirect to the appropriate payment gateway
    if payment_method == 'Paystack':
        return redirect(url_for('initiate_paystack_payment'))
    elif payment_method == 'Stripe':
        return redirect(url_for('create_checkout_session'))
    else:
        flash('Unsupported payment method selected.', 'danger')
        return redirect(url_for('checkout'))



@app.route('/order_confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    order = Order.query.filter_by(order_id=order_id, user_id=user_id).first_or_404()
    order_items = OrderItem.query.filter_by(order_id=order_id).all()
    return render_template('user/order_confirmation.html', order=order, order_items=order_items)