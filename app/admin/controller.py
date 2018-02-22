import os

from app.admin import admin

from flask.views import MethodView
from werkzeug.utils import secure_filename

import PIL
from PIL import Image
import traceback

from app import app
from app.data.models import db

from flask import render_template, abort, request, redirect, flash, url_for, send_from_directory
from app.menu_content import Content

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

IGNORED_FILES = set(['.gitignore'])


TOPIC_DICT = Content()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def gen_file_name(filename):
    """
    If file was exist already, rename it and return a new name
    """

    i = 1
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        name, extension = os.path.splitext(filename)
        filename = '%s_%s%s' % (name, str(i), extension)
        i += 1

    return filename


def create_thumbnail(image):
    try:
        base_width = 200
        img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], image))
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
        img.save(os.path.join(app.config['THUMBNAIL_FOLDER'], image))

        return True

    except:
        print (traceback.format_exc())
        return False


@admin.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


class CRUIDAPI(MethodView):
    list_template = 'admin/manage.html'
    detail_template = 'admin/create_edit.html'

    def __init__(self, model, endpoint, form, exclude=[], rel_mode=None, list_template=None,
                 detail_template=None):
        self.model = model
        self.endpoint = endpoint
        self.form = form
        self.exclude = exclude
        self.rel_mode = rel_mode
        # so we can generate a url relevant to this
        # endpoint, for example if we utilize this CRUD object
        # to enpoint comments the path generated will be
        # /admin/comments/
        self.path = url_for('.%s' % self.endpoint)
        if list_template:
            self.list_template = list_template
        if detail_template:
            self.detail_template = detail_template

    def render_detail(self, **kwargs):
        return render_template(self.detail_template, path=self.path, TOPIC_DICT=TOPIC_DICT, **kwargs)

    def render_list(self, **kwargs):
        return render_template(self.list_template, path=self.path, TOPIC_DICT=TOPIC_DICT, **kwargs)

    def get(self, obj_id='', operation=''):
        
        obj = self.model.query.get(obj_id)

        if operation == 'delete':

            if hasattr(obj, 'filename'):
                path = os.path.join(app.config['UPLOAD_FOLDER'], obj.filename)
                file_thumb_path = os.path.join(app.config['THUMBNAIL_FOLDER'], obj.filename)
                if os.path.exists(path):
                    try:
                        os.remove(path)
                        if os.path.exists(file_thumb_path):
                            os.remove(file_thumb_path)
                        db.session.delete(obj)
                        db.session.commit()
                    except OSError as e:
                        print("Error: %s - %s." % (e.obj.filename, e.strerror))
                else:
                    print("Sorry, I can not find %s file." % obj.filename)
                    db.session.delete(obj)
                    db.session.commit()

            elif hasattr(obj, 'images'):
                for img_name in obj.images.all():
                    path = os.path.join(app.config['UPLOAD_FOLDER'], img_name.filename)
                    file_thumb_path = os.path.join(app.config['THUMBNAIL_FOLDER'], img_name.filename)
                    if img_name.filename:
                        if os.path.exists(path):
                            try:
                                os.remove(path)
                                if os.path.exists(file_thumb_path):
                                    os.remove(file_thumb_path)
                                db.session.delete(obj)
                                db.session.commit()
                            except OSError as e:
                                print("Error: %s - %s." % (e.img_name.filename, e.strerror))
                        else:
                            print("Sorry, I can not find %s file." % img_name.filename)
                            db.session.delete(obj)
                            db.session.commit()
            else:
                db.session.delete(obj)
                db.session.commit()
            return redirect(self.path)

        elif operation == 'delete_image':
            obj = self.rel_mode.query.get(obj_id)
            path = os.path.join(app.config['UPLOAD_FOLDER'], obj.filename)
            file_thumb_path = os.path.join(app.config['THUMBNAIL_FOLDER'], obj.filename)
            if os.path.exists(path):
                try:
                    os.remove(path)
                    if os.path.exists(file_thumb_path):
                            os.remove(file_thumb_path)
                    db.session.delete(obj)
                    db.session.commit()
                except OSError as e:
                    print("Error: %s - %s." % (e.obj.filename, e.strerror))
            else:
                print("Sorry, I can not find %s file." % obj.filename)
                db.session.delete(obj)
                db.session.commit()

            return redirect(self.path +'delete/'+ str(obj_id))

        elif operation == 'new':
            form = self.form()
            action = self.path
            return self.render_detail(form=form, action=action)

        elif operation == 'edit':
            obj = self.model.query.get(obj_id)
            # populate the form with our blog data
            form = self.form(obj=obj)
            # action is the url that we will later use
            # to do post, the same url with obj_id in this case
            action = request.path
            return self.render_detail(form=form, action=action, obj=obj)

        else:
            col = self.model.__table__.columns.keys()
            col_names = [name for name in col if name not in self.exclude]
            obj = self.model.query.order_by(self.model.created_on.desc()).all()
            return self.render_list(obj=obj, col_names=col_names)

    def post(self, obj_id='', operation=''):

        form = self.form()

        if obj_id:

            obj = self.model.query.get(obj_id)

            for attr, value in obj.__dict__.items():
                if attr not in ['_sa_instance_state','id', 'created_on', 'updated_on', 'rate_average', 'total']:
                    setattr(obj, attr, form[attr].data)

            if hasattr(form, 'images'):
                if form.images.data:
                    uploaded_files = request.files.getlist(form.images.name)
                    for file in uploaded_files:
                        # Check if the file is one of the allowed types/extensions
                        if file and allowed_file(file.filename):
                            # Make the filename safe, remove unsupported chars
                            filename = secure_filename(file.filename)
                            filename = gen_file_name(filename)
                            mime_type = file.content_type
                            # Move the file form the temporal folder to the upload
                            # folder we setup
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                            # path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                            upload_obj = self.rel_mode(filename=filename)
                            obj.images.append(upload_obj)
                            if mime_type.startswith('image'):
                                create_thumbnail(filename)

            else:
                if form.filename.data:
                        file = request.files[form.filename.name]
                        if file and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            filename = gen_file_name(filename)
                            mime_type = file.content_type
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                            form.filename.data = filename

                            if mime_type.startswith('image'):
                                create_thumbnail(filename)
                        form.populate_obj(obj)


        else:
            obj = self.model()
            if hasattr(form, 'images'):
                form = self.form()

                for attr, value in obj.__dict__.items():
                    if attr not in '_sa_instance_state':
                        setattr(obj, attr, form[attr].data)
                if form.images.data:
                    uploaded_files = request.files.getlist(form.images.name)
                    for file in uploaded_files:
                        # Check if the file is one of the allowed types/extensions
                        if file and allowed_file(file.filename):
                            # Make the filename safe, remove unsupported chars
                            filename = secure_filename(file.filename)
                            filename = gen_file_name(filename)
                            # Move the file form the temporal folder to the upload
                            # folder we setup
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                            upload_obj = self.rel_mode(filename=filename)
                            obj.images.append(upload_obj)
                    db.session.add(obj)
                    db.session.commit()
                return redirect(self.path)

            elif hasattr(form, 'filename'):
                if form.filename.data:
                    file = request.files[form.filename.name]
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        filename = gen_file_name(filename)
                        mime_type = file.content_type
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        form.filename.data = filename

                        if mime_type.startswith('image'):
                            create_thumbnail(filename)
                    form.populate_obj(obj)
                    db.session.add(obj)
                    db.session.commit()

                flash("Achievement created")

                return redirect(self.path)

            elif hasattr(form, 'dates_available'):
                obj = self.rel_mode()
                obj2 = self.model(dates_available=form.dates_available.data)
                obj.dates.append(obj2)
                db.session.add(obj)
            else:
                form.populate_obj(obj)
                db.session.add(obj)


        # form.populate_obj(obj)
        db.session.commit()
        return redirect(self.path)


def register_crud(app, url=None, endpoint=None, model=None, form=None, exclude=[], rel_mode=None, decorators=[], **kwargs):
    view = CRUIDAPI.as_view(endpoint, endpoint=endpoint,
                            model=model, form=form, exclude=exclude, rel_mode=rel_mode, **kwargs)

    for decorator in decorators:
        view = decorator(view)

    app.add_url_rule('%s/' % url, view_func=view, methods=['GET', 'POST'])
    app.add_url_rule('%s/<int:obj_id>/' % url, view_func=view)
    app.add_url_rule('%s/<operation>/' % url, view_func=view, methods=['GET'])
    app.add_url_rule('%s/<operation>/<int:obj_id>/' % url, view_func=view,
                     methods=['GET'])
    app.add_url_rule('%s/<operation>/<obj_id>/' % url, view_func=view,
                     methods=['GET', 'POST'])


