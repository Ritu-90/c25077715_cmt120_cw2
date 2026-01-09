import os
from uuid import uuid4
from typing import Optional
from flask import Flask, render_template, redirect, url_for, request, session, flash, abort
from werkzeug.utils import secure_filename
from config import Config
from extensions import db, csrf
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, func

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db.init_app(app)
csrf.init_app(app)

from models import (Education, Experience, Skill, Project, Comment, About, SocialLink, User, ProjectComment, ProjectRating)
from forms import (ProjectForm, CommentForm, AboutForm, SocialLinkForm, EducationForm, ExperienceForm,RegisterForm, UserLoginForm, ProjectCommentForm, ProjectRatingForm)

with app.app_context():
    db.create_all()

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_image(file_obj) -> Optional[str]:
    if not file_obj or not getattr(file_obj, "filename", "").strip():
        return None

    original = secure_filename(file_obj.filename)
    if not allowed_file(original):
        raise ValueError("Invalid file type. Allowed: png, jpg, jpeg, gif, webp")

    ext = original.rsplit(".", 1)[1].lower()
    stored_name = f"{uuid4().hex}.{ext}"
    file_obj.save(os.path.join(app.config["UPLOAD_FOLDER"], stored_name))
    return stored_name

# AUTH HELPERS
def is_admin() -> bool:
    return bool(session.get("is_admin"))

def current_user_obj():
    user_id = session.get("user_id")
    return User.query.get(user_id) if user_id else None

def can_manage_resource(owner_user_id: Optional[int]) -> bool:
    """
    Admin can manage everything.
    User can manage only their own resource.
    """
    if is_admin():
        return True
    user_id = session.get("user_id")
    return bool(user_id and owner_user_id and owner_user_id == user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if (
            request.form['username'] == app.config['ADMIN_USERNAME']
            and request.form['password'] == app.config['ADMIN_PASSWORD']
        ):
            session['is_admin'] = True
            return redirect(url_for('home'))
        flash("Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('home'))

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data.strip(),
                full_name=form.full_name.data.strip(),
                email=form.email.data.strip().lower(),
                password_hash=generate_password_hash(form.password.data),
            )
            db.session.add(user)
            db.session.commit()
            flash("Account created! You can now log in.", "success")
            return redirect(url_for("user_login"))
        
        except IntegrityError:
            db.session.rollback()
            flash("Username or email already exists.", "danger")

        except Exception as e:
            db.session.rollback()
            # Show the real error while developing
            flash(f"Register error: {e}", "danger")

    elif request.method == "POST":
        # Show field errors, if validation failed
        for field, errors in form.errors.items():
            for err in errors:
                flash(f"{field}: {err}", "danger")
    return render_template("register.html", form=form)

@app.route("/user-login", methods=["GET", "POST"])
def user_login():
    form = UserLoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data.strip()).first()
            if user and check_password_hash(user.password_hash, form.password.data):
                session["user_id"] = user.id
                flash("Logged in successfully.", "success")
                return redirect(url_for("projects"))

            flash("Invalid username or password.", "danger")

        except Exception as e:
            flash(f"Login error: {e}", "danger")

    elif request.method == "POST":
        for field, errors in form.errors.items():
            for err in errors:
                flash(f"{field}: {err}", "danger")
    return render_template("user_login.html", form=form)

@app.route("/user-logout")
def user_logout():
    session.pop("user_id", None)
    flash("Logged out.", "success")
    return redirect(url_for("home"))

@app.context_processor
def inject_admin():
    return dict(is_admin=session.get('is_admin', False))

@app.context_processor
def inject_user():
    user_id = session.get("user_id")
    user = User.query.get(user_id) if user_id else None
    return dict(current_user=user)

# -- HOME --

@app.route("/")
def home():
    about = About.query.first()

    latest_projects = Project.query.order_by(Project.id.desc()).limit(3).all()

    stats = {
        "projects": Project.query.count(),
        "skills": Skill.query.count(),
        "education": Education.query.count(),
        "experience": Experience.query.count(),
    }

    social_links = SocialLink.query.order_by(SocialLink.id.asc()).all()

    return render_template(
        "home.html",
        about=about,
        latest_projects=latest_projects,
        stats=stats,
        social_links=social_links,
    )

# -- ABOUT --

@app.route('/about', methods=['GET', 'POST'])
def about():
    about = About.query.first()  # get from DB
    form = AboutForm(obj=about) if about else AboutForm()

    # Only admin can edit/save
    if request.method == 'POST' and not session.get('is_admin'):
        abort(403)

    if form.validate_on_submit():
    
        if about:
            about.bio = form.bio.data
        else:
            about = About(bio=form.bio.data)
            db.session.add(about)

        db.session.commit()
        flash("About section updated!")
        return redirect(url_for('about'))

    return render_template('about.html', about=about, form=form)

@app.route('/social', methods=['POST'])
def social():
    if not session.get('is_admin'):
        abort(403)

    form = SocialLinkForm()
    if form.validate_on_submit():
        db.session.add(SocialLink(platform=form.platform.data, url=form.url.data))
        db.session.commit()
        flash("Social link added!")
    return redirect(url_for("about"))

# -- EDUCATION --

@app.route('/education')
def education():
    return render_template(
        'education.html',
        data=Education.query.all()
    )

@app.route('/add-education', methods=['GET', 'POST'])
def add_education():
    if not session.get('is_admin'):
        abort(403)

    form = EducationForm()
    if form.validate_on_submit():
        db.session.add(
            Education(
                year=form.year.data,
                institution=form.institution.data,
                degree=form.degree.data,
                description=form.description.data
            )
        )
        db.session.commit()
        return redirect(url_for('education'))

    return render_template('add_education.html', form=form)

@app.route('/edit-education/<int:id>', methods=['GET', 'POST'])
def edit_education(id):
    if not session.get('is_admin'):
        abort(403)

    edu = Education.query.get_or_404(id)
    form = EducationForm(obj=edu)

    if form.validate_on_submit():
        edu.year = form.year.data
        edu.institution = form.institution.data
        edu.degree = form.degree.data
        edu.description = form.description.data
        db.session.commit()
        return redirect(url_for("education"))
    return render_template("edit_education.html", form=form, edu=edu)

@app.route('/delete-education/<int:id>', methods=["POST"])
def delete_education(id):
    if not session.get('is_admin'):
        abort(403)

    db.session.delete(Education.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('education'))

# -- EXPERIENCE --

@app.route('/experience')
def experience():
    return render_template(
        'experience.html',
        data=Experience.query.all()
    )

@app.route('/add-experience', methods=['GET', 'POST'])
def add_experience():
    if not session.get('is_admin'):
        abort(403)

    form = ExperienceForm()

    if form.validate_on_submit():
        exp = Experience(
            role=form.role.data,
            organisation=form.organisation.data,
            duration=form.duration.data,
            description=form.description.data
        )

        db.session.add(exp)   
        db.session.commit()

        return redirect(url_for('experience'))

    return render_template('add_experience.html', form=form)

@app.route('/edit-experience/<int:id>', methods=['GET', 'POST'])
def edit_experience(id):
    if not session.get('is_admin'):
        abort(403)

    exp = Experience.query.get_or_404(id)
    form = ExperienceForm(obj=exp)

    if form.validate_on_submit():
        exp.role = form.role.data
        exp.organisation = form.organisation.data
        exp.duration = form.duration.data
        exp.description = form.description.data
        db.session.commit()
        return redirect(url_for("experience"))
    return render_template("edit_experience.html", form=form, exp=exp)

@app.route('/delete-experience/<int:id>', methods=["POST"])
def delete_experience(id):
    if not session.get('is_admin'):
        abort(403)

    db.session.delete(Experience.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('experience'))

# --SKILLS --

@app.route('/skills')
def skills():
    return render_template(
        'skills.html',
        data=Skill.query.all()
    )

@app.route('/add-skill', methods=['POST'])
def add_skill():
    if not session.get('is_admin'):
        abort(403)

    name = request.form.get("name", "").strip()
    if name:
        db.session.add(Skill(name=name))
        db.session.commit()
    return redirect(url_for('skills'))

@app.route('/delete-skill/<int:id>', methods=["POST"])
def delete_skill(id):
    if not session.get('is_admin'):
        abort(403)

    db.session.delete(Skill.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('skills'))

# -- PROJECTS --

@app.route('/projects')
def projects():
    q = request.args.get("q", "").strip()

    query = Project.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Project.title.ilike(like),
                Project.overview.ilike(like),
                Project.description.ilike(like),
            )
        )

    projects_list = query.order_by(Project.id.desc()).all()
    return render_template("projects.html", data=projects_list, q=q)

@app.route('/add-project', methods=['GET', 'POST'])
def add_project():
    if not session.get('is_admin'):
        abort(403)

    form = ProjectForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data and getattr(form.image.data, "filename", "").strip():
            try:
                filename = save_uploaded_image(form.image.data)
            except ValueError as e:
                flash(str(e))
                return redirect(url_for("add_project"))

        db.session.add(
            Project(
                title=form.title.data,
                overview=form.overview.data,
                link=form.link.data,
                description=form.description.data,
                image=filename,
            )
        )
        db.session.commit()
        flash("Project saved successfully!")
        return redirect(url_for('projects'))
    
    if request.method == "POST":
        for field_name, errors in form.errors.items():
            for err in errors:
                flash(f"{field_name}: {err}")

    return render_template('add_project.html', form=form)

@app.route('/edit-project/<int:id>', methods=['GET', 'POST'])
def edit_project(id):
    if not session.get('is_admin'):
        abort(403)

    project = Project.query.get_or_404(id)
    form = ProjectForm(obj=project)

    if form.validate_on_submit():
        project.title = form.title.data
        project.overview = form.overview.data
        project.link = form.link.data
        project.description = form.description.data

        if form.image.data and getattr(form.image.data, "filename", "").strip():
            try:
                project.image = save_uploaded_image(form.image.data)
            except ValueError as e:
                flash(str(e))
                return redirect(url_for("edit_project", id=project.id))

        db.session.commit()
        return redirect(url_for('projects'))

    return render_template('add_project.html', form=form, project=project)

@app.route('/delete-project/<int:id>', methods=["POST"])
def delete_project(id):
    if not session.get('is_admin'):
        abort(403)

    db.session.delete(Project.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('projects'))

@app.route("/project/<int:project_id>", methods=["GET", "POST"])
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)

    comment_form = ProjectCommentForm()
    rating_form = ProjectRatingForm()

    user_id = session.get("user_id")

    # Average rating
    avg_rating = db.session.query(func.avg(ProjectRating.rating)).filter_by(project_id=project_id).scalar()
    avg_rating = round(float(avg_rating), 1) if avg_rating is not None else None

    # Current user's rating (if any)
    my_rating = None
    if user_id:
        existing = ProjectRating.query.filter_by(project_id=project_id, user_id=user_id).first()
        my_rating = existing.rating if existing else None

    # Handle comment submit
    if comment_form.validate_on_submit() and request.form.get("form_name") == "comment":
        if not user_id:
            flash("Please log in to comment.")
            return redirect(url_for("user_login"))

        db.session.add(ProjectComment(project_id=project_id, user_id=user_id, text=comment_form.text.data))
        db.session.commit()
        flash("Comment posted!")
        return redirect(url_for("project_detail", project_id=project_id))

    # Handle rating submit
    if rating_form.validate_on_submit() and request.form.get("form_name") == "rating":
        if not user_id:
            flash("Please log in to rate.")
            return redirect(url_for("user_login"))

        existing = ProjectRating.query.filter_by(project_id=project_id, user_id=user_id).first()
        if existing:
            existing.rating = rating_form.rating.data
        else:
            db.session.add(ProjectRating(project_id=project_id, user_id=user_id, rating=rating_form.rating.data))

        db.session.commit()
        flash("Rating saved!")
        return redirect(url_for("project_detail", project_id=project_id))

    comments = ProjectComment.query.filter_by(project_id=project_id).order_by(ProjectComment.created_at.desc()).all()

    return render_template(
        "project_detail.html",
        project=project,
        comments=comments,
        avg_rating=avg_rating,
        my_rating=my_rating,
        comment_form=comment_form,
        rating_form=rating_form,
    )

# USER EDIT/DELETE ON PROJECT COMMENTS

@app.route("/project-comment/<int:comment_id>/edit", methods=["GET", "POST"])
def edit_project_comment(comment_id):
    comment = ProjectComment.query.get_or_404(comment_id)

    if not can_manage_resource(comment.user_id):
        abort(403)

    if request.method == "POST":
        new_text = request.form.get("text", "").strip()
        if not new_text:
            flash("Comment cannot be empty.", "danger")
            return redirect(url_for("edit_project_comment", comment_id=comment_id))

        comment.text = new_text
        db.session.commit()
        flash("Comment updated.", "success")
        return redirect(url_for("project_detail", project_id=comment.project_id))

    return render_template("edit_project_comment.html", comment=comment)

@app.route("/project-comment/<int:comment_id>/delete", methods=["POST"])
def delete_project_comment(comment_id):
    comment = ProjectComment.query.get_or_404(comment_id)

    if not can_manage_resource(comment.user_id):
        abort(403)

    project_id = comment.project_id
    db.session.delete(comment)
    db.session.commit()
    flash("Comment deleted.", "success")
    return redirect(url_for("project_detail", project_id=project_id))

# -- CONTACT --

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = CommentForm()
    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    user = current_user_obj()

    if form.validate_on_submit():
        if user:
            display_name = (user.full_name or user.username).strip()
            msg = Comment(
                user_id=user.id,
                name=display_name,
                message=form.message.data
            )
        else:
            if not (form.name.data and form.name.data.strip()):
                flash("Name is required if you are not logged in.", "danger")
                return redirect(url_for("contact"))
            msg = Comment(
                user_id=None,
                name=form.name.data.strip(),
                message=form.message.data
            )

        db.session.add(msg)
        db.session.commit()
        return redirect(url_for('contact'))

    return render_template(
        'contact.html',
        form=form,
        comments=comments
    )

# Admin OR owner can delete
@app.route('/delete-message/<int:msg_id>', methods=['POST'])
def delete_message(msg_id):
    message = Comment.query.get_or_404(msg_id)

    if not can_manage_resource(message.user_id):
        abort(403)

    db.session.delete(message)
    db.session.commit()
    flash("Message deleted.", "success")
    return redirect(url_for('contact'))

# Admin OR owner can edit
@app.route('/edit-message/<int:msg_id>', methods=['GET', 'POST'])
def edit_message(msg_id):
    message = Comment.query.get_or_404(msg_id)

    if not can_manage_resource(message.user_id):
        abort(403)

    if request.method == "POST":
        new_msg = request.form.get("message", "").strip()
        if not new_msg:
            flash("Message cannot be empty.", "danger")
            return redirect(url_for("edit_message", msg_id=msg_id))

        message.message = new_msg
        db.session.commit()
        flash("Message updated.", "success")
        return redirect(url_for("contact"))

    return render_template("edit_message.html", message=message)

# Admin-only reply

@app.route('/reply-message/<int:msg_id>', methods=['GET', 'POST'])
def reply_message(msg_id):
    if not session.get('is_admin'):
        abort(403)

    message = Comment.query.get_or_404(msg_id)

    if request.method == "POST":
        message.reply = request.form.get("reply")
        db.session.commit()
        return redirect(url_for("contact"))

    return render_template("reply_message.html", message=message)

@app.route('/edit-reply/<int:msg_id>', methods=['GET', 'POST'])
def edit_reply(msg_id):
    if not is_admin():
        abort(403)

    message = Comment.query.get_or_404(msg_id)

    if request.method == 'POST':
        message.reply = request.form['reply']
        db.session.commit()
        return redirect(url_for('contact'))

    return render_template('reply_message.html', message=message)

@app.route('/delete-reply/<int:msg_id>', methods=['POST'])
def delete_reply(msg_id):
    if not session.get('is_admin'):
        abort(403)

    message = Comment.query.get_or_404(msg_id)
    message.reply = None  
    db.session.commit()

    return redirect(url_for('contact'))

if __name__ == '__main__':
    app.run(debug=True)
