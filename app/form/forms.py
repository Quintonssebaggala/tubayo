from flask_wtf.file import FileField, FileRequired, FileAllowed

from app.data.models import db, Advert, Cart, Date_available, Experience, Flyer, Image, Imageexp, Rate, Shop, Slideshow, Story

from wtforms.fields import FormField
from wtforms_alchemy import ModelFieldList

from flask_wtf import FlaskForm
from wtforms_alchemy import model_form_factory
from wtforms_alchemy.fields import StringField, ModelFormField

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
    # image = ModelFieldList(FormField(ImageForm))
    # cart = ModelFieldList(FormField(CartForm))
    # date = ModelFieldList(FormField(Date_available))