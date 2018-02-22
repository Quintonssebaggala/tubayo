from app import app
from app.data.models import db, Experience, Image, Flyer, Advert, Cart, Date_available, Imageexp, Rate, Shop, Slideshow, Story 
from flask_migrate import Migrate

migrate = Migrate(app, db)

with app.app_context():
    # db.drop_all()
    db.create_all()


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, 
    			db=db, 
    			Experience=Experience, 
    			Image=Image, 
    			Flyer=Flyer, 
    			Advert=Advert, 
    			Cart=Cart, 
    			Date_available=Date_available, 
    			Imageexp=Imageexp, 
    			Rate=Rate, 
    			Shop=Shop, 
    			Slideshow=Slideshow, 
    			Story=Story)
