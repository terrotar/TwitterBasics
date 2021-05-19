from flask import render_template, redirect, request, url_for

from flask_login import login_user, logout_user

from app import app, db
from app.models import User, Post


@app.errorhandler(404)
def page_not_found(error):
    return 'A página não existe. Provavelmente você não está logado.', 404


@app.route("/", methods=["GET"])
def home():
    all_posts = Post.query.all()
    return render_template("home.html",
                           all_posts=all_posts)


@app.route("/register", methods=["GET", "POST"])
def register():
    if(request.method == 'POST'):
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        username = request.form['username']
        if(email and password and name and username):
            all_users = User.query.all()
            for user in all_users:
                if(user.username == username):
                    return render_template('register.html',
                                           error_username=True)
                elif(user.email == email):
                    return render_template('register.html',
                                           error_email=True)
            new_user = User(username, password, name, email)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('register.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if(request.method == 'POST'):
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        # Check if inserted password is the same as the registered in the email
        if not user or not user.verify_password(password):
            return render_template('home.html',
                                   error=True)

        login_user(user)
        all_posts = Post.query.all()
        return render_template("home.html",
                               all_posts=all_posts)

    return render_template("home.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/update_pwd', methods=["GET", "POST"])
def update_pwd():
    if(request.method == 'POST'):
        old_pwd = request.form['old_pwd']
        new_pwd = request.form['new_pwd']
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if not user or not user.verify_password(old_pwd):
            return render_template('alterar_senha.html',
                                   error=True)
        else:
            user.set_password(new_pwd)
            db.session.commit()
            return redirect(url_for('logout'))
    return render_template('alterar_senha.html')


@app.route('/update_data', methods=["GET", "POST"])
def update_data():
    if(request.method == 'POST'):
        password = request.form['password']
        email = request.form['email']
        name = request.form['name']
        username = request.form['username']
        user = User.query.filter_by(email=email).first()
        if not user or not user.verify_password(password):
            return render_template('alterar_dados.html',
                                   error=True)
        else:
            user.name = name
            user.username = username
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('alterar_dados.html')


@app.route('/delete_user', methods=["GET", "POST"])
def delete_user():
    if(request.method == 'POST'):
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user or not user.verify_password(password):
            return render_template('deletar_conta.html',
                                   error=True)
        else:
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for('home'))
    else:
        return render_template('deletar_conta.html',
                               error=False)


@app.route('/followers/<user>/<username>', methods=["GET"])
def followers(user, username):
    logged_user = User.query.filter_by(username=user).first()
    perfil_user = User.query.filter_by(username=username).first()
    followers = perfil_user.followers.split(";")
    del followers[0]
    return render_template('search_perfil.html',
                           username=logged_user.username,
                           user=perfil_user,
                           followers=followers)


@app.route('/profile/<username>', methods=["GET"])
def profile(username):
    user = User.query.filter_by(username=username).first()
    user_posts = user.posts
    return render_template('perfil.html',
                           posts_owner=user,
                           user_posts=user_posts)


@app.route('/search', methods=["GET"])
def search():
    if(request.method == 'GET'):
        search = request.args.get('search')
        user = User.query.filter_by(username=search).first()
        if user:
            return render_template('search_perfil.html',
                                   username=user.username,
                                   user=user)
        else:
            return redirect(url_for('home'))


@app.route('/follow/<user>/<username>', methods=["GET"])
def follow(user, username):
    logged_user = User.query.filter_by(username=user).first()
    perfil_user = User.query.filter_by(username=username).first()
    following = logged_user.following.split(";")
    for user in following:
        if(perfil_user.username == user):
            return render_template('search_perfil.html',
                                   username=logged_user.username,
                                   user=perfil_user,
                                   follow_error=True)
    logged_user.follow(perfil_user)
    db.session.commit()
    return render_template('search_perfil.html',
                           username=logged_user.username,
                           user=perfil_user)


@app.route('/unfollow/<user>/<username>', methods=["GET"])
def unfollow(user, username):
    logged_user = User.query.filter_by(username=user).first()
    perfil_user = User.query.filter_by(username=username).first()
    following = logged_user.following.split(";")
    # a partir daqui atualizar seguidores do perfil_user
    followers = perfil_user.followers.split(";")
    for user in followers:
        if(len(followers) < 1):
            return render_template('search_perfil.html',
                                   username=logged_user.username,
                                   user=perfil_user,
                                   unfollow_allowed=True)
        elif(user == logged_user.username):
            followers.remove(user)
            followers = str(followers)
            perfil_user.followers = followers
            db.session.commit()
    # aqui acaba
    for user in following:
        if(user == perfil_user.username):
            following.remove(user)
            following = str(following)
            logged_user.following = following
            db.session.commit()
            return render_template('search_perfil.html',
                                   username=logged_user.username,
                                   user=perfil_user,
                                   unfollow_allowed=True)
    return render_template('search_perfil.html',
                           username=logged_user.username,
                           user=perfil_user,
                           unfollow_error=True)


@ app.route('/following/<user>/<username>', methods=["GET"])
def following(user, username):
    logged_user = User.query.filter_by(username=user).first()
    perfil_user = User.query.filter_by(username=username).first()
    following = perfil_user.following.split(";")
    del following[0]
    return render_template('search_perfil.html',
                           username=logged_user.username,
                           user=perfil_user,
                           following=following)


@app.route('/tweet/<username>', methods=["GET", "POST"])
def tweet(username):
    if(request.method == 'POST'):
        user = User.query.filter_by(username=username).first()
        content = request.form['content']
        post = Post(content=content, owner=user)
        db.session.add(post)
        db.session.commit()
        all_posts = Post.query.all()
    return render_template("home.html",
                           all_posts=all_posts)


@app.route('/tweet/deletar/<post_id>', methods=["GET"])
def remove_tweet(post_id):
    post = Post.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('home'))


app.run(debug=True)
