from flask import Flask,render_template,request,redirect,url_for,session,flash
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash


app=Flask(__name__)

app.secret_key="Yoga@123SQL"

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root' 
app.config['MYSQL_PASSWORD']='Yoga_1010@SQL'
app.config['MYSQL_DB']='list_student'   
mysql =MySQL(app)



class User:
    def __init__(self,username,password):
        self.username=username
        self.password=password  
class signupform(FlaskForm):
    username=StringField('Username',validators=[InputRequired(),Length(min=5,max=19)])
    password=PasswordField('Password',validators=[InputRequired(),Length(min=7,max=25)])
    submit=SubmitField('Signup') 
class loginform(FlaskForm):
    username=StringField('Username',validators=[InputRequired(),Length(min=5,max=19)])
    password=PasswordField('Password',validators=[InputRequired(),Length(min=7,max=25)])
    submit=SubmitField('Login')   


@app.route("/",methods=["GET","POST"])
def signup():
    form=signupform()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data         
        hashedpassword=generate_password_hash(password)
        cur=mysql.connection.cursor()
        cur.execute("SELECT * FROM signup WHERE username=%s",(username,))
        exec_user= cur.fetchone()
        if exec_user:
            cur.close()
            flash("user name is already their,choose another name",'danger')
            return redirect(url_for("signup"))
        cur.execute("INSERT INTO signup (username,password) Values(%s,%s) ",(username,hashedpassword))  
        mysql.connection.commit()
        cur.close()  
        flash("singup successfull",'success')
        return redirect(url_for('login'))
    return render_template('signup.html',form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = loginform()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        cur = mysql.connection.cursor()
        cur.execute("SELECT  username, password FROM signup WHERE username = %s", (username,))
        user_data = cur.fetchone()
        cur.close()
        if user_data:
            storedpassword=user_data[1]
            if check_password_hash(storedpassword,password):
                user = User(username=user_data[0], password=user_data[1])
                session['username'] = user.username
                flash('Login successful', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid password', 'danger')
        else:
            flash('Invalid username', 'danger')
    return render_template('login.html', form=form)


@app.route("/home")
def home():
    if "username" in session:
        user_input = session['username']
        return render_template("home.html", user_input=user_input)
    else:
        flash("Please log in to access this page.", 'danger')
        return redirect(url_for('login'))


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if "cart" not in session:
        session["cart"] = []    

    product_name = request.form["product_name"]
    product_price = request.form["product_price"]

    session["cart"].append({"name": product_name, "price": product_price})
    session.modified = True
    flash(f'{product_name} added to cart!', 'success')
    return redirect(url_for("home"))


@app.route("/cart")
def cart():
    cart_items = session.get("cart", [])
    return render_template("cart.html", cart_items=cart_items)

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully", 'info')
    return redirect(url_for("login"))


if __name__== "__main__":
    app.run(debug=True)