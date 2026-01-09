from datetime import datetime
from extensions import db

class About(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.Text, nullable=False)
    profile_pic = db.Column(db.String(200))

class SocialLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)

class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(50), nullable=False)
    institution = db.Column(db.String(200), nullable=False)
    degree = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(200), nullable=False)
    organisation = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    overview = db.Column(db.String(300))      
    link = db.Column(db.String(300))         
    description = db.Column(db.Text, nullable=False)  
    image = db.Column(db.String(200))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    user = db.relationship("User", backref=db.backref("contact_messages", lazy=True))
    name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    reply = db.Column(db.Text, nullable=True)   
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), nullable=False, unique=True)
    full_name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProjectComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    project = db.relationship("Project", backref=db.backref("project_comments", lazy=True))
    user = db.relationship("User", backref=db.backref("project_comments", lazy=True))

class ProjectRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("project_id", "user_id", name="uq_project_user_rating"),)
    project = db.relationship("Project", backref=db.backref("ratings", lazy=True))
    user = db.relationship("User", backref=db.backref("ratings", lazy=True))