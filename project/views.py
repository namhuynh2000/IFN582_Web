from flask import (
    Blueprint, render_template, request, session, flash, current_app,
    redirect, url_for, jsonify
)
from datetime import datetime
from hashlib import sha256
import os
from werkzeug.utils import secure_filename

from project.db import (
    add_image, add_purchase, config_image, config_user, count_images,
    delete_category, edit_category, edit_image, get_all_categories,
    get_all_users, get_images_by_user_purchase, get_images_by_vendor,
    get_images_sort, get_status_user, get_vendor, remove_all_image_cart,
    add_customer, add_vendor, get_user, check_user, get_active_image,
    add_to_cart, get_image_in_cart, remove_image_cart, get_image,
    add_category, get_categories, get_customer, get_vendorName
)

from project.forms import (
    LoginForm, RegisterForm, AddImageForm, EditImageForm, CheckoutFormPayment
)

from project.models import Currency, Image, Role, Category

from project.utils import (
    is_allowed_file, generate_uuid, check_user_logged_in
)

from project.wrappers import only_admins, only_vendors


bp = Blueprint('main', __name__)


@bp.route('/manage/')
def manage():
    # check if the user is logged in and is an admin
    if check_user_logged_in() == False:
        flash('Please log in before managing photosite', 'error')
        return redirect(url_for('main.login'))
    if not session['user']['role'] == Role.ADMIN.value:
        flash('You do not have permission to manage orders', 'error')
        return redirect(url_for('main.index'))
    # now we know the user is logged in and is an admin
    categories = get_categories()
    users = get_all_users()
    return render_template('manage.html', categories=categories, users=users)


@bp.route('/users/<user_id>/toggle', methods=['POST'])
def user_toggle(user_id):
    userStatus = get_status_user(user_id)

    if not userStatus:
        flash("User not found", "error")
        return redirect(url_for('main.manage'))

    new_status = not userStatus['isDeleted']
    config_user(user_id, new_status)

    msg = "User reactivated" if new_status == False else "User deactivated"
    flash(msg)
    return redirect(url_for('main.manage'))


@bp.route('/manage/categories/create', methods=['GET', 'POST'])
def cat_create():
    name = request.form.get('categoryName', '').strip()
    desc = request.form.get('description', '').strip()
    if not name:
        flash('Category name is required', 'error')
        return redirect(url_for('main.manage'))

    success = add_category(Category(
        categoryID=generate_uuid(),
        categoryName=name,
        description=desc
    ))
    if not success:
        flash('Category creation failed', 'error')
        return redirect(url_for('main.manage'))
    flash('Category created successfully')
    return redirect(url_for('main.manage'))


@bp.route('/manage/categories/update', methods=['POST'])
def cat_update():
    cid = request.form.get('categoryID')
    name = request.form.get('categoryName', '').strip()
    desc = request.form.get('description', '').strip()

    if not cid or not name:
        flash('Invalid data', 'error')
        return redirect(url_for('main.manage'))

    success = edit_category(
        Category(categoryID=cid, categoryName=name, description=desc))
    if not success:
        flash('Category update failed', 'error')
        return redirect(url_for('main.manage'))
    flash('Category updated successfully')
    return redirect(url_for('main.manage'))


@bp.route('/manage/categories/<category_id>/delete', methods=['POST'])
@only_admins
def cat_delete(category_id):
    if check_user_logged_in() == False:
        flash('Please log in before managing photosite', 'error')
        return redirect(url_for('main.login'))
    if not session['user']['role'] == Role.ADMIN.value:
        flash('You do not have permission to manage orders', 'error')
        return redirect(url_for('main.index'))
    success = delete_category(category_id)
    if not success:
        flash('Category deletion failed', 'error')
        return redirect(url_for('main.manage'))
    flash('Category deleted successfully')
    return redirect(url_for('main.manage'))


@bp.route('/', methods=['GET', 'POST'])
def index():
    userID = session['user']['userID'] if 'user' in session else None
    images = get_active_image()
    boughtImages = []
    if (userID):
        boughtImages = get_images_by_user_purchase(userID)
    boughtIDImages = [img.imageID for img in boughtImages]
    bestSaleImages = sorted(images, key=lambda x: x.quantity, reverse=True)
    bestSaleImages_with_vendor = [
        (img, get_vendor(img.userID)) for img in bestSaleImages]
    newImages = sorted(images, key=lambda x: x.updateDate, reverse=True)

    newImages_with_vendor = [(img, get_vendor(img.userID))
                             for img in newImages]

    return render_template('index.html', boughtIDImages=boughtIDImages, images=bestSaleImages_with_vendor, newImages=newImages_with_vendor, userID=userID)

# To get vendor name for each image in item details page


@bp.route('/item/<string:imageID>', methods=['GET', 'POST'])
def item_detail(imageID):
    userID = session['user']['userID'] if 'user' in session else None
    item = get_image(imageID)
    boughtImages = []
    if (userID):
        boughtImages = get_images_by_user_purchase(userID)
    boughtIDImages = [img.imageID for img in boughtImages]
    username = get_vendorName(item.userID)
    return render_template('item.html', item=item, username=username, userID=userID, boughtIDImages=boughtIDImages)


@bp.route('/cart/<string:imageID>', methods=['GET', 'POST'])
def add_cart(imageID):
    if check_user_logged_in() == False:
        flash('Please log in before add to cart', 'error')
        return jsonify({'redirect': url_for('main.login')}), 401

    add_to_cart(session['user']['userID'], imageID)
    return ('', 204)


@bp.route('/remove_image_cart/<string:imageID>', methods=['POST'])
def remove_cart_item(imageID):
    if check_user_logged_in() == False:
        flash('Please log in before remove from cart', 'error')
        return redirect(url_for('main.login'))
    userID = session['user']['userID']

    remove_image_cart(userID, imageID)
    flash('Image removed from cart successfully')
    return redirect(url_for('main.checkout'))


@bp.route('/clear_cart/', methods=['POST', 'GET'])
def clear_cart():
    if check_user_logged_in() == False:
        flash('Please log in before remove from cart', 'error')
        return redirect(url_for('main.login'))
    userID = session['user']['userID']

    success = remove_all_image_cart(userID)
    if not success:
        flash('Failed to clear cart', 'error')
        return redirect(url_for('main.checkout'))
    flash('Cart cleared successfully')
    return redirect(url_for('main.checkout'))


@bp.route('/vendor/', methods=['GET', 'POST'])
@only_vendors
def vendor():
    addImageForm = AddImageForm()
    userID = session['user']['userID']
    addImageForm.categories.choices = get_all_categories()
    vendor_images = get_images_by_vendor(userID)

    cats = get_categories()
    addImageForm.categories.choices = [
        (c.categoryID, c.categoryName) for c in cats]

    edit_forms = {}
    for img in vendor_images:
        form = EditImageForm(obj=img)
        # Populate all available categories
        # returns [(id, name), ...]
        form.categories.choices = get_all_categories()
        form.imageStatus.data = img.imageStatus
        # Pre-check the assigned categories
        form.categories.data = [c.categoryID for c in img.listCategory]
        edit_forms[img.imageID] = form

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
                    imageStatus='Active',
                    updateDate=datetime.now(),
                    listRatings=[],
                    extension=os.path.splitext(
                        secure_filename(file.filename))[1]
                )
                save_path = os.path.join(
                    current_app.config['UPLOAD_FOLDER'], imageUpload.imageID + imageUpload.extension)
                file.save(save_path)

                add_image(imageUpload)
                flash("Image uploaded successfully")
                return redirect(url_for('main.vendor'))
            else:
                flash("Invalid file type! Only png, jpg, jpeg allowed", 'error')

    return render_template('vendor.html', addImageForm=addImageForm, vendor_images=vendor_images, edit_forms=edit_forms)

# To update image's details in vendor.html page


@bp.route('/vendor/edit_image/<imageID>', methods=['POST'])
@only_vendors
def update_image(imageID):
    userID = session['user']['userID']

    # Fetch the image from db
    img = get_image(imageID)
    if not img or img.userID != userID:
        flash("Image not found", "error")
        return redirect(url_for('main.vendor'))

    # Initialize the form
    form = EditImageForm(request.form, obj=img)
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
            flash("Image updated successfully")
        else:
            flash("Failed to update image", "error")
        return redirect(url_for('main.vendor'))

    else:
        flash("Form validation failed. Please check the inputs", "error")

    return redirect(url_for('main.vendor'))

# Vendor site, to delete the existing images via vendor.html page


@bp.route('/vendor/delete_image/<imageID>', methods=['POST'])
@only_vendors
def delete_image(imageID):
    success = config_image(imageID, True)
    if success:
        flash("Image deleted successfully")
    else:
        flash("Image not found or failed to delete", "error")
    return redirect(url_for('main.vendor'))

# To display all active images in the system on gallery page


@bp.route('/gallery')
def gallery():
    userID = session['user']['userID'] if 'user' in session else None
    categories = get_all_categories()
    category_id = request.args.get('category', 'all')
    page = int(request.args.get('page', 1))
    per_page = 8

    images = get_images_sort(
        page=page, per_page=per_page, category_id=category_id)
    total = count_images(category_id)
    total_pages = (total + per_page - 1) // per_page

    boughtIDImages = []
    if (userID):
        boughtImages = get_images_by_user_purchase(userID)
        if (boughtImages):
            boughtIDImages = [row.imageID for row in boughtImages]

    return render_template(
        'gallery.html',
        images=images,
        boughtIDImages=boughtIDImages,
        userID=userID,
        page=page,
        total_pages=total_pages,
        categories=categories
    )


@bp.route('/register/', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # temp debug
            form.password.data = sha256(
                form.password.data.encode()).hexdigest()

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

            flash('Registration successful')
            return redirect(url_for('main.login'))

    return render_template('register.html', form=form)


@bp.route('/login/', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            # temp debug
            form.password.data = sha256(
                form.password.data.encode()).hexdigest()
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
            flash('Login successful')
            if user.role.value == Role.ADMIN.value:
                return redirect(url_for('main.manage'))
            return redirect(url_for('main.index'))

    return render_template('login.html', form=form)


@bp.route('/logout/')
def logout():
    session.pop('user', None)
    session.pop('logged_in', None)
    flash('You have been logged out successfully')
    return redirect(url_for('main.index'))


@bp.route('/checkout/', methods=['GET', 'POST'])
def checkout():
    if check_user_logged_in() == False:
        flash('Please log in before checkout', 'error')
        return redirect(url_for('main.login'))
    userID = session['user']['userID']
    listImage = get_image_in_cart(userID)
    totalPrice = 0.0
    if (listImage or len(listImage) > 0):
        totalPrice = round(sum(image.price for image in listImage), 2)
    customerInfor = get_customer(userID)

    # form = CheckoutForm()
    formPayment = CheckoutFormPayment()

    if request.method == 'POST':
        if formPayment.validate_on_submit():
            remove_all_image_cart(userID)
            add_purchase(userID, listImage)
            flash('Payment successful')
            return redirect(url_for('main.checkout'))
        else:
            flash('The provided information is missing or incorrect', 'error')

    formPayment.firstname.data = session['user']['firstname']
    formPayment.surname.data = session['user']['surname']
    formPayment.email.data = session['user']['email']
    formPayment.phone.data = session['user']['phone']

    return render_template(
        'checkout.html',
        formPayment=formPayment,
        listImage=listImage,
        totalPrice=totalPrice,
        customerInfor=customerInfor
    )
