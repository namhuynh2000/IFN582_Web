from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField, PasswordField, TextAreaField, RadioField, DecimalField, SelectField, FileField, SelectMultipleField
from wtforms.validators import InputRequired, email
from project.models import Currency, Role, ImageStatus
from wtforms.widgets import ListWidget, CheckboxInput


class AddImageForm(FlaskForm):
    """Form for uploading an image."""
    title = StringField("Image Title", validators=[InputRequired()])
    description = TextAreaField(
        "Image Description", validators=[InputRequired()])
    price = DecimalField("Image Price", validators=[InputRequired()])
    currency = SelectField("Currency", choices=[(
        c.value, c.name) for c in Currency], validators=[InputRequired()])
    categories = SelectMultipleField("Category", choices=[],
                                     option_widget=CheckboxInput(),
                                     widget=ListWidget(prefix_label=True),
                                     render_kw={"class": "list-unstyled"})
    image_file = FileField("Image File", validators=[InputRequired()])
    submit = SubmitField("Upload Image")


class EditImageForm(FlaskForm):
    title = StringField("Image Title", validators=[InputRequired()])
    description = TextAreaField(
        "Image Description", validators=[InputRequired()])
    price = DecimalField("Image Price", validators=[InputRequired()])
    currency = SelectField("Currency", choices=[(
        c.value, c.name) for c in Currency], validators=[InputRequired()])
    categories = SelectMultipleField("Category", choices=[],
                                     option_widget=CheckboxInput(),
                                     widget=ListWidget(prefix_label=True),
                                     render_kw={"class": "list-unstyled"})
    imageStatus = RadioField("Image Status", choices=[(
        ImageStatus.ACTIVE.value, "ACTIVE"), (ImageStatus.DRAFT.value, "DRAFT")], validators=[InputRequired()],
        widget=ListWidget(prefix_label=True),
        render_kw={"class": "list-unstyled"})
    submit = SubmitField('Save Changes')


class AddCategoryForm(FlaskForm):
    """Form for adding a tour."""
    categoryName = StringField("Category name", validators=[InputRequired()])
    description = TextAreaField("Description", validators=[InputRequired()])
    category = SubmitField("Add Category")


class CheckoutForm(FlaskForm):
    """Form for user checkout."""
    firstname = StringField("Your first name", validators=[InputRequired()])
    surname = StringField("Your surname", validators=[InputRequired()])
    email = StringField("Your email", validators=[InputRequired()])
    phone = StringField("Your phone number", validators=[InputRequired()])
    submit = SubmitField("Send to Agent")


class CheckoutFormPayment(FlaskForm):
    """Form for user checkout."""
    firstname = StringField("Your first name", validators=[InputRequired()])
    surname = StringField("Your surname", validators=[InputRequired()])
    email = StringField("Your email", validators=[InputRequired()])
    phone = StringField("Your phone number", validators=[InputRequired()])
    # total_price = DecimalField("Price", validators=[InputRequired()])
    """Payment Information"""
    paymentMethod = RadioField("Payment Method", choices=[(
        "Credit Card", "Credit Card"), ("Debit Card", "Debit Card")], validators=[InputRequired()])
    # cardNumber = StringField("Card Number", validators=[
    #     InputRequired(),
    #     Regexp(r"^\d{16}$", message="Card number must be 16 digits")
    # ])
    # expiryDate = StringField("Expiry Date (MM/YY)", validators=[InputRequired()])
    # CVV = StringField("CVV", validators=[
    #     InputRequired(),
    #     Regexp(r"^\d{3}$", message="CVV must be 3 digits")
    # ])
    submit = SubmitField("Complete Payment")
    
    
class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    """Form for user registry."""
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), email()])
    firstname = StringField("Your first name", validators=[InputRequired()])
    surname = StringField("Your surname", validators=[InputRequired()])
    phone = StringField("Your phone number", validators=[InputRequired()])
    role = RadioField("Role", choices=[(Role.CUSTOMER.value, Role.CUSTOMER.value), (
        Role.VENDOR.value, Role.VENDOR.value)], validators=[InputRequired()])
    submit = SubmitField("Make Account")

