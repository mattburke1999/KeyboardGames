from flask import render_template

def home():
    return render_template('index.html')

def first_circle():
    return render_template('firstCircle.html')

def second_circle():
    return render_template('secondCircle.html')

def disappearing_circle():
    return render_template('disappearingCircle.html')

def disappearing_dot():
    return render_template('disappearingDot.html')

def shrinking_circle():
    return render_template('shrinkingCircle.html')