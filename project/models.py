from __future__ import annotations  # For forward references in type hints
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from enum import Enum
from uuid import uuid4


class Currency(Enum):
    USD = 'USD'
    EUR = 'EUR'
    AUD = 'AUD'


class ImageStatus(Enum):
    ACTIVE = 'Active'
    DRAFT = 'Draft'


@dataclass
class Rating:
    userID: str
    imageID: str
    score: int  # 1 to 5
    ratingID: str = field(default_factory=lambda: str(uuid4()))
    comment: str = ''
    updateDate: datetime = field(default_factory=lambda: datetime.now())


@dataclass
class Category:
    categoryName: str
    categoryID: str = field(default_factory=lambda: str(uuid4()))
    description: str = ''
    # listImages: List[Image] = field(default_factory=lambda: [])


@dataclass
class Image:
    userID: str
    listCategory: List[Category]
    extension: str
    # url: str = '' #?????????
    imageID: str = field(default_factory=lambda: str(uuid4()))
    title: str = ''
    description: str = ''
    price: float = 0.0
    quantity: int = 0
    currency: Currency = Currency.USD
    imageStatus: ImageStatus = ImageStatus.ACTIVE
    updateDate: datetime = field(default_factory=lambda: datetime.now())
    listRatings: List[Rating] = field(default_factory=lambda: [])

    def get_average_rating(self):
        if not self.listRatings:
            return 0.0
        return sum(rating.score for rating in self.listRatings) / len(self.listRatings)

    def get_totalAmount(self):
        return self.price*self.quantity


class Role(Enum):
    ADMIN = 'Admin'
    CUSTOMER = 'Customer'


@dataclass
class User:
    username: str
    password: str
    role: Role
    userID: str = field(default_factory=lambda: str(uuid4()))
    email: str = ''
    firstname: str = ''
    surname: str = ''
    phone: str = ''

    def update_profile(self, firstname: str = '', surname: str = '', email: str = '', phone: str = ''):
        if firstname:
            self.firstname = firstname
        if surname:
            self.surname = surname
        if email:
            self.email = email
        if phone:
            self.phone = phone

# class Vendor(User):  # Inherit/
#     def __init__(self):
#         super().__init__(role=Role.VENDOR)
#         self.bio: str = ''
#         self.portfolio: str = ''
#         self.totalSales: int = 0
#         self.listOwnImages: List[Image] = []

#     def view_earnings(self):
#         return sum(image.get_totalAmount() for image in self.listOwnImages)


class CustomerRank(Enum):
    BRONZE = 'Bronze'
    SILVER = 'Silver'
    GOLD = 'Gold'


class Customer(User):  # Inherit/
    def __init__(self, username: str, password: str, userID: str, email: str = '', firstname: str = '', surname: str = '', phone: str = '', bio: str = '', portfolio: str = '', totalSales: int = 0):
        super().__init__(username=username, password=password, userID=userID, email=email,
                         firstname=firstname, surname=surname, phone=phone, role=Role.CUSTOMER)
        # attributes for customer
        self.customerRank = CustomerRank.BRONZE
        # self.purchaseHistory: List[Purchase] = []
        # self.listRatings: List[Rating] = []
        # self.listPurchaseImages: List[Image] = [].append(image for purchase in self.purchaseHistory for image in purchase.listImages for purchase in self.purchaseHistory)
        # self.cart: List[Image] = []

        # attributes for vendor
        self.bio = bio
        self.portfolio = portfolio
        self.totalSales = totalSales
        # self.listOwnImages: List[Image] = []

    # def view_earnings(self):
    #     return sum(image.get_totalAmount() for image in self.listOwnImages)


class Admin(User):  # Inherit/
    def __init__(self, username: str, password: str, userID: str, email: str = '', firstname: str = '', surname: str = '', phone: str = ''):
        super().__init__(username=username, password=password, userID=userID, email=email,
                         firstname=firstname, surname=surname, phone=phone,  role=Role.ADMIN)


@dataclass
class Purchase:
    purchaseID: str = field(default_factory=lambda: str(uuid4()))
    purchaseDate: datetime = field(default_factory=lambda: datetime.now())
    # listImages: List[Image] = field(default_factory=lambda: [])
    currency: Currency = Currency.USD
    totalAmount: float = 0.0

    # def __post_init__(self):
    #     self.totalAmount = sum(image.get_totalAmount() for image in self.listImages)


# -----------------------------------------------------------TENMPLATE----------------------------------------------------
@dataclass
class City:
    id: str
    name: str
    description: str = 'fooobar'
    image: str = 'foobar.png'


@dataclass
class Tour:
    id: str
    name: str
    description: str
    city: City
    image: str = 'foobar.png'
    price: float = 10.00
    date: datetime = field(default_factory=lambda: datetime.now())


class OrderStatus(Enum):
    PENDING = 'Pending'
    CONFIRMED = 'Confirmed'
    CANCELLED = 'Cancelled'


@dataclass
class UserInfo:
    id: str
    firstname: str
    surname: str
    email: str
    phone: str


@dataclass
class BasketItem:
    tour: Tour
    quantity: int = 1
    id: str = field(default_factory=lambda: str(uuid4()))

    def total_price(self):
        return self.tour.price * self.quantity

    def increment_quantity(self):
        self.quantity += 1

    def decrement_quantity(self):
        if self.quantity > 1:
            self.quantity -= 1


@dataclass
class Basket:
    items: List[BasketItem] = field(default_factory=lambda: [])

    def add_item(self, item: BasketItem):
        self.items.append(item)

    def remove_item(self, item_id: str):
        self.items = [item for item in self.items if item.id != item_id]

    def get_item(self, item_id: str):
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def empty(self):
        self.items = []

    def total_cost(self):
        return sum(item.total_price() for item in self.items)


@dataclass
class Order:
    id: str
    status: OrderStatus
    user: UserInfo
    total_cost: float = 0.0
    items: List[BasketItem] = field(default_factory=list)
    date: datetime = field(default_factory=lambda: datetime.now())


@dataclass
class UserAccount:
    username: str
    password: str
    email: str
    info: UserInfo
