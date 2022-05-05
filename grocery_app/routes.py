from flask import Blueprint, request, render_template, redirect, url_for, flash
from datetime import date, datetime
from grocery_app.models import GroceryStore, GroceryItem, User
from grocery_app.forms import GroceryStoreForm, GroceryItemForm, LoginForm, SignUpForm

# Import app and db from events_app package so that we can run app
from grocery_app.extensions import app, db, bcrypt

from flask_login import login_required, login_user, logout_user, current_user

main = Blueprint("main", __name__)
auth = Blueprint("auth", __name__)

##########################################
#           Routes                       #
##########################################

@main.route('/')
def homepage():
    all_stores = GroceryStore.query.all()
    return render_template('home.html', all_stores=all_stores)

@main.route('/new_store', methods=['GET', 'POST'])
@login_required
def new_store():
    form = GroceryStoreForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            grocery_title = request.form.get('title')
            grocery_address = request.form.get('address')
            created_by = current_user
        
            new_grocery = GroceryStore(title=grocery_title, address=grocery_address, created_by=created_by)

            db.session.add(new_grocery)
            db.session.commit()

            flash('Successfully Added!')
            return redirect(url_for('main.store_detail', store_id=new_grocery.id))
    return render_template('new_store.html', form=form)

@main.route('/new_item', methods=['GET', 'POST'])
@login_required
def new_item():
    form = GroceryItemForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            item_name = request.form.get('name')
            item_price = request.form.get('price')
            item_category = request.form.get('category')
            photo_url = request.form.get('photo_url')
            store_id = int(request.form.get('store'))
            created_by = current_user

            new_item = GroceryItem(name=item_name, price=item_price, category=item_category, photo_url=photo_url, store_id=store_id, created_by=created_by)

            db.session.add(new_item)
            db.session.commit()

            flash('Successfully Added!')
            return redirect(url_for('main.item_detail', item_id=new_item.id))

    return render_template('new_item.html', form=form)

@main.route('/store/<store_id>', methods=['GET', 'POST'])
@login_required
def store_detail(store_id):
    store = GroceryStore.query.get(store_id)
    form = GroceryStoreForm(obj=store)

    if request.method == 'POST':
        if form.validate_on_submit():
            store.title = form.title.data
            store.address = form.address.data

            db.session.add(store)
            db.session.commit()

            flash('Successfully Updated!')
            return redirect(url_for('main.store_detail', store_id=store.id))

    return render_template('store_detail.html', store=store, form=form)

@main.route('/item/<item_id>', methods=['GET', 'POST'])
@login_required
def item_detail(item_id):
    item = GroceryItem.query.get(item_id)
    form = GroceryItemForm(obj=item)

    if request.method == 'POST':
        if form.validate_on_submit:
            item.name = form.name.data
            item.price = form.price.data
            item.category = form.category.data
            item.photo_url = form.photo_url.data
            item.store = form.store.data

            db.session.add(item)
            db.session.commit()

            flash('Successfully Updated!')
            return redirect(url_for('main.item_detail', item_id=item.id))

    item = GroceryItem.query.get(item_id)
    return render_template('item_detail.html', item=item, form=form)

@main.route('/add_to_shopping_list/<item_id>', methods=['GET', 'POST'])
def add_to_shopping_list(item_id):
    item = GroceryItem.query.get(item_id)
    current_user.groceryitems.append(item)
    db.session.add(current_user)
    db.session.commit()
    flash(f'{item.name} is added to the shopping list!')
    return redirect(url_for('main.item_detail', item_id=item.id))

@main.route('/shopping_list')
@login_required
def shopping_list():
    user_shopping_list = current_user.groceryitems
    return render_template('shopping_list.html', shopping_list=user_shopping_list)

# Auth route
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    print('in signup')
    form = SignUpForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.data['password']).decode('utf-8')
            user = User(
                username=form.username.data,
                password=hashed_password
            )
            db.session.add(user)
            db.session.commit()
            flash('Account Created.')
            print('created')
            return redirect(url_for('auth.login'))
    print(form.errors)
    return render_template('signup.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.homepage'))
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.homepage'))
