from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, StringField, PasswordField
from wtforms.fields import TextAreaField, RadioField, DecimalField, SelectField, FileField, SelectMultipleField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import InputRequired, email, Length, Regexp
from project.models import Currency, Role
from wtforms.widgets import ListWidget, CheckboxInput



class AddImageForm(FlaskForm):
    """Form for uploading an image."""
    title = StringField("Image Title", validators=[InputRequired()])
    description = TextAreaField(
        "Image Description", validators=[InputRequired()])
    price = DecimalField("Image Price", validators=[InputRequired()])
    currency = SelectField("Currency", choices=[(
        c.value, c.name) for c in Currency], validators=[InputRequired()])
    categories = SelectMultipleField("Category", choices=[], validators=[Length(min=1, message="Select at least one category")],
                                     option_widget=CheckboxInput(),
                                     widget=ListWidget(prefix_label=True),
                                     render_kw={"class": "list-unstyled"})
    image_file = FileField("Image File", validators=[InputRequired()])
    submit = SubmitField("Upload Image")

class EditImageForm(FlaskForm):
    title = StringField("Image Title", validators = [InputRequired()])
    description = TextAreaField("Image Description", validators = [InputRequired()])
    price = DecimalField("Image Price", validators = [InputRequired()])
    currency = SelectField("Currency", choices = [(c.value, c.name) for c in Currency], validators = [InputRequired()])
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
    firstname = StringField("Your first name", validators = [InputRequired()])
    surname = StringField("Your surname", validators = [InputRequired()])
    email = StringField("Your email", validators = [InputRequired()])
    phone = StringField("Your phone number", validators = [InputRequired()])
    """Payment Information"""
    cardNumber = StringField("Card Number", validators=[
        InputRequired(),
        Regexp(r"^\d{16}$", message="Card number must be 16 digits")
    ])
    expiryDate = StringField("Expiry Date (MM/YY)", validators=[InputRequired()])
    CVV = StringField("CVV", validators=[
        InputRequired(),
        Regexp(r"^\d{3}$", message="CVV must be 3 digits")
    ])
    submit = SubmitField("Complete Payment")



# -----------------------------------TEMPLATE-----------------------------------



class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    """Form for user registry."""
    username = StringField("Username", validators = [InputRequired()])
    password = PasswordField("Password", validators = [InputRequired()])
    email = StringField("Email", validators = [InputRequired(), email()])
    firstname = StringField("Your first name", validators = [InputRequired()])
    surname = StringField("Your surname", validators = [InputRequired()])
    phone = StringField("Your phone number", validators = [InputRequired()])
    role = RadioField("Role", choices=[(Role.CUSTOMER.value, Role.CUSTOMER.value), (Role.VENDOR.value, Role.VENDOR.value)], validators=[InputRequired()])
    submit = SubmitField("Make Account")


# you need to be a bit careful with variable names on these forms
# as they are used in the same template, so on submission it is
# possible to get them mixed up as they both are 'submitted'

class AddTourForm(FlaskForm):
    """Form for adding a tour."""
    tour_city = RadioField("City", choices=[], validators=[InputRequired()])
    tour_name = StringField("Tour Name", validators=[InputRequired()])
    tour_description = StringField("Description", validators=[InputRequired()])
    tour_price = DecimalField("Price", validators=[InputRequired()])
    tour_date = DateTimeLocalField(
        "Date", format="%Y-%m-%dT%H:%M", validators=[InputRequired()])
    tour_submit = SubmitField("Add Tour")


class AddCityForm(FlaskForm):
    """Form for adding a city."""
    city_name = StringField("City Name", validators=[InputRequired()])
    city_description = TextAreaField(
        "City Description", validators=[InputRequired()])
    city_submit = SubmitField("Add City")
