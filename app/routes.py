from app import app
from flask import render_template, flash, redirect, url_for
from app.forms import LOgin


@app.route('/')
@app.route('/index')
def index():
    user = {'username':'Faruq'}
    posts= [
        {
            'author': {'username':'Fareedah'},
            'body': 'I really wanna be the very best!'
        },
        {
            'author': {'username':'Maddie'},
            'body': 'I really hope i pass the design course!'
        },
        {
            'author': {'username': 'Yasir'},
            'body': 'May Allah accept all our prayers, Ameen!'
        },
        {
            'author': {'username': 'Aarol'},
            'body': 'I am not undecided!'
        }
        
    ]
    return render_template('index.html', title='Home page', user=user, posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LOgin()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me ={}'.format(
            form.username.data, form.remember_me.data
        ))
        return redirect(url_for('index'))
    return render_template('login.html', title = 'Sign In', form=form)