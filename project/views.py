from flask import Blueprint, render_template, request, session, flash, current_app
from flask import redirect, url_for, jsonify
from datetime import datetime

from hashlib import sha256

from project.db import add_order, get_orders, check_for_user, add_user, is_admin, get_images, get_ratings
from project.db import get_cities, get_city, get_tours_for_city, add_city, add_tour, add_image, add_to_cart
from project.session import get_basket, add_to_basket, empty_basket, remove_from_basket, convert_basket_to_order
from project.forms import CheckoutForm, LoginForm, RegisterForm, AddTourForm, AddCityForm, AddImageForm
from project.models import City, Tour, Currency, Image
from project.utils import is_allowed_file, generate_uuid
from werkzeug.utils import secure_filename
import os

from project.wrappers import only_admins

bp = Blueprint('main', __name__)


@bp.route('/root/', methods=['GET', 'POST'])
def root_index():
    print(get_images())
    return render_template('index.html', images=get_images())


@bp.route('/cart/<string:imageID>', methods=['GET', 'POST'])
def add_cart(imageID):
    if 'user' not in session or session['user']['userID'] == 0 or not session['logged_in']:
        flash('Please log in before add to cart.')
        return jsonify({'redirect': url_for('main.login')}), 401

    add_to_cart(session['user']['userID'], imageID)
    return ('', 204)


@bp.route('/upload/', methods=['GET', 'POST'])
@only_admins
def upload_image():
    addImageForm = AddImageForm()
    if 'user' not in session or session['user']['userID'] == 0 or not session['logged_in']:
        flash('Please log in before upload image.')
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
                    extension=os.path.splitext(
                        secure_filename(file.filename))[1]
                )

                # filename = secure_filename(file.filename)
                save_path = os.path.join(
                    current_app.config['UPLOAD_FOLDER'], imageUpload.imageID + imageUpload.extension)
                file.save(save_path)

                add_image(imageUpload)

                flash("Image uploaded successfully!")
                return redirect(url_for('main.upload_image'))
            else:
                flash("Invalid file type! Only png, jpg, jpeg allowed.", 'error')
    return render_template('upload.html', addImageForm=addImageForm)


@bp.route('/register/', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # temp debug
            # form.password.data = sha256(
            #     form.password.data.encode()).hexdigest()

            # Check if the user already exists
            user = check_for_user(form.username.data, form.password.data)
            if user:
                flash('User already exists', 'error')
                return redirect(url_for('main.register'))

            add_user(form)
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
            user = check_for_user(form.username.data, form.password.data)
            print("----------------user:", user)
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
            return redirect(url_for('main.root_index'))

    return render_template('login.html', form=form)


@bp.route('/logout/')
def logout():
    session.pop('user', None)
    session.pop('logged_in', None)
    flash('You have been logged out.')
    return redirect(url_for('main.root_index'))

# -----------------------------------------------------------TENMPLATE----------------------------------------------------


@bp.route('/')
def index():
    return render_template('index.html', cities=get_cities())


@bp.route('/tours/<int:cityid>/')
def citytours(cityid):
    citytours = get_tours_for_city(cityid)
    return render_template('citytours.html', tours=citytours, city=get_city(cityid))


@bp.route('/order/', methods=['GET'])
def order():
    tour_id = request.args.get('tour_id')
    order = get_basket()

    if tour_id:
        print(f'user requested to add tour id = {tour_id}')
        add_to_basket(tour_id)

    return render_template('order.html', order=order, totalprice=order.total_cost())


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


@bp.route('/checkout/', methods=['POST', 'GET'])
def checkout():

    if 'user' not in session or session['user']['user_id'] == 0:
        flash('Please log in before checking out.')
        return redirect(url_for('main.login'))

    form = CheckoutForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # If user not logged in, use form data to simulate a user
            if 'user' not in session:
                session['user'] = {
                    'user_id': 0,
                    'firstname': form.firstname.data,
                    'surname': form.surname.data,
                    'email': form.email.data,
                    'phone': form.phone.data,
                }

            order = convert_basket_to_order(get_basket())
            add_order(order)
            empty_basket()
            flash('Thank you for your information, your order is being processed!')
            return redirect(url_for('main.index'))
        else:
            flash('The provided information is missing or incorrect', 'error')
    else:
        form.firstname.data = session['user']['firstname']
        form.surname.data = session['user']['surname']
        form.email.data = session['user']['email']
        form.phone.data = session['user']['phone']

    return render_template('checkout.html', form=form)


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


@bp.route('/manage/')
@only_admins
def manage():
    # check if the user is logged in and is an admin
    if 'user' not in session or session['user']['user_id'] == 0:
        flash('Please log in before managing orders.', 'error')
        return redirect(url_for('main.login'))
    if not session['user']['is_admin']:
        flash('You do not have permission to manage orders.', 'error')
        return redirect(url_for('main.index'))
    # now we know the user is logged in and is an admin
    # we can show the manage panel
    cityform = AddCityForm()
    tourform = AddTourForm()
    # we need to populate the cities in the tourform
    tourform.tour_city.choices = [(city.id, city.name)
                                  for city in get_cities()]
    return render_template('manage.html', cityform=cityform, tourform=tourform)


@bp.post('/manage/')
def handle_manage():
    cityform = AddCityForm()
    tourform = AddTourForm()
    # we need to populate the cities in the tourform
    # otherwise the form will not validate
    tourform.tour_city.choices = [(city.id, city.name)
                                  for city in get_cities()]
    try:
        if cityform.validate_on_submit():
            # Add the new city to the database
            city = City(
                id=0,
                name=cityform.city_name.data,
                description=cityform.city_description.data,
                image='brisbane.jpg'
            )
            add_city(city)
            flash('City added successfully!')
        elif tourform.validate_on_submit():
            # Add the new tour to the database
            tour = Tour(
                id=0,
                name=tourform.tour_name.data,
                description=tourform.tour_description.data,
                price=float(tourform.tour_price.data),
                city=get_city(tourform.tour_city.data)
            )
            add_tour(tour)
            flash('Tour added successfully!')
        else:
            flash('Failed to add city or tour. Please check your input.')
    except Exception as e:
        flash(f'An error occurred: {e}', 'error')
    return redirect(url_for('main.index'))
