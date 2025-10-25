from __future__ import annotations  # For forward references in type hints
from project.models import (Admin, Category, Customer, CustomerRank, Image, Purchase, Rating, Role, Vendor)
from datetime import datetime
from project.utils import generate_uuid
from . import mysql
from project.models import User

def get_images_sort(page=1, per_page=8, category_id=None):
    offset = (page - 1) * per_page

    base_query = """
        SELECT 
            i.imageID,
            i.title,
            i.description,
            i.price,
            i.currency,
            i.updateDate,
            i.imageStatus,
            i.quantity,
            i.extension,
            i.userID
        FROM Image i
        WHERE i.isDeleted = FALSE
          AND i.imageStatus = 'Active'
    """

    if category_id and category_id != 'all':
        base_query = """
            SELECT 
                i.imageID,
                i.title,
                i.description,
                i.price,
                i.currency,
                i.updateDate,
                i.imageStatus,
                i.quantity,
                i.extension,
                i.userID
            FROM Image i
            JOIN ImageCategory ic ON i.imageID = ic.imageID
            WHERE i.isDeleted = FALSE
              AND i.imageStatus = 'Active'
              AND ic.categoryID = %s
        """
        params = (category_id, per_page, offset)
    else:
        params = (per_page, offset)

    base_query += " ORDER BY i.updateDate DESC LIMIT %s OFFSET %s;"
    with mysql.connection.cursor() as cur:
        cur.execute(base_query, params)
        return cur.fetchall()

def count_images(category_id=None):
    if category_id and category_id != 'all':
        query = """
            SELECT COUNT(*) AS total
            FROM Image i
            JOIN ImageCategory ic ON i.imageID = ic.imageID
            WHERE i.isDeleted = FALSE
              AND i.imageStatus = 'Active'
              AND ic.categoryID = %s;
        """
        params = (category_id,)
    else:
        query = """
            SELECT COUNT(*) AS total
            FROM Image i
            WHERE i.isDeleted = FALSE
              AND i.imageStatus = 'Active';
        """
        params = ()

    with mysql.connection.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchone()["total"]


def get_status_user(userID: str):
    cur = mysql.connection.cursor()
    cur.execute("SELECT isDeleted FROM User WHERE userID = %s", (userID,))
    row = cur.fetchone()
    cur.close()
    if row:
        return row
    return None


def get_categories():
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT categoryID, categoryName, description FROM Category ORDER BY categoryName")
    rows = cur.fetchall()
    cur.close()
    return [Category(
        categoryID=row['categoryID'],
        categoryName=row['categoryName'],
        description=row['description']
    ) for row in rows] if rows else []


def add_category(category: Category):
    cur = mysql.connection.cursor()
    query = """
        INSERT INTO Category (categoryID, categoryName, description) VALUES (%s, %s, %s)
    """
    data = (category.categoryID, category.categoryName, category.description)
    try:
        cur.execute(query, data)
        mysql.connection.commit()
        return True
    except Exception as e:
        print("Error adding category:", e)
        mysql.connection.rollback()
        return False
    finally:
        cur.close()


def edit_category(category: Category):
    cur = mysql.connection.cursor()
    query = """
        UPDATE Category
        SET categoryName=%s, description=%s
        WHERE categoryID=%s
    """
    data = (category.categoryName, category.description, category.categoryID)
    try:
        cur.execute(query, data)
        mysql.connection.commit()
        return True
    except Exception as e:
        print("Error updating category:", e)
        mysql.connection.rollback()
        return False
    finally:
        cur.close()


def delete_category(categoryID: str):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM Category WHERE categoryID = %s",
                    (categoryID,))
        mysql.connection.commit()
        return True
    except Exception as e:
        print("Error deleting category:", e)
        mysql.connection.rollback()
        return False
    finally:
        cur.close()


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


def get_image_categories(imageID):

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT c.categoryID, c.categoryName, c.description
        FROM category c
        JOIN imagecategory ic ON c.categoryID = ic.categoryID
        WHERE ic.imageID = %s
    """, (imageID,))
    results = cur.fetchall()
    cur.close()

    listCategory = [
        Category(
            categoryID=row['categoryID'],
            categoryName=row['categoryName'],
            description=row.get('description', '')
        )
        for row in results
    ]

    return listCategory

# This is for list all images

# Vendor site, to get only categoryID and categoryName for each image


def get_all_categories():
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT categoryID, categoryName FROM category ORDER BY categoryName ASC")
    results = cur.fetchall()
    cur.close()
    return [(str(r['categoryID']), r['categoryName']) for r in results]

# Vendor site, to fetch seleted categories based on each imageID


def update_image_categories(imageID, categoryIDs):

    cur = mysql.connection.cursor()
    try:
        # Delete old category assignments
        cur.execute("DELETE FROM imagecategory WHERE imageID = %s", (imageID,))

        # Insert new category assignments
        for cat_id in categoryIDs:
            cur.execute(
                "INSERT INTO imagecategory (imageID, categoryID) VALUES (%s, %s)",
                (imageID, cat_id)
            )
        mysql.connection.commit()
    except Exception as e:
        print("Error updating image categories:", e)
        mysql.connection.rollback()
    finally:
        cur.close()


def get_images():
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT 
                    *
                FROM image
                """)
    results = cur.fetchall()
    listImage = []
    if results:
        listImage = [Image(
            userID=row['userID'], listCategory=get_image_categories(imageID=row['imageID']), imageID=row['imageID'], title=row['title'], description=row['description'],
            price=float(row['price']), quantity=int(row['quantity']), currency=row['currency'], imageStatus=row['imageStatus'], extension=row['extension'],
            updateDate=datetime.combine(row['updateDate'], datetime.min.time()), listRatings=get_ratings(imageID=row['imageID'])) for row in results]
    else:
        listImage = []

    cur.close()
    return listImage


def get_image(imageID: str):
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT 
                    *
                FROM image WHERE imageID = %s AND isDeleted = False;
                """, [imageID])
    result = cur.fetchone()
    image = Image(
        userID=result['userID'], listCategory=get_image_categories(imageID=result['imageID']), imageID=result['imageID'], title=result['title'], description=result['description'],
        price=float(result['price']), quantity=int(result['quantity']), currency=result['currency'], imageStatus=result['imageStatus'], extension=result['extension'],
        updateDate=datetime.combine(result['updateDate'], datetime.min.time()), listRatings=get_ratings(imageID=result['imageID'])
    ) if result else None

    cur.close()
    return image


def get_images_by_page(page: int, per_page: int):
    offset = (page - 1) * per_page
    cur = mysql.connection.cursor()
    cur.execute("""
            SELECT *
            FROM image
            WHERE image.imageStatus = 'Active' AND image.isDeleted = FALSE
            ORDER BY image.updateDate DESC
            LIMIT %s OFFSET %s;
        """, (per_page, offset))
    results = cur.fetchall()
    cur.close()

    images = []
    for row in results:
        image = Image(
            userID=row['userID'],
            listCategory=get_image_categories(imageID=row['imageID']),
            imageID=row['imageID'],
            title=row['title'],
            description=row['description'],
            price=float(row['price']),
            quantity=int(row['quantity']),
            currency=row['currency'],
            imageStatus=row['imageStatus'],
            extension=row['extension'],
            updateDate=datetime.combine(
                row['updateDate'], datetime.min.time()),
            listRatings=get_ratings(imageID=row['imageID'])
        )
        images.append(image)

    return images


def get_active_image():
    cur = mysql.connection.cursor()
    cur.execute("""
            SELECT *
            FROM image
            WHERE image.imageStatus = 'Active' AND image.isDeleted = FALSE
            ORDER BY image.updateDate DESC;
        """)
    result = cur.fetchall()
    cur.close()

    active_images = []
    for row in result:
        image = Image(
            userID=row['userID'],
            listCategory=get_image_categories(imageID=row['imageID']),
            imageID=row['imageID'],
            title=row['title'],
            description=row['description'],
            price=float(row['price']),
            quantity=int(row['quantity']),
            currency=row['currency'],
            imageStatus=row['imageStatus'],
            extension=row['extension'],
            updateDate=datetime.combine(
                row['updateDate'], datetime.min.time()),
            listRatings=get_ratings(imageID=row['imageID'])
        )
        active_images.append(image)

    return active_images

# Display vendor name in item detail page


def get_vendorName(userID):
    cur = mysql.connection.cursor()
    cur.execute("SELECT username FROM user WHERE userID = %s", (userID,))
    row = cur.fetchone()
    cur.close()
    if row:
        return row['username']
    return None

# To display all images in vendor management


def get_images_by_vendor(vendor_id):
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

    images = []
    for row in results:
        # Fetch categories for each image
        categories = get_image_categories(imageID=row['imageID'])
        images.append(
            Image(
                imageID=str(row['imageID']),
                userID=row['userID'],
                title=row['title'],
                description=row['description'],
                price=float(row['price']),
                currency=row['currency'],
                imageStatus=row['imageStatus'],
                updateDate=row['updateDate'],
                extension=row['extension'],
                listRatings=[],
                quantity=0,
                listCategory=categories
            )
        )

    return images

# Update an existing image's details via vendor management


def edit_image(imageID, title, description, price, currency, imageStatus, category_ids):
    cur = mysql.connection.cursor()
    try:

        cur.execute("""
            UPDATE image
            SET title=%s, description=%s, price=%s, currency=%s, imageStatus=%s, updateDate=NOW()
            WHERE imageID=%s
        """, (title, description, price, currency, imageStatus, imageID))

        # To delete and add new category
        cur.execute("DELETE FROM imagecategory WHERE imageID=%s", (imageID,))

        for cat_id in category_ids:
            cur.execute(
                "INSERT INTO imagecategory (imageID, categoryID) VALUES (%s, %s)",
                (imageID, cat_id)
            )

        mysql.connection.commit()
        return True
    except Exception as e:
        print("Error updating image:", e)
        mysql.connection.rollback()
        return False
    finally:
        cur.close()

# delete image from vendor management but still existing in database (change status to false)


def delete_selected_image(image_id, isDeleted: bool):
    # fetch the image
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM image WHERE imageID = %s",
                (isDeleted, image_id))
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
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
        UPDATE image
        SET isDeleted = %s
        WHERE imageID = %s
    """, [isDeleted, imageID])
        mysql.connection.commit()
        return True
    except Exception as e:
        print("Error updating image:", e)
        mysql.connection.rollback()
        return False
    finally:
        cur.close()


def config_user(userID: str, isDeleted: bool):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
        UPDATE user
        SET isDeleted = %s
        WHERE userID = %s
    """, [isDeleted, userID])
        mysql.connection.commit()
        return True
    except Exception as e:
        print("Error updating image:", e)
        mysql.connection.rollback()
        return False
    finally:
        cur.close()


def get_image_in_cart(userID: str):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT *
        FROM CartImage 
        WHERE userID = %s;
    """, [userID])
    results = cur.fetchall()
    listImage = []
    for row in results:
        image = get_image(row['imageID'])
        if image is not None:
            listImage.append(image)
    cur.close()
    return listImage

# add new image in vendor management


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
        WHERE username = %s AND password = %s AND isDeleted = FALSE
    """, (username, password))
    row = cur.fetchone()
    cur.close()
    if row:
        if row['role'] == Role.ADMIN.value:
            return get_admin(row['userID'])
        elif row['role'] == Role.CUSTOMER.value:
            return get_customer(row['userID'])
        elif row['role'] == Role.VENDOR.value:
            return get_vendor(row['userID'])
    return None


def get_all_users():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT *
        FROM user
    """)
    results = cur.fetchall()
    cur.close()

    users = []
    if results:
        for row in results:
            users.append(User(
                username=row['username'],
                role=Role(row['role']),
                userID=row['userID'],
                email=row['email'],
                surname=row['surname'],
                firstname=row['firstname'],
                phone=row['phone'],
                isDeleted=row['isDeleted']
            ))

    return users


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
    



def remove_all_image_cart(userID: str):
    cur = mysql.connection.cursor()
    query = """
        DELETE FROM CartImage
        WHERE userID = %s
    """
    data = (userID,)
    try:
        cur.execute(query, data)
        mysql.connection.commit()
        return True
    except Exception as e:
        print("Error removing all images from cart:", e)
        mysql.connection.rollback()
        return False
    finally:
        cur.close()


def add_purchase(userID: str, listImage: list[Image]):
    cur = mysql.connection.cursor()
    totalPrice = round(sum(image.price for image in listImage), 2)
    purchaseID = generate_uuid()
    try:
        queryPurchase = """
            INSERT INTO Purchase(
                purchaseID, userID, purchaseDate, totalAmount
            ) VALUES (%s, %s, %s, %s)
        """
        dataPurchase = [
            purchaseID,
            userID,
            datetime.now(),
            totalPrice
        ]

        queryPurchaseImage = """
            INSERT INTO PurchaseImage(
                purchaseID, imageID) VALUES (%s, %s)
        """
        dataPurchaseImage = [(purchaseID, image.imageID)
                             for image in listImage]

        cur.execute(queryPurchase, dataPurchase)
        cur.executemany(queryPurchaseImage, dataPurchaseImage)

        mysql.connection.commit()
    except Exception as e:
        print("Error adding purchase:", e)
        mysql.connection.rollback()
    finally:
        cur.close()


def get_purchases_by_user(userID: str):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT *
        FROM Purchase
        WHERE userID = %s
    """, (userID,))
    results = cur.fetchall()
    cur.close()

    purchases = [Purchase(
        purchaseID=row['purchaseID'],
        purchaseDate=row['purchaseDate'],
        totalAmount=float(row['totalAmount']),
    ) for row in results]

    return purchases


def get_images_in_purchase(purchaseID: str):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT *
        FROM image i
        JOIN PurchaseImage pi ON i.imageID = pi.imageID
        WHERE pi.purchaseID = %s
    """, (purchaseID,))
    results = cur.fetchall()
    cur.close()

    images = [Image(
        userID=row['userID'], listCategory=get_image_categories(imageID=row['imageID']), imageID=row['imageID'], title=row['title'], description=row['description'],
        price=float(row['price']), quantity=int(row['quantity']), currency=row['currency'], imageStatus=row['imageStatus'], extension=row['extension'],
        updateDate=datetime.combine(row['updateDate'], datetime.min.time()), listRatings=get_ratings(imageID=row['imageID'])) for row in results]

    return images


def get_images_by_user_purchase(userID: str):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT i.*
        FROM image i
        JOIN PurchaseImage pi ON i.imageID = pi.imageID
        JOIN Purchase p ON pi.purchaseID = p.purchaseID
        WHERE p.userID = %s
    """, (userID,))
    results = cur.fetchall()
    cur.close()

    images = [Image(
        userID=row['userID'], listCategory=get_image_categories(imageID=row['imageID']), imageID=row['imageID'], title=row['title'], description=row['description'],
        price=float(row['price']), quantity=int(row['quantity']), currency=row['currency'], imageStatus=row['imageStatus'], extension=row['extension'],
        updateDate=datetime.combine(row['updateDate'], datetime.min.time()), listRatings=get_ratings(imageID=row['imageID'])) for row in results]

    return images


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
    try:
        # if user is not vendor, then become only customer
        role_value = Role.VENDOR.value if is_vendor else Role.CUSTOMER.value

        # Insert into user table with isDeleted default FALSE
        cur.execute("""
            INSERT INTO user (userID, username, password, email, firstname, surname, phone, role, isDeleted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, FALSE)
        """, (userID, form.username.data, form.password.data, form.email.data, form.firstname.data, form.surname.data, form.phone.data, role_value))

        # Insert into customer table
        cur.execute("""
            INSERT INTO customer (userID, customerRank)
            VALUES (%s, %s)
        """, (userID, CustomerRank.BRONZE.value))

        # If vendor, insert into vendor table
        if is_vendor:
            cur.execute("""
                INSERT INTO vendor (userID, bio, portfolio)
                VALUES (%s, %s, %s)
            """, (userID, '', ''))

        mysql.connection.commit()
        return userID
    except Exception:
        mysql.connection.rollback()
        raise
    finally:
        cur.close()


def add_vendor(form):
    add_customer(form, is_vendor=True)


# temp debug
def change_role(userID: str, new_role: Role):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE user
        SET role = %s
        WHERE userID = %s
    """, (new_role.value, userID))
    if (new_role == Role.ADMIN):
        cur.execute("""
            INSERT INTO admin (userID)
            VALUES (%s)
        """, (userID,))
    elif (new_role == Role.VENDOR):
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

