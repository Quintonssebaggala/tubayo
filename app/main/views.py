from flask import render_template, send_from_directory, request, json
from app import app
from app.main import main
from app.cache import cache
from flask_login import current_user, login_required
from app.data.models import db, Permission, Advert, Cart, Date_available, Experience, Flyer, Imageexp, Rate, Shop, Slideshow, Story
from flask_mail import Message
from app import mail
from app.decorators import admin_required, permission_required

@main.route("/message")
def message():

    msg = Message("Hello",
                  sender="from@example.com",
                  recipients=["quinton.ssebaggala@gmail.com"])
    msg.body = "testing"
    msg.html = "<b>testing</b>"
    
    return mail.send(msg)

@main.route('/')
# @login_required
# @admin_required
@cache.cached(300, key_prefix='index')
def index():
    slideshow = Slideshow.query.order_by(Slideshow.created_on.desc()).limit(3).all()
    stories = Story.query.order_by(Story.created_on.desc()).limit(12).all()
    experience = Imageexp.query.order_by(Imageexp.created_on.desc()).limit(8).all()
    shop = Shop.query.order_by(Shop.created_on.desc()).limit(12).all()
    flyers = Flyer.query.order_by(Flyer.created_on.desc()).limit(2).all()
    adverts = Advert.query.order_by(Advert.created_on.desc()).limit(3).all()
    return render_template('main/body.html', slideshow=slideshow, stories=stories, 
							experience=experience, shop=shop, flyers=flyers, adverts=adverts)


@main.route('/test')
def test():
    data = Experience.query.order_by(Experience.created_on.desc()).limit(5).all()
    return render_template('test.html', data=data)

@main.route('/shop/')
@login_required
# @permission_required(Permission.FOLLOW)
def shop():
    page_num = int(request.args.get('page', 1))
    # shop = Shop.query.order_by(Shop.created_on.desc()).limit(12).all()
    shop = Shop.query.order_by(Shop.created_on.desc()).paginate(page=page_num, per_page=5, error_out=True)
    return render_template('main/shop.html', shop=shop)



@main.route('/detail', methods=['GET'])
@cache.cached(300, key_prefix='detail')
def detail():
    experience_id = request.args.get('id')
    experience = Imageexp.query.filter_by(id=experience_id).first()
    return render_template('main/detail.html', experience=experience)


@main.route('/details', methods=['GET'])
def details():
    id = request.args.get('id2', type=int)
    rating = request.args.get('name')
    experience = Experience.query.get(id)
    rate2 = Rate(rating=rating)
    experience.rates.append(rate2)
    cache.delete('index')
    cache.delete('detail')
    db.session.add(experience)
    db.session.commit()
    return json.dumps({'status': 'OK', 'rating': rating, 'id': id})


# @main.route("/addToCart", methods=['GET', 'POST'])
# @login_required
# def addToCart():
#     # data = request.form['quality']
#     quality=request.form['quality']
#     # quality = request.args.get('quality')
#     expid = int(request.args.get('productid'))
#     user = User.query.get(current_user.id)
#     exp = Experience.query.get(expid)
#     subtotal = float(quality)*float(exp.price)
#     cart = Kart(name=exp.title, quantity=quality, price=exp.price, total=subtotal, user_id=current_user.id, experience_id=expid)
#     user.karts.append(cart)
#     exp.karts.append(cart)
#     db.session.add(user)
#     db.session.add(exp)
#     db.session.commit()
#     return redirect(url_for('experienc.cart'))


# @experienc.route("/cart")
# @login_required
# def cart():
#     noOfItems = getLoginDetails()
#     userId = current_user.id
#     l = []
#     m = { }
#     # products = Kart.query.filter(and_(Kart.user_id == userId, Kart.experience_id == 2)).all()
#     products = Kart.query.filter_by(user_id=userId).all()
#     for p in products:
#         # l.append(p.experience)
#         m.update({p.id: p.experience})
#     totalPrice = 0
#     # for row in products:
#     #     totalPrice += row[2]
    # return render_template("experience/cart.html", product=products, totalPrice=totalPrice, noOfItems=noOfItems)