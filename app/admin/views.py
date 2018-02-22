import os

from app.admin import admin
from app.main import main
from app.admin.controller import register_crud


from app import app
from sqlalchemy.orm.exc import NoResultFound
from app.data.models import db, Experience, Image, Flyer, Shop, Slideshow, Imageexp, Date_available, Advert, Cart, Rate, Story 
from app.form.forms import AdvertForm, CartForm, Date_availableForm, ExperienceForm, FlyerForm, ImageForm, ShopForm, SlideshowForm, StoryForm  

from flask import render_template, abort, request, redirect, flash, url_for, send_from_directory, json
from app.menu_content import Content


TOPIC_DICT = Content()




@admin.route('/')
def index():
    return render_template('admin/home.html', TOPIC_DICT=TOPIC_DICT)


@admin.route('/select')
def select():
    id = request.args.get('id')
    experience = Experience.query.filter_by(id=id).first()
    # images = experience.images.all()
    return render_template('admin/select_image.html', experience=experience, TOPIC_DICT=TOPIC_DICT)

@admin.route('/both')
def both():
    imgid = request.args.get('id1')
    expid = request.args.get('id2')
    query = Imageexp.query.filter_by(experience_id=expid)
    try:
        user = query.one()
        if user:
            admin = query.update(dict(image_id=imgid))
            db.session.commit()
    except NoResultFound:
        image = Image.query.get(imgid)
        experience = Experience.query.get(expid)
        query2 = Imageexp(image_id=imgid, experience_id=expid)
        image.imageexp.append(query2)
        experience.imageexp.append(query2)
        db.session.add(image)
        db.session.add(experience)
        db.session.commit()
    return redirect('/admin/experience')



register_crud(admin, '/experience', 'experience', Experience, ExperienceForm, ['created_on','updated_on', 'id', 'about_experience', 'who_can_come', 'total', 'what_well_do'], Image)
register_crud(admin, '/flyer', 'flyer', Flyer, FlyerForm, ['created_on','updated_on', 'id'])
register_crud(admin, '/shop', 'shop', Shop, ShopForm, ['created_on','updated_on', 'id'])
register_crud(admin, '/slideshow', 'slideshow', Slideshow, SlideshowForm, ['created_on','updated_on', 'id'])
register_crud(admin, '/date', 'date', Date_available, Date_availableForm, ['created_on','updated_on', 'id'], Experience)
register_crud(admin, '/stroy', 'story', Story, StoryForm, ['created_on','updated_on', 'id'])
register_crud(admin, '/images', 'images', Image, ImageForm, ['created_on','updated_on', 'id'])
register_crud(admin, '/advert', 'advert', Advert, AdvertForm, ['created_on','updated_on', 'id'])
register_crud(admin, '/cart', 'cart', Cart, CartForm, ['created_on','updated_on', 'id'])


