from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField
from flask_wtf.file import FileAllowed
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    video = FileField('Upload Video', validators=[FileAllowed(['mp4', 'mov', 'avi', 'mkv'])])
    submit = SubmitField('Post')