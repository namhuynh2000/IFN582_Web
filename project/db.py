from __future__ import annotations  # For forward references in type hints
from project.models import City, Tour, Order, OrderStatus, UserInfo, UserAccount, Image, Rating, Category, Admin, Customer, Vendor, Role, CustomerRank
from datetime import datetime
from project.utils import generate_uuid
from . import mysql


def get_ratings(userID=None, imageID=None):
    cur = mysql.connection.cursor()
    listRating = []
    if (userID is None and imageID is None):
        pass
    elif (userID is not None and imageID is None):
        cur.execute("""
                    SELECT
                        r.ratingID,
                        r.imageID,
                        r.userID,
                        r.score,
                        r.comment,
                        r.updateDate
                    FROM rating AS r
                    JOIN user AS c ON r.userID = c.userID
                    WHERE r.userID = %s;
                    """, [userID])
        results = cur.fetchall()
        cur.close()
        listRating = [Rating(
            userID=row['userID'], imageID=row['imageID'], score=int(
                row['score']),
            ratingID=row['ratingID'], comment=row['comment'], updateDate=datetime.combine(
                row['updateDate'], datetime.min.time())
        ) for row in results]
    elif (userID is None and imageID is not None):
        cur.execute("""
                    SELECT 
                        r.ratingID,
                        r.imageID,
                        r.userID,
                        r.score,
                        r.comment,
                        r.updateDate
                    FROM rating AS r
                    JOIN image AS i ON r.imageID = i.imageID
                    WHERE r.imageID = %s;
                    """, [imageID])
        results = cur.fetchall()
        cur.close()
        listRating = [Rating(
            userID=row['userID'], imageID=row['imageID'], score=int(
                row['score']),
            ratingID=row['ratingID'], comment=row['comment'], updateDate=datetime.combine(
                row['updateDate'], datetime.min.time())
        ) for row in results]
    else:
        cur.execute("""
                    SELECT *
                    FROM rating AS r
                    JOIN user AS c ON r.userID = c.userID
                    JOIN image AS i ON r.imageID = i.imageID
                    WHERE r.userID = %s AND r.imageID = %s;
                    """, [userID, imageID])
        results = cur.fetchall()
        cur.close()
        listRating = [Rating(
            userID=row['userID'], imageID=row['imageID'], score=int(
                row['score']),
            ratingID=row['ratingID'], comment=row['comment'], updateDate=datetime.combine(
                row['updateDate'], datetime.min.time())
        ) for row in results]
    return listRating


def get_image_categories(imageID=None):
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT 
                    *
                FROM category AS c
                JOIN ImageCategory AS ic ON c.categoryID = ic.categoryID
                WHERE ic.imageID = %s;
                """, [imageID])
    results = cur.fetchall()
    listCategory = [Category(categoryName=row['categoryName'], categoryID=row['categoryID'],
                             description=row['description']) for row in results]
    cur.close()
    return listCategory

#This is for list all images
def get_categories():
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT * FROM category;
                """)
    results = cur.fetchall()
    listCategory = [Category(categoryName=row['categoryName'], categoryID=row['categoryID'],
                             description=row['description']) for row in results]
    cur.close()
    print("listCategory: ", listCategory)
    return listCategory


def get_images():
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT 
                    *
                FROM image;
                """)
    results = cur.fetchall()
    print("Results:", results)
    listImage = [Image(
        userID=row['userID'], listCategory=get_image_categories(imageID=row['imageID']), imageID=row['imageID'], title=row['title'], description=row['description'],
        price=float(row['price']), quantity=int(row['quantity']), currency=row['currency'], imageStatus=row['imageStatus'], extension=row['extension'],
        updateDate=datetime.combine(row['updateDate'], datetime.min.time()), listRatings=get_ratings(imageID=row['imageID'])) for row in results]

    cur.close()
    return listImage

def get_image(imageID: str):
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT 
                    *
                FROM image WHERE imageID = %s;
                """, [imageID])
    result = cur.fetchone()
    image = Image(
        userID=result['userID'], listCategory=get_image_categories(imageID=result['imageID']), imageID=result['imageID'], title=result['title'], description=result['description'],
        price=float(result['price']), quantity=int(result['quantity']), currency=result['currency'], imageStatus=result['imageStatus'], extension=result['extension'],
        updateDate=datetime.combine(result['updateDate'], datetime.min.time()), listRatings=get_ratings(imageID=result['imageID'])
    ) if result else None

    cur.close()
    return image
#To display all images in vendor management
def get_images_by_vendor(vendor_id):
    """
    Retrieve all images uploaded by a specific vendor.
    """
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT i.imageID, i.userID, i.title, i.description, i.price,
               i.currency, i.extension, i.imageStatus, i.updateDate
        FROM image i
        WHERE i.userID = %s AND i.isDeleted = False
        ORDER BY i.updateDate DESC
    """, (vendor_id,))
    results = cur.fetchall()
    cur.close()

    # Convert SQL rows to Image objects (if you have an Image class)
    images = []
    for row in results:
        images.append(
            Image(
                imageID=str(row['imageID']),
                userID=row['userID'],
                title=row['title'],
                description=row['description'],
                price=float(row['price']),
                currency=(row['currency']),
                imageStatus=row['imageStatus'],
                updateDate=row['updateDate'],
                extension=row['extension'],
                listRatings=[],
                quantity=0,
                listCategory=[]
            )
        )

    return images

#Update an existing image's details via vendor management
def edit_image(imageID, title, description, price, currency):  
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            UPDATE image
            SET title = %s,
                description = %s,
                price = %s,
                currency = %s,
                updateDate = NOW()
            WHERE imageID = %s
        """, (title, description, price, currency, imageID))
        mysql.connection.commit()
        return True
    except Exception as e:
        print("Error updating image:", e)
        mysql.connection.rollback()
        return False
    finally:
        cur.close()
        
#delete image from vendor management but still existing in database (change status to false)
def delete_selected_image(image_id):
    # fetch the image
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM image WHERE imageID = %s", (image_id,))
    image = cur.fetchone()

    if not image:
        cur.close()
        return False

    # delete selected image
    cur.execute(""" 
                UPDATE image 
                SET isDeleted = TRUE
                WHERE imageID = %s;""", (image_id,))
    mysql.connection.commit()
    cur.close()

    return True
def config_image(imageID: str, isDeleted: bool):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE image
        SET isDeleted = %s
        WHERE imageID = %s
    """, [isDeleted, imageID])
    mysql.connection.commit()
    cur.close()
    
def config_user(userID: str, isDeleted: bool):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE user
        SET isDeleted = %s
        WHERE userID = %s
    """, [isDeleted, userID])
    mysql.connection.commit()
    cur.close()


def get_image_in_cart(userID: str):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT *
        FROM CartImage 
        WHERE userID = %s;
    """, [userID])
    results = cur.fetchall()
    listImage = [get_image(row['imageID']) for row in results]
    cur.close()
    return listImage

#add new image in vendor management
def add_image(image: Image):
    cur = mysql.connection.cursor()
    queryAddImage = """
        INSERT INTO image (
            imageID, userID, title, description, price, currency,
            updateDate, imageStatus, quantity, extension
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    queryAddImageCategory = """
        INSERT INTO ImageCategory (
            categoryID, imageID
        ) VALUES (%s, %s)
    """

    dataImage = (
        image.imageID,
        image.userID,
        # '38850c01-a90d-11f0-9f66-700894b19280',  # Placeholder vendorID
        image.title,
        image.description,
        image.price,
        image.currency.value,
        image.updateDate,
        image.imageStatus,
        image.quantity,
        image.extension
    )
    
    dataImageCategory = [(
        category,
        image.imageID
    ) for category in image.listCategory]
    
    cur.execute(queryAddImage, dataImage)
    cur.executemany(queryAddImageCategory, dataImageCategory)
    mysql.connection.commit()
    cur.close()

def add_category(category: Category):
    cur = mysql.connection.cursor()
    query = """
        INSERT INTO Category (categoryID, categoryName, description) VALUES (%s, %s, %s)
    """
    data = (category.categoryID, category.categoryName, category.description)
    cur.execute(query, data)
    mysql.connection.commit()
    cur.close()

def add_to_cart(userID: str, imageID: str):
    cur = mysql.connection.cursor()
    query = """
        INSERT IGNORE INTO CartImage(
            userID, imageID
        ) VALUES (%s, %s)
    """
    data = (
        userID,  # temp placeholder userID
        imageID,
    )
    cur.execute(query, data)
    mysql.connection.commit()
    cur.close()


def get_user(username, password):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT *
        FROM user
        WHERE username = %s AND password = %s AND isDeleted = 0
    """, (username, password))
    row = cur.fetchone()
    print("row:", row)
    cur.close()
    if row:
        if row['role'] == Role.ADMIN.value:
            return get_admin(row['userID'])
        elif row['role'] == Role.CUSTOMER.value:
            return get_customer(row['userID'])
        elif row['role'] == Role.VENDOR.value:
            return get_vendor(row['userID'])
    return None

def remove_image_cart(userID: str, imageID: str):
    cur = mysql.connection.cursor()
    query = """
        DELETE FROM CartImage
        WHERE userID = %s AND imageID = %s
    """
    data = (userID, imageID)
    cur.execute(query, data)
    mysql.connection.commit()
    cur.close()


def get_admin(userID: str):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT *
        FROM user
        JOIN admin ON user.userID = admin.userID
        WHERE user.userID = %s
    """, (userID,))
    row = cur.fetchone()
    cur.close()
    if row:
        return Admin(username=row['username'], userID=row['userID'], email=row['email'], firstname=row['firstname'], surname=row['surname'], phone=row['phone'])
    return None

def get_customer(userID: str):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT *
        FROM user AS u
        JOIN customer AS c ON u.userID = c.userID
        WHERE u.userID = %s
    """, (userID,))
    row = cur.fetchone()
    print("Customer row:", row)
    cur.close()
    if row:
        return Customer(username=row['username'], userID=row['userID'], email=row['email'], firstname=row['firstname'], surname=row['surname'], phone=row['phone'], customerRank=row['customerRank'])
    return None


def get_vendor(userID: str):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT *
        FROM user AS u
        JOIN customer AS c ON u.userID = c.userID
        JOIN vendor AS v ON u.userID = v.userID
        WHERE u.userID = %s
    """, (userID,))
    row = cur.fetchone()
    cur.close()
    if row:
        return Vendor(username=row['username'], userID=row['userID'], email=row['email'], firstname=row['firstname'], surname=row['surname'], phone=row['phone'], customerRank=row['customerRank'], bio=row['bio'], portfolio=row['portfolio'])
    return None

def add_customer(form, is_vendor=False):
    cur = mysql.connection.cursor()
    userID = generate_uuid()
    cur.execute("""
        INSERT INTO user (userID, username, password, email, firstname, surname, phone, role, isDeleted)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (userID, form.username.data, form.password.data, form.email.data,
          form.firstname.data, form.surname.data, form.phone.data, Role.VENDOR.value if is_vendor else Role.CUSTOMER.value, 0))
    cur.execute("""
        INSERT INTO customer (userID, customerRank)
        VALUES (%s, %s)
    """, (userID, CustomerRank.BRONZE.value))
    if is_vendor:
        cur.execute("""
            INSERT INTO vendor (userID, bio, portfolio)
            VALUES (%s, %s, %s)
        """, (userID, '', ''))
        
    mysql.connection.commit()
    cur.close()

def add_vendor(form):
    add_customer(form, is_vendor=True)


#temp debug
def change_role(userID: str, new_role: Role):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE user
        SET role = %s
        WHERE userID = %s
    """, (new_role.value, userID))
    if(new_role == Role.ADMIN):
        cur.execute("""
            INSERT INTO admin (userID)
            VALUES (%s)
        """, (userID,))
    elif(new_role == Role.VENDOR):
        cur.execute("""
            INSERT INTO vendor (userID, bio, portfolio)
            VALUES (%s, %s, %s)
        """, (userID, '', ''))
    mysql.connection.commit()
    cur.close()    

    
def check_user(username: str):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT *
        FROM user
        WHERE username = %s AND isDeleted = 0
    """, (username,))
    row = cur.fetchone()
    cur.close()
    if row:
        return True
    return False

# ------------------------------------------TEMPLATE----------------------------------------------------


def get_cities():
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT city_id, city_name, city_description, city_image FROM cities")
    results = cur.fetchall()
    cur.close()
    return [City(str(row['city_id']), row['city_name'], row['city_description'], row['city_image']) for row in results]


def get_city(city_id):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT city_id, city_name, city_description, city_image FROM cities WHERE city_id = %s", (city_id,))
    row = cur.fetchone()
    cur.close()
    return City(str(row['city_id']), row['city_name'], row['city_description'], row['city_image']) if row else None


def get_tours():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT t.tour_id, t.tour_name, t.tour_description, t.tour_image,
               t.price, t.tour_date,
               c.city_id, c.city_name, c.city_description, c.city_image
        FROM tours t
        JOIN cities c ON t.city_id = c.city_id
    """)
    results = cur.fetchall()
    cur.close()
    return [
        Tour(str(row['tour_id']), row['tour_name'], row['tour_description'],
             City(str(row['city_id']), row['city_name'],
                  row['city_description'], row['city_image']),
             row['tour_image'], float(row['price']), row['tour_date']) for row in results
    ]


def get_tour(tour_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT t.tour_id, t.tour_name, t.tour_description, t.tour_image,
               t.price, t.tour_date,
               c.city_id, c.city_name, c.city_description, c.city_image
        FROM tours t
        JOIN cities c ON t.city_id = c.city_id
        WHERE t.tour_id = %s
    """, (tour_id,))
    row = cur.fetchone()
    cur.close()
    return Tour(str(row['tour_id']), row['tour_name'], row['tour_description'],
                City(str(row['city_id']), row['city_name'],
                     row['city_description'], row['city_image']),
                row['tour_image'], float(row['price']), row['tour_date']) if row else None


def get_tours_for_city(city_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT t.tour_id, t.tour_name, t.tour_description, t.tour_image,
               t.price, t.tour_date,
               c.city_id, c.city_name, c.city_description, c.city_image
        FROM tours t
        JOIN cities c ON t.city_id = c.city_id
        WHERE c.city_id = %s
    """, (city_id,))
    results = cur.fetchall()
    cur.close()
    return [
        Tour(str(row['tour_id']), row['tour_name'], row['tour_description'],
             City(str(row['city_id']), row['city_name'],
                  row['city_description'], row['city_image']),
             row['tour_image'], float(row['price']), row['tour_date']) for row in results
    ]


def add_city(city):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO cities (city_name, city_description, city_image) VALUES (%s, %s, %s)",
                (city.name, city.description, city.image))
    mysql.connection.commit()
    cur.close()


def add_tour(tour):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO tours (city_id, tour_name, tour_description, tour_image, price, tour_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (tour.city.id, tour.name, tour.description, tour.image, tour.price, tour.date))
    mysql.connection.commit()
    cur.close()


def add_order(order):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO orders (user_id, order_status, total_cost, customer_name, customer_email, customer_phone)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (order.user.id, order.status.value, order.total_cost,
          f"{order.user.firstname} {order.user.surname}",
          order.user.email, order.user.phone))
    order_id = cur.lastrowid

    for item in order.items:
        cur.execute("INSERT INTO order_items (order_id, tour_id, quantity) VALUES (%s, %s, %s)",
                    (order_id, item.tour.id, item.quantity))

    mysql.connection.commit()
    cur.close()


def get_orders():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT order_id, user_id, order_status, total_cost, order_date,
               customer_name, customer_email, customer_phone
        FROM orders
    """)
    results = cur.fetchall()
    cur.close()
    return [
        Order(str(row['order_id']), OrderStatus(row['order_status']),
              UserInfo(str(row['user_id']),
                       row['customer_name'].split()[0],
                       row['customer_name'].split()[-1],
                       row['customer_email'], row['customer_phone']),
              row['total_cost'], [], row['order_date']) for row in results
    ]


def get_order(order_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT order_id, user_id, order_status, total_cost, order_date,
               customer_name, customer_email, customer_phone
        FROM orders
        WHERE order_id = %s
    """, (order_id,))
    row = cur.fetchone()
    cur.close()
    return Order(str(row['order_id']), OrderStatus(row['order_status']),
                 UserInfo(str(row['user_id']),
                          row['customer_name'].split()[0],
                          row['customer_name'].split()[-1],
                          row['customer_email'], row['customer_phone']),
                 row['total_cost'], [], row['order_date']) if row else None


def check_for_user_(username, password):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT user_id, username, user_password, email, firstname, surname, phone
        FROM users
        WHERE username = %s AND user_password = %s
    """, (username, password))
    row = cur.fetchone()
    cur.close()
    if row:
        return UserAccount(row['username'], row['user_password'], row['email'],
                           UserInfo(str(row['user_id']), row['firstname'], row['surname'],
                                    row['email'], row['phone']))
    return None


def is_admin(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM admins WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    return True if row else False


def add_user_(form):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO users (username, user_password, email, firstname, surname, phone)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (form.username.data, form.password.data, form.email.data,
          form.firstname.data, form.surname.data, form.phone.data))
    mysql.connection.commit()
    cur.close()
