from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Optional, URL, Email, Length, NumberRange

class AboutForm(FlaskForm):
    bio = TextAreaField("About Me", validators=[DataRequired()])
    profile_pic = FileField("Profile Picture")
    submit = SubmitField("Save")

class SocialLinkForm(FlaskForm):
    platform = StringField("Platform", validators=[DataRequired()])
    url = StringField("Profile URL", validators=[DataRequired()])
    submit = SubmitField("Add")

class ProjectForm(FlaskForm):
    title = StringField('Project Title', validators=[DataRequired()])
    overview = StringField('Overview (short)', validators=[Optional()])   # NEW
    link = StringField('Project Link', validators=[Optional()])    # NEW
    description = TextAreaField('Details', validators=[DataRequired()])
    image = FileField('Project Image')
    submit = SubmitField('Save')

class CommentForm(FlaskForm):
    name = StringField('Name', validators=[Optional(), Length(min=2, max=100)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=2)])
    submit = SubmitField('Send')

class EducationForm(FlaskForm):
    year = StringField("Year", validators=[DataRequired()])
    institution = StringField("Institution", validators=[DataRequired()])
    degree = StringField("Degree", validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField("Save")

class ExperienceForm(FlaskForm):
    role = StringField("Role", validators=[DataRequired()])
    organisation = StringField("Organisation", validators=[DataRequired()])
    duration = StringField('Duration', validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Save")

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=60)])
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Create account")

class UserLoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class ProjectCommentForm(FlaskForm):
    text = TextAreaField("Comment", validators=[DataRequired(), Length(min=2)])
    submit = SubmitField("Post Comment")

class ProjectRatingForm(FlaskForm):
    rating = IntegerField("Rating (1 to 5)", validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField("Submit Rating")