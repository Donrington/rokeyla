from PIL import Image
import json, os
import io
from os.path import basename
import random
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
import pytz

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in as an admin.')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# Admin login route
@app.route('/admin/login/', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        # Authenticate admin
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session['admin_logged_in'] = True
            session['admin_id'] = admin.admin_id
            flash('Admin logged in successfully.')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.')

    return render_template('admin/login.html')

# Admin logout route
@app.route('/admin/logout/')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    flash('Admin logged out.')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_login_required
def admin_dashboard():
    admin = Admin.query.get(session['admin_id'])
    if not admin:
        flash('Admin not found.', 'danger')
        return redirect(url_for('login'))

    # Fetch metrics
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_sales = db.session.query(func.sum(Order.total_amount)).scalar() or 0

    # Fetch notifications
    unread_notifications = Notification.query.filter_by(admin_id=admin.admin_id, is_read=False).order_by(Notification.created_at.desc()).all()
    unread_notifications_count = len(unread_notifications)
    recent_notifications = Notification.query.filter_by(admin_id=admin.admin_id).order_by(Notification.created_at.desc()).limit(10).all()

    # Fetch recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()

    # Fetch recent products
    products = Product.query.order_by(Product.created_at.desc()).limit(5).all()

    # Sales data for the last 6 months

    # Sales data for the last 6 months
    today = datetime.today()
    six_months_ago = today - timedelta(days=180)

    sales_data = db.session.query(
        func.to_char(Order.created_at, 'YYYY-MM').label('month'),
        func.sum(Order.total_amount).label('total_sales')
    ).filter(Order.created_at >= six_months_ago).group_by(func.to_char(Order.created_at, 'YYYY-MM')).order_by(func.to_char(Order.created_at, 'YYYY-MM')).all()

    sales_labels = [datetime.strptime(row.month, '%Y-%m').strftime('%B %Y') for row in sales_data]
    sales_amounts = [float(row.total_sales) for row in sales_data]
  

    sales_labels = [datetime.strptime(row.month, '%Y-%m').strftime('%B %Y') for row in sales_data]
    sales_amounts = [float(row.total_sales) for row in sales_data]

    # Fetch user activities
    user_activities = Activity.query.filter(Activity.user_id.isnot(None)).order_by(Activity.time.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        pagename="Admin Dashboard",
        admin=admin,
        total_users=total_users,
        total_products=total_products,
        total_orders=total_orders,
        total_sales=total_sales,
        recent_orders=recent_orders,
        products=products,
        sales_labels=sales_labels,
        sales_amounts=sales_amounts,
        recent_activity=user_activities,  # Pass user activities
        unread_notifications=unread_notifications,
        unread_notifications_count=unread_notifications_count,
        recent_notifications=recent_notifications,
    )


@app.route('/admin/products/create/', methods=['GET', 'POST'])
@admin_login_required
def create_product():
    errors = {}
    categories = Category.query.filter_by(parent_id=None).all()


    # Define 'admin' directly by querying the database
    admin_id = session.get('admin_id')  # Assuming 'admin_id' is stored in the session on login
    admin = Admin.query.get(admin_id) if admin_id else None
    unread_notifications = Notification.query.filter_by(admin_id=admin.admin_id, is_read=False).order_by(Notification.created_at.desc()).all()
    unread_notifications_count = len(unread_notifications)

    recent_notifications = Notification.query.filter_by(admin_id=admin.admin_id).order_by(Notification.created_at.desc()).limit(10).all()

    if not admin:
        flash('Admin not found. Please log in as an admin.', 'danger')
        return redirect(url_for('admin_login'))  # Redirect to admin login if admin not found
    
    if request.method == 'POST':
        # Retrieve form data
        is_featured = True if request.form.get('is_featured') == 'on' else False
        product_name = request.form.get('product_name')
        description = request.form.get('description')
        price = request.form.get('price')
        stock_quantity = request.form.get('stock_quantity')
        sizes = request.form.getlist('sizes')  # Using getlist for multiple sizes
        colors = request.form.getlist('colors')  # Using getlist for multiple colors
        category_id = request.form.get('category_id')
        images = request.files.getlist('images')  # Retrieve list of uploaded images

        # Validation
        if not product_name:
            errors['product_name'] = 'Product name is required.'
        if not price:
            errors['price'] = 'Price is required.'
        else:
            try:
                price = float(price)
            except ValueError:
                errors['price'] = 'Price must be a number.'
        if not stock_quantity:
            errors['stock_quantity'] = 'Stock quantity is required.'
        else:
            try:
                stock_quantity = int(stock_quantity)
            except ValueError:
                errors['stock_quantity'] = 'Stock quantity must be an integer.'
        if not category_id:
            errors['category_id'] = 'Category is required.'
        else:
            category = Category.query.get(category_id)
            if not category:
                errors['category_id'] = 'Selected category does not exist.'

        # If there are validation errors, re-render the form with errors
        if errors:
            return render_template(
                'admin/create_product.html',
                categories=categories,
                errors=errors,
                request=request,
                unread_notifications=unread_notifications,
                unread_notifications_count=unread_notifications_count,
                recent_notifications=recent_notifications,
                admin=admin  # Pass 'admin' to the template
            )

        # Create new product
        product = Product(
            product_name=product_name,
            description=description,
            price=price,
            stock_quantity=stock_quantity,
            sizes=','.join(sizes),
            colors=','.join(colors),
            category_id=category_id,
            is_featured=is_featured
        )

        try:
            # Add product to the session and commit to generate product_id
            db.session.add(product)
            db.session.commit()

            # Handle image uploads
            # Ensure the upload folder exists
            product_folder = app.config['PRODUCT_UPLOADER']
            if not os.path.exists(product_folder):
                os.makedirs(product_folder)

            # Handle image uploads
            if images and images[0].filename != '':
                for image_file in images:
                    filename = secure_filename(image_file.filename)
                    
                    # Save the file to the file system
                    image_save_path = os.path.join(product_folder, filename)
                    image_file.save(image_save_path)

                    # Construct the image URL using forward slashes
                    image_url = f"products/{filename}"

                    # Alternatively, ensure any backslashes are replaced with forward slashes
                    image_url = os.path.join('products', filename).replace('\\', '/')

                    # Create ProductImage
                    product_image = ProductImage(
                        product_id=product.product_id,
                        image_url=image_url
                    )
                    db.session.add(product_image)
                db.session.commit()

            flash('Product created successfully.', 'success')
            return redirect(url_for('admin_products'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the product.', 'danger')
            print(f"Error: {e}")
            return render_template(
                'admin/create_products.html',  # Ensure the template name is correct
                categories=categories,
                errors=errors,
                request=request,
                unread_notifications=unread_notifications,
                unread_notifications_count=unread_notifications_count,
                recent_notifications=recent_notifications,
                admin=admin  # Pass 'admin' to the template
            )

    # For GET request, ensure 'errors', 'request', and 'admin' are passed to the template
    return render_template(
        'admin/create_products.html',  # Ensure the template name is correct
        categories=categories,
        errors=errors,
        request=request,
        unread_notifications=unread_notifications,
        unread_notifications_count=unread_notifications_count,
        recent_notifications=recent_notifications,
        admin=admin  # Pass 'admin' to the template
    )


def seed_categories():
    # Clear existing categories (optional, use with caution)
    # Category.query.delete()
    # db.session.commit()

    # Create parent categories
    men_category = Category(category_name='Men', description='Men\'s category')
    women_category = Category(category_name='Women', description='Women\'s category')
    accessories_category = Category(category_name='Accessories', description='Accessories category')
    db.session.add(men_category)
    db.session.add(women_category)
    db.session.add(accessories_category)
    db.session.commit()

    # Categories for Men
    men_subcategories = [
        {'category_name': 'Shoes', 'description': 'Men\'s Shoes'},
         {'category_name': 'Sandals', 'description': 'Men\'s Sandals'},
        {'category_name': 'Shirts', 'description': 'Men\'s Shirts'},
        {'category_name': 'T-Shirts', 'description': 'Men\'s T-Shirts'},
        {'category_name': 'Sweaters', 'description': 'Men\'s Sweaters'},
        {'category_name': 'Jackets', 'description': 'Men\'s Jackets'},
    ]

    # Categories for Women
    women_subcategories = [
        {'category_name': 'Dresses', 'description': 'Women\'s Dresses'},
        {'category_name': 'Tops', 'description': 'Women\'s Tops'},
        {'category_name': 'Skirts', 'description': 'Women\'s Skirts'},
        {'category_name': 'Shoes', 'description': 'Women\'s Shoes'},
        {'category_name': 'Accessories', 'description': 'Women\'s Accessories'},
    ]

    accessories_subcategories = [
        {'category_name': 'Bags', 'description': 'Bags'},
        {'category_name': 'Belts', 'description': 'Belts'},
        {'category_name': 'Hats', 'description': 'Hats'},
        {'category_name': 'Wallets', 'description': 'Wallets'},
        {'category_name': 'Watches', 'description': 'Watches'},
        {'category_name': 'Bracelets', 'description': 'Bracelets'},
    ]

    # Add subcategories for Men
    for subcat in men_subcategories:
        category = Category(
            category_name=subcat['category_name'],
            description=subcat['description'],
            parent=men_category
        )
        db.session.add(category)

    # Add subcategories for Women
    for subcat in women_subcategories:
        category = Category(
            category_name=subcat['category_name'],
            description=subcat['description'],
            parent=women_category
        )
        db.session.add(category)

    for subcat in accessories_subcategories:
        category = Category(
            category_name=subcat['category_name'],
            description=subcat['description'],
            parent=accessories_category
        )
        db.session.add(category)


    db.session.commit()
    print('Categories seeded successfully.')


@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_login_required
def edit_product(product_id):
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id)
    if not admin:
        flash('Admin not found. Please log in as an admin.', 'danger')
        return redirect(url_for('admin_login'))

    product = Product.query.get_or_404(product_id)
    categories = Category.query.filter_by(parent_id=None).all()
    errors = {}

    unread_notifications = Notification.query.filter_by(admin_id=admin.admin_id, is_read=False).order_by(Notification.created_at.desc()).all()
    unread_notifications_count = len(unread_notifications)
    recent_notifications = Notification.query.filter_by(admin_id=admin.admin_id).order_by(Notification.created_at.desc()).limit(10).all()

    if request.method == 'POST':
        # Retrieve form data
        try:
            is_featured = True if request.form.get('is_featured') == 'on' else False
            product_name = request.form.get('product_name')
            description = request.form.get('description')  # Allow HTML content
            price = request.form.get('price')
            stock_quantity = request.form.get('stock_quantity')
            sizes = request.form.getlist('sizes')
            colors = request.form.getlist('colors')
            category_id = request.form.get('category_id')
            images = request.files.getlist('images')

            # Validation
            if not product_name:
                errors['product_name'] = 'Product name is required.'
            if not price:
                errors['price'] = 'Price is required.'
            else:
                try:
                    price = float(price)
                except ValueError:
                    errors['price'] = 'Price must be a number.'
            if not stock_quantity:
                errors['stock_quantity'] = 'Stock quantity is required.'
            else:
                try:
                    stock_quantity = int(stock_quantity)
                except ValueError:
                    errors['stock_quantity'] = 'Stock quantity must be an integer.'
            if not category_id:
                errors['category_id'] = 'Category is required.'
            else:
                category = Category.query.get(category_id)
                if not category:
                    errors['category_id'] = 'Selected category does not exist.'

            # Re-render the form with errors
            if errors:
                return render_template(
                    'admin/edit_product.html',
                    product=product,
                    categories=categories,
                    errors=errors,
                    request=request,
                    unread_notifications=unread_notifications,
                    unread_notifications_count=unread_notifications_count,
                    recent_notifications=recent_notifications,
                    admin=admin,
                )

            # Update product details
            product.product_name = product_name
            product.description = description
            product.price = price
            product.stock_quantity = stock_quantity
            product.sizes = ','.join(sizes)
            product.colors = ','.join(colors)
            product.category_id = category_id
            product.is_featured = is_featured

            # Handle image uploads
            product_folder = app.config['PRODUCT_UPLOADER']
            if not os.path.exists(product_folder):
                os.makedirs(product_folder)

            if images and images[0].filename != '':
                # Remove old images
                ProductImage.query.filter_by(product_id=product.product_id).delete()

                # Add new images
                for image_file in images:
                    filename = secure_filename(image_file.filename)
                    image_save_path = os.path.join(product_folder, filename)
                    image_file.save(image_save_path)
                    image_url = os.path.join('products', filename).replace('\\', '/')
                    product_image = ProductImage(product_id=product.product_id, image_url=image_url)
                    db.session.add(product_image)

            db.session.commit()
            flash('Product updated successfully.', 'success')
            return redirect(url_for('admin_products'))  # Redirect to the products page

        except Exception as e:
            db.session.rollback()
            print(f"Error updating product: {e}")  # Log error for debugging
            flash('An error occurred while updating the product.', 'danger')

    return render_template(
        'admin/edit_product.html',
        product=product,
        categories=categories,
        errors=errors,
        request=request,
        unread_notifications=unread_notifications,
        unread_notifications_count=unread_notifications_count,
        recent_notifications=recent_notifications,
        admin=admin,
    )



@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@admin_login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the product.', 'danger')
        print(f"Error: {e}")
    return redirect(url_for('admin_products'))




@app.route('/admin/products/')
@admin_login_required
def admin_products():
    # Assuming 'admin_id' is stored in session after login
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id) if admin_id else None  # Fetch the admin from the database
    unread_notifications = Notification.query.filter_by(admin_id=admin.admin_id, is_read=False).order_by(Notification.created_at.desc()).all()
    unread_notifications_count = len(unread_notifications)

    recent_notifications = Notification.query.filter_by(admin_id=admin.admin_id).order_by(Notification.created_at.desc()).limit(10).all()

    if admin is None:
        flash("Admin not found", "danger")
        return redirect(url_for('admin_login'))

    products = Product.query.all()
    return render_template('admin/products.html', products=products, admin=admin,        unread_notifications=unread_notifications,
    unread_notifications_count=unread_notifications_count,
    recent_notifications=recent_notifications,)


@app.route('/admin/register/', methods=['GET', 'POST'])
def admin_register():
    errors = {}
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')

        # Basic validation
        if not username:
            errors['username'] = 'Username is required.'
        if not email:
            errors['email'] = 'Email is required.'
        if not password:
            errors['password'] = 'Password is required.'
        if password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match.'

        # Check if username or email already exists
        if Admin.query.filter_by(username=username).first():
            errors['username'] = 'Username already exists.'
        if Admin.query.filter_by(email=email).first():
            errors['email'] = 'Email already registered.'

        if errors:
            # Render template with errors
            return render_template('admin/register.html', errors=errors, request=request)
        else:
            # Create new admin
            admin = Admin(username=username, email=email)
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            flash('Admin registered successfully. You can now log in.')
            return redirect(url_for('admin_login'))

    return render_template('admin/register.html', errors=errors, request=request)


@app.route('/admin/products/update/<int:product_id>/', methods=['GET', 'POST'])
@admin_login_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.product_name = request.form['product_name']
        product.description = request.form['description']
        product.price = request.form['price']
        product.stock_quantity = request.form['stock_quantity']
        product.sizes = ','.join(request.form.getlist('sizes'))
        product.colors = ','.join(request.form.getlist('colors'))
        product.category_id = request.form['category_id']

        db.session.commit()
        flash('Product updated successfully.')
        return redirect(url_for('admin_products'))

    categories = Category.query.all()
    return render_template('admin/update_product.html', product=product, categories=categories)


@app.route('/admin/users')
@admin_login_required  # Ensure this decorator checks for admin privileges
def admin_users():
    # Fetch admin from session
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id) if admin_id else None
    unread_notifications = Notification.query.filter_by(admin_id=admin.admin_id, is_read=False).order_by(Notification.created_at.desc()).all()
    unread_notifications_count = len(unread_notifications)

    recent_notifications = Notification.query.filter_by(admin_id=admin.admin_id).order_by(Notification.created_at.desc()).limit(10).all()

    if admin is None:
        flash("Admin not found", "danger")
        return redirect(url_for('admin_login'))

    # Fetch all users from the database
    users = User.query.all()
    return render_template('admin/adminusers.html', users=users, admin=admin,  unread_notifications=unread_notifications,
    unread_notifications_count=unread_notifications_count,
    recent_notifications=recent_notifications,)



@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_login_required
def edit_user(user_id):
    # Fetch admin from session
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id) if admin_id else None
    unread_notifications = Notification.query.filter_by(admin_id=admin.admin_id, is_read=False).order_by(Notification.created_at.desc()).all()
    unread_notifications_count = len(unread_notifications)

    recent_notifications = Notification.query.filter_by(admin_id=admin.admin_id).order_by(Notification.created_at.desc()).limit(10).all()
    if admin is None:
        flash("Admin not found", "danger")
        return redirect(url_for('admin_login'))

    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('name')
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        address = request.form.get('address')
        phone = request.form.get('phone')
        email = request.form.get('email')
        # Add additional fields as needed (e.g., role, status)
        
        # Update user details
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.address = address
        user.phone= phone
        user.email = email
        # Update other fields as needed
        
        try:
            db.session.commit()
            flash('User updated successfully', 'success')
            return redirect(url_for('admin_users'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the user.', 'danger')
            print(f"Error: {e}")
            return redirect(url_for('edit_user', user_id=user_id))
    
    return render_template('admin/edit_user.html', user=user, admin=admin, unread_notifications=unread_notifications,
    unread_notifications_count=unread_notifications_count,
    recent_notifications=recent_notifications)



@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@admin_login_required
def delete_user(user_id):
    # Fetch admin from session
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id) if admin_id else None

    if admin is None:
        flash("Admin not found", "danger")
        return redirect(url_for('admin_login'))

    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if user.user_id == admin_id:
        flash("You cannot delete your own account.", 'warning')
        return redirect(url_for('admin_users'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the user.', 'danger')
        print(f"Error: {e}")
    return redirect(url_for('admin_users'))


@app.route('/admin/messages', methods=['GET', 'POST'])
@admin_login_required
def admin_messages():
    admin_id = session.get('admin_id')
    admin = Admin.query.get_or_404(admin_id)
    users = User.query.all()  # Fetch all users
    unread_notifications = Notification.query.filter_by(admin_id=admin.admin_id, is_read=False).order_by(Notification.created_at.desc()).all()
    unread_notifications_count = len(unread_notifications)

    recent_notifications = Notification.query.filter_by(admin_id=admin.admin_id).order_by(Notification.created_at.desc()).limit(10).all()

    if request.method == 'POST':
        receiver_id = request.form.get('receiver_id')  # Ensure this matches the form field name
        subject = request.form.get('subject')
        content = request.form.get('content')

        # Validation
        if not receiver_id or not subject or not content:
            flash("All fields are required.", "danger")
            return redirect(url_for('admin_messages'))

        receiver = User.query.get_or_404(receiver_id)

        # Create the message
        message = Message(
            sender_id=admin_id,
            receiver_id=receiver.user_id,  # Correct field name
            subject=subject,
            content=content
        )

        try:
            db.session.add(message)
            db.session.commit()
            flash(f"Message sent to {receiver.username}.", "success")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while sending the message.", "danger")
            print(f"Error: {e}")

    return render_template('admin/send_messages.html', admin=admin, users=users,  unread_notifications=unread_notifications,
    unread_notifications_count=unread_notifications_count,
    recent_notifications=recent_notifications,)


@app.route('/admin/messages/<int:user_id>')
@admin_login_required
def admin_view_user_messages(user_id):
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id) if admin_id else None  # Fetch the admin from the database
    unread_notifications = Notification.query.filter_by(admin_id=admin.admin_id, is_read=False).order_by(Notification.created_at.desc()).all()
    unread_notifications_count = len(unread_notifications)

    recent_notifications = Notification.query.filter_by(admin_id=admin.admin_id).order_by(Notification.created_at.desc()).limit(10).all()

    user = User.query.get_or_404(user_id)
    messages = Message.query.filter_by(receiver_id=user_id).order_by(Message.created_at.desc()).all()
    return render_template('admin/user_messages.html', user=user, messages=messages, admin=admin,  unread_notifications=unread_notifications,
    unread_notifications_count=unread_notifications_count,
    recent_notifications=recent_notifications,)


@app.route('/admin/messages/users')
@admin_login_required
def admin_manage_messages():
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id) if admin_id else None
    unread_notifications = Notification.query.filter_by(admin_id=admin.admin_id, is_read=False).order_by(Notification.created_at.desc()).all()
    unread_notifications_count = len(unread_notifications)

    recent_notifications = Notification.query.filter_by(admin_id=admin.admin_id).order_by(Notification.created_at.desc()).limit(10).all()

    # Fetch all users
    users = User.query.all()

    # Fetch message counts for each user
    user_messages = []
    for user in users:
        message_count = Message.query.filter_by(receiver_id=user.user_id, sender_id=admin.admin_id).count()
        user_messages.append({
            'user': user,
            'message_count': message_count
        })

    return render_template('admin/manage_messages.html', admin=admin, user_messages=user_messages,  unread_notifications=unread_notifications,
    unread_notifications_count=unread_notifications_count,
    recent_notifications=recent_notifications,)


@app.route('/admin/messages/edit/<int:message_id>', methods=['GET', 'POST'])
@admin_login_required
def edit_message(message_id):
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id) if admin_id else None  # Fetch the admin from the database
    unread_notifications = Notification.query.filter_by(admin_id=admin.admin_id, is_read=False).order_by(Notification.created_at.desc()).all()
    unread_notifications_count = len(unread_notifications)

    recent_notifications = Notification.query.filter_by(admin_id=admin.admin_id).order_by(Notification.created_at.desc()).limit(10).all()
    message = Message.query.get_or_404(message_id)
    if request.method == 'POST':
        subject = request.form.get('subject')
        content = request.form.get('content')

        message.subject = subject
        message.content = content

        try:
            db.session.commit()
            flash('Message updated successfully.', 'success')
            return redirect(url_for('manage_messages'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the message.', 'danger')
            print(f"Error: {e}")
            return redirect(url_for('edit_message', message_id=message_id))

    return render_template('admin/edit_messages.html', message=message, admin=admin,  unread_notifications=unread_notifications,
    unread_notifications_count=unread_notifications_count,
    recent_notifications=recent_notifications)

@app.route('/admin/messages/delete/<int:message_id>', methods=['POST'])
@admin_login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)

    try:
        db.session.delete(message)
        db.session.commit()
        flash('Message deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the message.', 'danger')
        print(f"Error: {e}")
    
    return redirect(url_for('admin_manage_messages'))

@app.route('/admin/notifications/read', methods=['POST'])
@admin_login_required
def admin_mark_notifications_read():
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id)
    unread_notifications = Notification.query.filter_by(admin_id=admin.admin_id, is_read=False).all()
    for notification in unread_notifications:
        notification.is_read = True
    db.session.commit()
    return jsonify({'success': True})






@app.route('/admin/reports')
@login_required
def admin_reports():
    # Your code here
    pass

@app.route('/admin/profile')
@login_required
def admin_profile():
    # Your code here
    pass


@app.route('/admin/orders')
@admin_login_required
def admin_user_orders():
    # Fetch all orders
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id) if admin_id else None
    orders = Order.query.order_by(Order.created_at.desc()).all()
    unread_notifications = Notification.query.filter_by(admin_id=admin.admin_id, is_read=False).order_by(Notification.created_at.desc()).all()
    unread_notifications_count = len(unread_notifications)

    recent_notifications = Notification.query.filter_by(admin_id=admin.admin_id).order_by(Notification.created_at.desc()).limit(10).all()


    return render_template('admin/admin_orders.html', orders=orders, admin=admin,  unread_notifications=unread_notifications, unread_notifications_count=unread_notifications_count,
    recent_notifications=recent_notifications, pagename='All User Orders | Rokeyla Admin')


@app.route('/admin/cancel_requests')
@admin_login_required
def cancel_requests():
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id) if admin_id else None
    unread_notifications = Notification.query.filter_by(admin_id=admin.admin_id, is_read=False).order_by(Notification.created_at.desc()).all()
    unread_notifications_count = len(unread_notifications)

    recent_notifications = Notification.query.filter_by(admin_id=admin.admin_id).order_by(Notification.created_at.desc()).limit(10).all()

    cancel_orders = Order.query.filter_by(cancel_request=True).order_by(Order.created_at.desc()).all()
    return render_template('admin/cancel_requests.html', orders=cancel_orders, admin=admin, unread_notifications=unread_notifications, unread_notifications_count=unread_notifications_count,
    recent_notifications=recent_notifications)

@app.route('/admin/deny_cancel/<int:order_id>', methods=['POST'])
@admin_login_required
def admin_deny_cancel(order_id):
    order = Order.query.get_or_404(order_id)

    try:
        order.cancel_request = False
        db.session.commit()
        flash('Cancellation request has been denied.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'danger')
    return redirect(url_for('admin_user_orders'))

@app.route('/admin/deny_cancel/<int:order_id>', methods=['POST'])
@admin_login_required
def deny_cancel(order_id):
    order = Order.query.get_or_404(order_id)

    try:
        order.cancel_request = False
        db.session.commit()
        flash("Cancellation request has been denied.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred. Please try again.", "danger")
    return redirect(url_for('cancel_requests'))


@app.route('/admin/update_order_status/<int:order_id>', methods=['POST'])
@admin_login_required
def admin_update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('order_status')

    try:
        order.order_status = new_status
        if new_status == 'Cancelled':
            order.cancel_request = False
        db.session.commit()
        flash('Order status updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'danger')
    return redirect(url_for('admin_user_orders'))


# Define allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_login_required
def admin_settings():
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id) if admin_id else None
    unread_notifications = Notification.query.filter_by(admin_id=admin.admin_id, is_read=False).order_by(Notification.created_at.desc()).all()
    unread_notifications_count = len(unread_notifications)
    
    recent_notifications = Notification.query.filter_by(admin_id=admin.admin_id).order_by(Notification.created_at.desc()).limit(10).all()

    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        email = request.form.get('email')
        theme_preference = request.form.get('theme_preference')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        profile_pic = request.files.get('profile_pic')  # Correct field name here

        # Update basic info
        admin.username = username
        admin.email = email
        admin.theme_preference = theme_preference

        # Handle profile picture upload
        if profile_pic and allowed_file(profile_pic.filename):
            filename = secure_filename(profile_pic.filename)
            filename = f"profile_{admin.admin_id}_{filename}"  # Unique filename
            file_path = os.path.join(app.config['ADMIN_PROFILE_PATH'], filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure the directory exists
            profile_pic.save(file_path)
            relative_path = f"uploads/admins/{filename}"  # Adjust relative path
            admin.profile_pic = relative_path
        elif profile_pic:  # Invalid file type
            flash('Invalid file type. Allowed types are png, jpg, jpeg, gif, webp.', 'danger')
            return redirect(url_for('admin_settings'))

        # Handle password change
        if current_password and new_password and confirm_password:
            if admin.check_password(current_password):
                if new_password == confirm_password:
                    admin.set_password(new_password)
                else:
                    flash('New passwords do not match.', 'danger')
                    return redirect(url_for('admin_settings'))
            else:
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('admin_settings'))

        try:
            db.session.commit()
            flash('Settings updated successfully.', 'success')
            return redirect(url_for('admin_settings'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating settings.', 'danger')
            print(f"Error: {e}")
            return redirect(url_for('admin_settings'))

    return render_template('admin/settings.html', admin=admin, pagename='Admin Profile | Rokeyla',  unread_notifications=unread_notifications, unread_notifications_count=unread_notifications_count,
    recent_notifications=recent_notifications)



@app.route('/admin/coupons', methods=['GET', 'POST'])
@admin_login_required # Ensure this decorator checks if the user is an admin
def admin_coupons():

    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id) if admin_id else None
    unread_notifications = Notification.query.filter_by(admin_id=admin.admin_id, is_read=False).order_by(Notification.created_at.desc()).all()
    unread_notifications_count = len(unread_notifications)
    
    recent_notifications = Notification.query.filter_by(admin_id=admin.admin_id).order_by(Notification.created_at.desc()).limit(10).all()

    if request.method == 'POST':
        # Get form data
        code = request.form.get('code')
        discount_value = float(request.form.get('discount_value'))
        discount_type = request.form.get('discount_type')
        minimum_order_value = request.form.get('minimum_order_value')
        max_discount = request.form.get('max_discount')
        usage_limit = request.form.get('usage_limit')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        is_active = True if request.form.get('is_active') == 'on' else False

        # Convert dates to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else datetime.utcnow()
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

        # Create new coupon
        new_coupon = Coupon(
            code=code,
            discount_value=discount_value,
            discount_type=discount_type,
            minimum_order_value=float(minimum_order_value) if minimum_order_value else None,
            max_discount=float(max_discount) if max_discount else None,
            usage_limit=int(usage_limit) if usage_limit else None,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active
        )

        db.session.add(new_coupon)
        db.session.commit()
        flash(f"Coupon '{code}' created successfully!", "success")
        return redirect(url_for('admin_coupons'))

    # Get all coupons
    coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()

    return render_template('admin/coupons.html', coupons=coupons, pagename='Manage Coupons', unread_notifications=unread_notifications, unread_notifications_count=unread_notifications_count,
    recent_notifications=recent_notifications, admin=admin)




@app.route('/admin/ads', methods=['GET', 'POST'])
@admin_login_required
def manage_ads():
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id) if admin_id else None
    unread_notifications = Notification.query.filter_by(admin_id=admin.admin_id, is_read=False).order_by(Notification.created_at.desc()).all()
    unread_notifications_count = len(unread_notifications)
    
    recent_notifications = Notification.query.filter_by(admin_id=admin.admin_id).order_by(Notification.created_at.desc()).limit(10).all()

    if request.method == 'POST':
        content = request.form['content']
        active = 'active' in request.form
        ad = Ad(content=content, active=active)
        db.session.add(ad)
        db.session.commit()
        flash('Ad has been created.', 'success')
        return redirect(url_for('manage_ads'))
    ads = Ad.query.order_by(Ad.created_at.desc()).all()
    return render_template('admin/manage_ads.html', ads=ads, unread_notifications=unread_notifications, unread_notifications_count=unread_notifications_count,
    recent_notifications=recent_notifications, admin=admin)




@app.route('/admin/ads/edit/<int:ad_id>', methods=['GET', 'POST'])
@admin_login_required
def edit_ad(ad_id):
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id) if admin_id else None
    unread_notifications = Notification.query.filter_by(admin_id=admin.admin_id, is_read=False).order_by(Notification.created_at.desc()).all()
    unread_notifications_count = len(unread_notifications)
    
    recent_notifications = Notification.query.filter_by(admin_id=admin.admin_id).order_by(Notification.created_at.desc()).limit(10).all()

    ad = Ad.query.get_or_404(ad_id)

    if request.method == 'POST':
        ad.content = request.form.get('content')
        ad.active = bool(request.form.get('active'))
        db.session.commit()
        flash('Ad updated successfully!', 'success')
        return redirect(url_for('manage_ads'))

    return render_template('admin/edit_ad.html', ad=ad, unread_notifications=unread_notifications, unread_notifications_count=unread_notifications_count,
    recent_notifications=recent_notifications, admin=admin)


@app.route('/admin/ads/delete/<int:ad_id>', methods=['POST'])
@admin_login_required
def delete_ad(ad_id):
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id) if admin_id else None

    ad = Ad.query.get_or_404(ad_id)
    db.session.delete(ad)
    db.session.commit()
    flash('Ad deleted successfully!', 'success')
    return redirect(url_for('manage_ads'))




@app.route('/admin/newsletter_subscribers')
@admin_login_required
def view_subscribers():
    admin_id = session.get('admin_id')
    admin = Admin.query.get(admin_id) if admin_id else None
    unread_notifications = Notification.query.filter_by(admin_id=admin.admin_id, is_read=False).order_by(Notification.created_at.desc()).all()
    unread_notifications_count = len(unread_notifications)
    recent_notifications = Notification.query.filter_by(admin_id=admin.admin_id).order_by(Notification.created_at.desc()).limit(10).all()
    subscribers = NewsletterSubscriber.query.order_by(NewsletterSubscriber.subscribed_at.desc()).all()
    return render_template('admin/newsletter_subscribers.html', subscribers=subscribers, unread_notifications=unread_notifications, unread_notifications_count=unread_notifications_count,
    recent_notifications=recent_notifications, admin=admin)



@app.route('/admin/newsletter_subscribers/delete/<int:subscriber_id>', methods=['POST'])
@admin_login_required
def delete_subscriber(subscriber_id):
    subscriber = NewsletterSubscriber.query.get_or_404(subscriber_id)
    db.session.delete(subscriber)
    db.session.commit()
    flash('Subscriber deleted successfully.', 'success')
    return redirect(url_for('view_subscribers'))
