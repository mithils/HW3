## SI 364 - Winter 2018
## HW 3

####################
## Import statements
####################

from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import Required, Length
from flask_sqlalchemy import SQLAlchemy

############################
# Application configurations
############################
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string from si364'
## TODO 364: Create a database in postgresql in the code line below, and fill in your app's database URI.
# It should be of the format: postgresql://localhost/YOUR_DATABASE_NAME

## Your final Postgres database should be your uniqname, plus HW3, e.g. "jczettaHW3" or "maupandeHW3"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/mithilsHW3"
## Provided:
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

##################
### App setup ####
##################
db = SQLAlchemy(app) # For database use


#########################
#########################
######### Everything above this line is important/useful setup,
## not problem-solving.##
#########################
#########################

#########################
##### Set up Models #####
#########################

## TODO 364: Set up the following Model classes, as described, with the respective fields (data types).

## The following relationships should exist between them:
# Tweet:User - Many:One

class Tweet(db.Model):
    __tablename__ = 'tweets'
    id = db.Column(db.Integer,primary_key=True)
    tweetText = db.Column(db.String(280))
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))

    def __repr__(self):
        return '{0} (ID: {1})'.format(self.tweetText,self.id)



# - Tweet
## -- id (Integer, Primary Key)
## -- text (String, up to 280 chars)
## -- user_id (Integer, ID of user posted -- ForeignKey)

## Should have a __repr__ method that returns strings of a format like:

#### {Tweet text...} (ID: {tweet id})

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True)
    display_name = db.Column(db.String(124))
    tweets = db.relationship('Tweet',backref='User')


    def __repr__(self):
        return '{0} | ID: {1}'.format(self.username,self.id)



# - User
## -- id (Integer, Primary Key)
## -- username (String, up to 64 chars, Unique=True)
## -- display_name (String, up to 124 chars)
## ---- Line to indicate relationship between Tweet and User tables (the 1 user: many tweets relationship)

## Should have a __repr__ method that returns strings of a format like:
#### {username} | ID: {id}


########################
##### Set up Forms #####
########################

# TODO 364: Fill in the rest of the below Form class so that someone running this web app will be able to fill in information about tweets they wish existed to save in the database:

## -- text: tweet text (Required, should not be more than 280 characters)
## -- username: the twitter username who should post it (Required, should not be more than 64 characters)
## -- display_name: the display name of the twitter user with that username (Required, + set up custom validation for this -- see below)

# HINT: Check out index.html where the form will be rendered to decide what field names to use in the form class definition

def validate_displayname(form,field):
    if str(field.data).startswith('@'):
        raise ValidationError('Please enter a valid username')

class tweetForm(FlaskForm):
    text = StringField('Enter tweet text', validators=[Required()])
    username = StringField('Enter twitter username', validators=[Required(),Length(min=2),validate_displayname])
    display_name = StringField('Enter user display name',validators=[Required()])
    submit = SubmitField("Submit")






# TODO 364: Set up custom validation for this form such that:
# - the twitter username may NOT start with an "@" symbol (the template will put that in where it should appear)
# - the display name MUST be at least 2 words (this is a useful technique to practice, even though this is not true of everyone's actual full name!)

# TODO 364: Make sure to check out the sample application linked in the readme to check if yours is like it!


###################################
##### Routes & view functions #####
###################################

## Error handling routes - PROVIDED
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

#############
## Main route
#############

## TODO 364: Fill in the index route as described.

# A template index.html has been created and provided to render what this route needs to show -- YOU just need to fill in this view function so it will work.
# Some code already exists at the end of this view function -- but there's a bunch to be filled in.
## HINT: Check out the index.html template to make sure you're sending it the data it needs.
## We have provided comment scaffolding. Translate those comments into code properly and you'll be all set!

# NOTE: The index route should:
# - Show the Tweet form.
# - If you enter a tweet with identical text and username to an existing tweet, it should redirect you to the list of all the tweets and a message that you've already saved a tweet like that.
# - If the Tweet form is entered and validates properly, the data from the form should be saved properly to the database, and the user should see the form again with a message flashed: "Tweet successfully saved!"
# Try it out in the sample app to check against yours!

@app.route('/', methods=['GET', 'POST'])
def index():
    # Initialize the form
    form = tweetForm()
    tweet_num = len(Tweet.query.all())
    if form.validate_on_submit():
        tweet_text = form.text.data
        user_name = form.username.data
        display_name = form.display_name.data

        user = User.query.filter_by(username=user_name).first()
        if user is None:
            user = User(username = user_name,display_name=display_name)
            db.session.add(user)
            db.session.commit()

        tweet = Tweet.query.filter_by(tweetText=tweet_text).first()
        if tweet is None:
            tweet = Tweet(tweetText=tweet_text,user_id=user.id)
            db.session.add(tweet)
            db.session.commit()
            flash('Tweet successfully added')

            return redirect('/')
        else:
            flash('Tweet already exists')
            print(user, tweet)

            return redirect(url_for('see_all_tweets'))





    # Get the number of Tweets


    # If the form was posted to this route,
    ## Get the data from the form

    ## Find out if there's already a user with the entered username
    ## If there is, save it in a variable: user
    ## Or if there is not, then create one and add it to the database


    ## If there already exists a tweet in the database with this text and this user id (the id of that user variable above...) ## Then flash a message about the tweet already existing
    ## And redirect to the list of all tweets

    ## Assuming we got past that redirect,
    ## Create a new tweet object with the text and user id
    ## And add it to the database
    ## Flash a message about a tweet being successfully added
    ## Redirect to the index page

    # PROVIDED: If the form did NOT validate / was not submitted
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    return render_template('index.html',form=form,num_tweets=tweet_num) # TODO 364: Add more arguments to the render_template invocation to send data to index.html

@app.route('/all_tweets')
def see_all_tweets():
    tweets = Tweet.query.all()
    tweets_users = tuple((t,User.query.filter_by(id=t.id).first()) for t in tweets)
    return render_template('all_tweets.html',all_tweets=tweets_users)

     # Replace with code
    # TODO 364: Fill in this view function so that it can successfully render the template all_tweets.html, which is provided.
    # HINT: Careful about what type the templating in all_tweets.html is expecting! It's a list of... not lists, but...
    # HINT #2: You'll have to make a query for the tweet and, based on that, another query for the username that goes with it...


@app.route('/all_users')
def see_all_users():
    users = User.query.all()
    return render_template('all_users.html',users=users)

    pass # Replace with code
    # TODO 364: Fill in this view function so it can successfully render the template all_users.html, which is provided.



@app.route('/longest_tweet')
def longest_tweet():
    tweets = Tweet.query.all()
    tweets_users = tuple((t,User.query.filter_by(id=t.id).first()) for t in tweets)

    dict_a = {}
    tweet_id = 0
    for tu in tweets_users:
        tweet_x = str(tu[0]).split('(')
        tweet = tweet_x[0]
        tweet_len = len(tweet) - tweet.count(' ')
        user_name = str(tu[1]).split('|')[0]
        dict_a[tweet_id] = (tweet,user_name,tweet_len)
        tweet_id = tweet_id + 1

    x = dict_a.items()
    key3 = lambda item:item[1][1]
    sorted_x = sorted(x,key=key3)
    max_tweet = sorted_x[0][1]
    print (max_tweet)
    tweet = max_tweet[0]
    user_name = max_tweet[1]
    data = (tweet,user_name)


    return render_template('longest_tweet.html',data=data)



# TODO 364
# Create another route (no scaffolding provided) at /longest_tweet with a view function get_longest_tweet (see details below for what it should do)
# TODO 364
# Create a template to accompany it called longest_tweet.html that extends from base.html.

# NOTE:
# This view function should compute and render a template (as shown in the sample application) that shows the text of the tweet currently saved in the database
# which has the most NON-WHITESPACE characters in it,
# and the username AND display name of the user that it belongs to.
#
#
# NOTE: This is different (or could be different) from the tweet with the most characters including whitespace!
# Any ties should be broken alphabetically (alphabetically by text of the tweet). HINT: Check out the chapter in the Python reference textbook on stable sorting.
# Check out /longest_tweet in the sample application for an example.

# HINT 2: The chapters in the Python reference textbook on:
## - Dictionary accumulation, the max value pattern
## - Sorting
# may be useful for this problem!


if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    app.run(use_reloader=True,debug=True) # The usual
