from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, DateTime, Float, Text, ForeignKey, String, Unicode, Date
from sqlalchemy.orm import relationship, backref, composite
from sqlalchemy_utils import aggregated, CountryType, EmailType, PhoneNumber
from wtforms.validators import Email


class Base(db.Model):
    __abstract__ = True

    created_on = Column(DateTime(timezone=True), default=func.now())
    updated_on = Column(DateTime(timezone=True),
                        default=func.now(), onupdate=func.now())


class Experience(Base):
    __tablename__ = 'experiences'

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
    filename = Column(String(30))
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

    id = Column(Integer, primary_key=True)
    filename = Column(String(30), nullable=False)

    def __init__(self, **kwargs):
        super(Flyer, self).__init__(**kwargs)

    def __repr__(self):
        return '<Flyer - {}>'.format(self.filename)


class Shop(Base):
    __tablename__ = 'shop'

    id = Column(Integer, primary_key=True)
    filename = Column(String(30), nullable=False)
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
    filename = Column(String(30), nullable=False)

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
    filename = Column(String(30), nullable=False)

    def __init__(self, **kwargs):
        super(Slideshow, self).__init__(**kwargs)

    def __repr__(self):
        return '<Slideshow - {}>'.format(self.filename)


class Story(Base):
    __tablename__ = 'stories'

    id = Column(Integer, primary_key=True)
    filename = Column(String(30), nullable=False)
    story_name = Column(String(30), nullable=False)
    caption = Column(String(200), nullable=False)


    def __init__(self, **kwargs):
        super(Story, self).__init__(**kwargs)

    def __repr__(self):
        return '<Story - {}>'.format(self.story_name)



