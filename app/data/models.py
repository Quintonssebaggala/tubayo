from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, AnonymousUserMixin


db = SQLAlchemy()
login_manager = LoginManager()


from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, DateTime, Float, Text, ForeignKey, String, Unicode, Date, Boolean
from sqlalchemy.orm import relationship, backref, composite
from sqlalchemy_utils import aggregated, CountryType, EmailType, PhoneNumber
from wtforms.validators import Email
from werkzeug.security import generate_password_hash, check_password_hash

from flask_dance.consumer.backend.sqla import OAuthConsumerMixin


class Base(db.Model):
    __abstract__ = True

    created_on = Column(DateTime(timezone=True), default=func.now())
    updated_on = Column(DateTime(timezone=True),
                        default=func.now(), onupdate=func.now())


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class User(UserMixin, Base):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = Column(String(64), index=True, unique=False)
    email = Column(String(120), index=True, unique=True)
    password_hash = Column(db.String(128))
    last_seen = Column(DateTime(timezone=True), default=func.now())
    role_id = Column(Integer, ForeignKey('roles.id'))
    experiences = relationship('Experience', backref='host', cascade="all, delete-orphan", lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == 'ssebaggalaq@gmail.com':
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def __repr__(self):
        return '<User - {}>'.format(self.username) 

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser

class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = Column(String(256), unique=True)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User)



class Role(db.Model):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    default = Column(Boolean, default=False, index=True)
    permissions = Column(Integer)
    users = relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)

        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        roles = {
                    'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
                    'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                    Permission.WRITE, Permission.MODERATE],
                    'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                    Permission.WRITE, Permission.MODERATE,
                    Permission.ADMIN],
                }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role - {}>'.format(self.name)


class Experience(Base):
    __tablename__ = 'experiences'
    __searchable__ = ['host_name','experience_title']

    id = Column(Integer, primary_key=True)
    host_name = Column(String(50), unique=True, nullable=False)
    experience_title = Column(String(100), unique=True, nullable=False)
    tag = Column(Text, nullable=False)
    email = Column(EmailType, nullable=False, 
                    info={'validators': Email()})
    phone_number = Column(String(50), nullable=False)
    country = Column(String(100), nullable=False)
    place = Column(String(50), nullable=False)
    about_experience = Column(Text, nullable=False)
    what_well_do = Column(Text, nullable=False, info={'label': 'What we will do'})
    who_can_come = Column(Text, nullable=False)
    price = Column(Float(20), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))

    @aggregated('rates', Column(Float, default=0.0))
    def rate_average(self):
        return func.avg(Rate.rating)

    @aggregated('carts', Column(Float))
    def total(self):
        return func.avg(Cart.total)

    images = relationship(
        'Image', cascade="all, delete-orphan", backref='image', lazy='dynamic')
    imageexp = relationship(
        'Imageexp', cascade="all, delete-orphan", backref='experience', lazy='dynamic')
    carts = relationship('Cart', backref='cart',
                         cascade="all, delete-orphan", lazy='dynamic')
    dates = relationship('Date_available', backref='date',
                         cascade="all, delete-orphan", lazy='dynamic')
    rates = relationship('Rate', backref='rate',
                         cascade="all, delete-orphan", lazy='dynamic')

    def __init__(self, host_name=None, experience_title=None, tag=None, email=None, phone_number=None, country=None, place=None, about_experience=None, what_well_do=None, who_can_come=None, price=None, images=None, rate_count=None, karts=None, dates=None, rates=None):
        self.host_name = host_name
        self.experience_title = experience_title
        self.tag = tag
        self.email = email
        self.phone_number = phone_number
        self.place = place
        self.country = country
        self.about_experience = about_experience
        self.what_well_do = what_well_do
        self.who_can_come = who_can_come
        self.price = price

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            p = Experience(host_name=forgery_py.name.full_name(), 
                            experience_title=forgery_py.lorem_ipsum.title(), 
                            tag=forgery_py.lorem_ipsum.sentence(), 
                            email=forgery_py.email.address(), 
                            phone_number=forgery_py.address.phone(),
                            country=forgery_py.address.country(), 
                            place=forgery_py.address.city(), 
                            about_experience=forgery_py.lorem_ipsum.paragraph(), 
                            what_well_do=forgery_py.lorem_ipsum.sentence(), 
                            who_can_come=forgery_py.lorem_ipsum.sentence(), 
                            price=forgery_py.monetary.formatted_money())
            db.session.add(p)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return '<Experience - {}>'.format(self.experience_title)




class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    filename = Column(String(150))
    imageexp = relationship(
        'Imageexp', cascade="all, delete-orphan", backref='image', lazy='dynamic')
    experience_id = Column(Integer, ForeignKey('experiences.id', ondelete='CASCADE'))

    def __init__(self, filename=None, experience_id=None):
        self.filename = filename
        self.experience_id = experience_id

    def __repr__(self):
        return '<Image - {}>'.format(self.filename)

class Imageexp(Base):
    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey('images.id'))
    experience_id = Column(Integer, ForeignKey('experiences.id'))

    def __init__(self, image_id=None, experience_id=None):
        self.image_id = image_id
        self.experience_id = experience_id

    def __repr__(self):
        return '<Image - {}>'.format(self.filename)


class Flyer(Base):
    __tablename__ = 'flyers'
    __searchable__ = ['filename']

    id = Column(Integer, primary_key=True)
    filename = Column(String(150), nullable=False)

    def __init__(self, **kwargs):
        super(Flyer, self).__init__(**kwargs)

    def __repr__(self):
        return '<Flyer - {}>'.format(self.filename)


class Shop(Base):
    __tablename__ = 'shop'

    id = Column(Integer, primary_key=True)
    filename = Column(String(150), nullable=False)
    item_name = Column(String(30), nullable=False)
    price = Column(Float(10), nullable=False)


    def __init__(self, filename=None, item_name=None, price=None):
        self.filename = filename
        self.item_name = item_name
        self.price = price

    def __repr__(self):
        return '<Shop - {}>'.format(self.item_name)


class Advert(Base):
    __tablename__ = 'adverts'

    id = Column(Integer, primary_key=True)
    filename = Column(String(150), nullable=False)

    def __init__(self, **kwargs):
        super(Advert, self).__init__(**kwargs)

    def __repr__(self):
        return '<Advert - {}>'.format(self.filename)


class Cart(Base):
    __tablename__ = 'cart'

    id = Column(Integer, primary_key=True)
    experience = Column(String(100))
    price = Column(Float)
    quantity = Column(Integer)
    total = Column(Float)
    experience_id = Column(Integer, ForeignKey('experiences.id'))

    def __init__(self, experience=None, price=None, quantity=None, total=None, experience_id=None):
        self.experience = experience
        self.price = price
        self.quantity = quantity
        self.total = total
        self.experience_id = experience_id

    def __repr__(self):
        return '<Cart - {}>'.format(self.experience)


class Date_available(Base):
    id = Column(Integer, primary_key=True)
    dates_available = Column(Date)
    experience_id = Column(Integer, ForeignKey(
        'experiences.id', ondelete='CASCADE'))

    def __init__(self, dates_available=None, exp_id=None):
        self.dates_available = dates_available
        self.exp_id = exp_id

    def __repr__(self):
        return '<Date_available - {}>'.format(self.dates_available)


class Rate(Base):
    id = Column(Integer, primary_key=True)
    rating = Column(Float)
    experience_id = Column(Integer, ForeignKey('experiences.id'),
                          nullable=False)

    def __init__(self, rating=None, exp_id=None):
        self.rating = rating
        self.exp_id = exp_id

    def __repr__(self):
        return '<Rate - {}>'.format(self.rating)


class Slideshow(Base):
    __tablename__ = 'slideshow'

    id = Column(Integer, primary_key=True)
    filename = Column(String(150), nullable=False)

    def __init__(self, **kwargs):
        super(Slideshow, self).__init__(**kwargs)

    def __repr__(self):
        return '<Slideshow - {}>'.format(self.filename)


class Story(Base):
    __tablename__ = 'stories'

    id = Column(Integer, primary_key=True)
    filename = Column(String(150), nullable=False)
    story_name = Column(String(30), nullable=False)
    caption = Column(String(200), nullable=False)


    def __init__(self, **kwargs):
        super(Story, self).__init__(**kwargs)

    def __repr__(self):
        return '<Story - {}>'.format(self.story_name)



