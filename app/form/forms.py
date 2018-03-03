from flask_wtf.file import FileField, FileRequired, FileAllowed

from app.data.models import db, Advert, Cart, Date_available, Experience, Flyer, Image, Imageexp, Rate, Shop, Slideshow, Story

from wtforms.fields import FormField
from wtforms_alchemy import ModelFieldList
from wtforms import DateField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError

from flask_wtf import FlaskForm
from wtforms_alchemy import model_form_factory
from wtforms_alchemy.fields import StringField, ModelFormField
from app.data.models import User

# Using WTForms-Alchemy with Flask-WTF (http://wtforms-alchemy.readthedocs.org/en/latest/advanced.html#using-wtforms-alchemy-with-flask-wtf) to include all good features of Flask-WTF https://flask-wtf.readthedocs.org/en/latest/#features
BaseModelForm = model_form_factory(FlaskForm)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class AdvertForm(ModelForm):
    class Meta:
        model = Advert

    filename = FileField(None, [
        FileRequired(),
        FileAllowed(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'], 'Image Only!')
    ])


class CartForm(ModelForm):
    class Meta:
        model = Cart


class Date_availableForm(ModelForm):
    class Meta:
        model = Date_available


class FlyerForm(ModelForm):
    class Meta:
        model = Flyer

    filename = FileField(None, [
        FileRequired(),
        FileAllowed(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'], 'Image Only!')
    ])


class ImageForm(ModelForm):
    class Meta:
        model = Image

    filename = FileField(None, [
        FileRequired(),
        FileAllowed(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'], 'Image Only!')
    ])



class ShopForm(ModelForm):
    class Meta:
        model = Shop

    filename = FileField(None, [
        FileRequired(),
        FileAllowed(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'], 'Image Only!')
    ])

class SlideshowForm(ModelForm):
    class Meta:
        model = Slideshow

    filename = FileField(None, [
        FileRequired(),
        FileAllowed(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'], 'Image Only!')
    ])

class StoryForm(ModelForm):
    class Meta:
        model = Story
        # exclude = ['email']

    filename = FileField(None, [
        FileRequired(),
        FileAllowed(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'], 'Image Only!')
    ])


class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        exclude = ['total', 'rate_average']

    images = FileField(None, [
        FileRequired(),
        FileAllowed(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'], 'Image Only!')
    ])
    # dates = DateField(label='Date', format='%Y-%m-%d')
    # image = ModelFieldList(FormField(ImageForm))
    # cart = ModelFieldList(FormField(CartForm))
    # date = ModelFieldList(FormField(Date_available))

class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

