from flask import (
    Blueprint, render_template, request, session, flash, current_app,
    redirect, url_for, jsonify
)
from datetime import datetime
from flask import send_file, Response
from project.db import get_images_by_vendor, add_image, edit_image, delete_selected_image,get_all_categories, config_image, get_vendor
from project.db import (add_image, config_image, edit_image,
    get_images_by_vendor)
from hashlib import sha256
from project.forms import EditImageForm
from project.db import add_order, get_orders, add_customer, add_vendor, is_admin, get_images, get_ratings, get_user, check_user, get_categories_by_image
from project.db import get_cities, get_city, get_tours_for_city, add_city, add_tour, add_image, add_to_cart, get_image_in_cart, update_image_categories
from project.session import get_basket, add_to_basket, empty_basket, remove_from_basket, convert_basket_to_order
from project.forms import CheckoutForm, LoginForm, RegisterForm, AddTourForm, AddCityForm, AddImageForm
from project.models import City, Tour, Currency, Image, Role
from project.utils import is_allowed_file, generate_uuid, check_user_logged_in
from werkzeug.utils import secure_filename
import os
from werkzeug.utils import secure_filename

from project.db import (
    add_category, add_customer, add_order, check_user, get_categories,
    get_images, get_orders, get_ratings, get_user, is_admin, get_customer,
    get_cities, get_city, get_tours_for_city, add_city, add_tour, add_image,
    add_to_cart, get_image_in_cart, remove_image_cart, get_image
)

from project.session import (
    get_basket, add_to_basket, empty_basket,
    remove_from_basket, convert_basket_to_order
)

from project.forms import (
    LoginForm, RegisterForm, AddTourForm, AddCityForm, AddImageForm,
    AddCategoryForm, CheckoutForm, CheckoutFormPayment
)

from project.models import City, Tour, Currency, Image, Role, Category

from project.utils import is_allowed_file, generate_uuid, check_user_logged_in
from project.wrappers import only_admins, only_vendors


bp = Blueprint('main', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    images = get_images()
    images_with_vendor = [(img, get_vendor(img.userID)) for img in images]
    
    newImages = sorted(images, key=lambda x: x.updateDate, reverse=True)
    newImages_with_vendor = [(img, get_vendor(img.userID)) for img in newImages]
    

    return render_template('index.html', images=images_with_vendor, newImages= newImages_with_vendor)


@bp.route('/item/<string:imageID>', methods=['GET', 'POST'])
def item_detail(imageID):
    item = get_image(imageID)
    return render_template('item.html', item=item)


@bp.route('/cart/<string:imageID>', methods=['GET', 'POST'])
def add_cart(imageID):
    if check_user_logged_in() == False:
        flash('Please log in before add to cart.', 'error')
        return jsonify({'redirect': url_for('main.login')}), 401

    add_to_cart(session['user']['userID'], imageID)
    return ('', 204)


@bp.route('/vendor/', methods=['GET', 'POST'])
@only_vendors
def vendor():
    addImageForm = AddImageForm()
    userID = session['user']['userID']
    vendor_images = get_images_by_vendor(userID)

    edit_forms = {}
    for img in vendor_images:
        form = EditImageForm(obj=img)
        # Populate all available categories
        form.categories.choices = get_all_categories()  # returns [(id, name), ...]
        form.imageStatus.data = img.imageStatus
        # Pre-check the assigned categories
        form.categories.data = [c.categoryID for c in img.listCategory]
        edit_forms[img.imageID] = form

    if check_user_logged_in() == False:
        flash('Please log in before upload image.', 'error')
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        if addImageForm.validate_on_submit():
            file = request.files['image_file']
            title = request.form['title']
            listCategory = request.form.getlist('categories')
            description = request.form['description']
            price = request.form['price']
            currency = request.form['currency']
            

            if file and is_allowed_file(file.filename):
                imageUpload = Image(
                    userID=session['user']['userID'],
                    listCategory=listCategory,
                    imageID=generate_uuid(),
                    title=title,
                    description=description,
                    price=float(price),
                    quantity=0,
                    currency=Currency(currency),
                    imageStatus='ACTIVE',
                    updateDate=datetime.now(),
                    listRatings=[],
                    extension=os.path.splitext(secure_filename(file.filename))[1]
                )
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], imageUpload.imageID + imageUpload.extension)
                file.save(save_path)

                add_image(imageUpload)
                flash("Image uploaded successfully!")
                return redirect(url_for('main.vendor'))
            else:
                flash("Invalid file type! Only png, jpg, jpeg allowed.", 'error')

    return render_template('vendor.html', addImageForm=addImageForm, vendor_images=vendor_images, edit_forms=edit_forms)

#To update image's details in vendor.html page

@bp.route('/vendor/edit_image/<imageID>', methods=['POST'])
@only_vendors
def update_image(imageID):
    userID = session['user']['userID']

    #Fetch the image from db
    img = get_image(imageID)
    if not img or img.userID != userID:
        flash("Image not found.", "error")
        return redirect(url_for('main.vendor'))

    # Initialize the form
    form = EditImageForm(obj=img)
    form.categories.choices = get_all_categories()  
    
    
    if form.validate_on_submit():
        # Get selected categories of image
        selected_categories = form.categories.data  
        
        # Update into image table
        success = edit_image(
            imageID,
            form.title.data,
            form.description.data,
            float(form.price.data),
            form.currency.data,
            form.imageStatus.data,
            selected_categories
            
        )
       
        if success:
            flash("Image updated successfully!", "success")
        else:
            flash("Failed to update image.", "error")

    return redirect(url_for('main.vendor'))

# Vendor site, to delete the existing images via vendor.html page
@bp.route('/vendor/delete_image/<imageID>', methods=['POST'])
@only_vendors
def delete_image(imageID):
    success = config_image(imageID, True)
    if success:
        flash("Image deleted successfully!", "success")
    else:
        flash("Image not found or failed to delete.", "danger")
    return redirect(url_for('main.vendor'))

@bp.route('/register/', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # temp debug
            # form.password.data = sha256(
            #     form.password.data.encode()).hexdigest()

            # Check if the user already exists
            user = check_user(form.username.data)
            if user:
                flash('User already exists', 'error')
                return redirect(url_for('main.register'))

            # I want to insert user based on role
            if form.role.data == Role.CUSTOMER.value:
                add_customer(form)
            elif form.role.data == Role.VENDOR.value:
                add_vendor(form)

            flash('Registration successful!')
            return redirect(url_for('main.login'))

    return render_template('register.html', form=form)


@bp.route('/login/', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            # temp debug
            # form.password.data = sha256(
            #     form.password.data.encode()).hexdigest()
            user = get_user(form.username.data, form.password.data)
            if not user:
                flash('Invalid username or password', 'error')
                return redirect(url_for('main.login'))
            # Store full user info in session
            session['user'] = {
                'userID': user.userID,
                'firstname': user.firstname,
                'surname': user.surname,
                'email': user.email,
                'phone': user.phone,
                'role': user.role.value,
            }
            session['logged_in'] = True
            flash('Login successful!')
            if user.role.value == Role.ADMIN.value:
                return redirect(url_for('main.manage'))
            return redirect(url_for('main.index'))
        


    return render_template('login.html', form=form)


@bp.route('/logout/')
def logout():
    session.pop('user', None)
    session.pop('logged_in', None)
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@bp.route('/remove_image_cart/<string:imageID>', methods=['POST'])
def remove_cart_item(imageID):
    if check_user_logged_in() == False:
        flash('Please log in before remove from cart.', 'error')
        return redirect(url_for('main.login'))
    userID = session['user']['userID']

    remove_image_cart(userID, imageID)
    flash('Image removed from cart.')
    return redirect(url_for('main.checkout'))


@bp.route('/checkout/', methods=['GET', 'POST'])
def checkout():
    if check_user_logged_in() == False:
        flash('Please log in before checkout.', 'error')
        return redirect(url_for('main.login'))
    userID = session['user']['userID']
    listImage = get_image_in_cart(userID)
    totalPrice = round(sum(image.price for image in listImage), 2)
    customerInfor = get_customer(session['user']['userID'])

    # form = CheckoutForm()
    formPayment = CheckoutFormPayment()

    if request.method == 'POST':
        if formPayment.validate_on_submit():
            flash('Payment successful!')
            return redirect(url_for('main.checkout'))
        else:
            flash('The provided information is missing or incorrect', 'error')

    formPayment.firstname.data = session['user']['firstname']
    formPayment.surname.data = session['user']['surname']
    formPayment.email.data = session['user']['email']
    formPayment.phone.data = session['user']['phone']

    # if form.validate_on_submit():
    #     form.firstname.data = session['user']['firstname']
    #     form.surname.data = session['user']['surname']
    #     form.email.data = session['user']['email']
    #     form.phone.data = session['user']['phone']
    #     flash("Payment successful!", "success")
    #     return redirect(url_for('main.checkout_success'))
    # if formPayment.validate_on_submit():

    #     card_number = form.cardNumber.data
    #     expiry = form.expiryDate.data
    #     cvv = form.CVV.data

    #     flash("Payment successful!", "success")
    #     return redirect(url_for('main.checkout_success'))

    return render_template(
        'checkout.html',
        formPayment=formPayment,
        listImage=listImage,
        totalPrice=totalPrice,
        customerInfor=customerInfor
    )


@bp.route('/manage/')
@only_admins
def manage():
    # check if the user is logged in and is an admin
    if check_user_logged_in() == False:
        flash('Please log in before managing orders.', 'error')
        return redirect(url_for('main.login'))
    if not session['user']['role'] == Role.ADMIN.value:
        flash('You do not have permission to manage orders.', 'error')
        return redirect(url_for('main.index'))
    # now we know the user is logged in and is an admin
    # we can show the manage panel
    categoryForm = AddCategoryForm()
    return render_template('manage.html', categoryForm=categoryForm)


@bp.post('/manage/')
@only_admins
def handle_manage():
    categoryForm = AddCategoryForm()
    try:
        if categoryForm.validate_on_submit():
            # Add the new city to the database
            category = Category(categoryID=generate_uuid(
            ), categoryName=categoryForm.categoryName.data, description=categoryForm.description.data)
            add_category(category)
            flash('Category added successfully!')
        else:
            flash('Failed to add Category. Please check your input.')
    except Exception as e:
        flash(f'An error occurred: {e}', 'error')
    return redirect(url_for('main.index'))



# -----------------------------------------------------------TENMPLATE----------------------------------------------------


# @bp.route('/')
# def index():
#     return render_template('index.html', cities=get_cities())


@bp.route('/tours/<int:cityid>/')
def citytours(cityid):
    citytours = get_tours_for_city(cityid)
    return render_template('citytours.html', tours=citytours, city=get_city(cityid))


# @bp.route('/order_temp/', methods=['GET'])
# def order_():
#     tour_id = request.args.get('tour_id')

#     if tour_id:
#         print(f'user requested to add tour id = {tour_id}')
#         add_to_basket(tour_id)

#     return render_template('order.html', order=order, totalprice=order.total_cost())


@bp.post('/basket/<int:tour_id>/')
def adding_to_basket(tour_id):
    add_to_basket(tour_id)
    return redirect(url_for('main.order'))


@bp.post('/basket/<int:tour_id>/<int:quantity>/')
def adding_to_basket_with_quantity(tour_id, quantity):
    add_to_basket(tour_id, quantity)
    return redirect(url_for('main.order'))


@bp.post('/clearbasket/')
def clear_basket():
    empty_basket()
    flash('Basket cleared.')
    return redirect(url_for('main.order'))


@bp.post('/removebasketitem/<string:item_id>/')
def remove_basketitem(item_id):
    basket = get_basket()
    item = basket.get_item(item_id)

    if item:
        flash(f"Removed '{item.tour.name}' from basket.")
        remove_from_basket(item_id)
    else:
        flash("Item not found in basket.", "warning")

    return redirect(url_for('main.order'))


# @bp.route('/checkout/', methods=['POST', 'GET'])
# def checkout():

#     if 'user' not in session or session['user']['userID'] == 0:
#         flash('Please log in before checking out.')
#         return redirect(url_for('main.login'))

#     form = CheckoutForm()
#     if request.method == 'POST':
#         if form.validate_on_submit():
#             # If user not logged in, use form data to simulate a user
#             if 'user' not in session:
#                 session['user'] = {
#                     'user_id': 0,
#                     'firstname': form.firstname.data,
#                     'surname': form.surname.data,
#                     'email': form.email.data,
#                     'phone': form.phone.data,
#                 }

#             order = convert_basket_to_order(get_basket())
#             add_order(order)
#             empty_basket()
#             flash('Thank you for your information, your order is being processed!')
#             return redirect(url_for('main.index'))
#         else:
#             flash('The provided information is missing or incorrect', 'error')
#     else:
#         form.firstname.data = session['user']['firstname']
#         form.surname.data = session['user']['surname']
#         form.email.data = session['user']['email']
#         form.phone.data = session['user']['phone']

#     return render_template('checkout.html', form=form)


# @bp.route('/register/', methods=['POST', 'GET'])
# def register():
#     form = RegisterForm()
#     if request.method == 'POST':
#         if form.validate_on_submit():
#             form.password.data = sha256(
#                 form.password.data.encode()).hexdigest()
#             # Check if the user already exists
#             user = check_for_user(form.username.data, form.password.data)
#             if user:
#                 flash('User already exists', 'error')
#                 return redirect(url_for('main.register'))

#             add_user(form)
#             flash('Registration successful!')
#             return redirect(url_for('main.login'))

#     return render_template('register.html', form=form)


# @bp.route('/login/', methods=['POST', 'GET'])
# def login():
#     form = LoginForm()

#     if request.method == 'POST':
#         if form.validate_on_submit():
#             form.password.data = sha256(
#                 form.password.data.encode()).hexdigest()
#             user = check_for_user(form.username.data, form.password.data)
#             if not user:
#                 flash('Invalid username or password', 'error')
#                 return redirect(url_for('main.login'))

#             # Store full user info in session
#             session['user'] = {
#                 'user_id': user.info.id,
#                 'firstname': user.info.firstname,
#                 'surname': user.info.surname,
#                 'email': user.info.email,
#                 'phone': user.info.phone,
#                 'is_admin': is_admin(user.info.id),
#             }
#             session['logged_in'] = True
#             flash('Login successful!')
#             return redirect(url_for('main.index'))

#     return render_template('login.html', form=form)


# @bp.route('/logout/')
# def logout():
#     session.pop('user', None)
#     session.pop('logged_in', None)
#     flash('You have been logged out.')
#     return redirect(url_for('main.index'))
