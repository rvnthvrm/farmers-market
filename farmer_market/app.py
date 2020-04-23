from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
)


app = Flask(__name__)
app.secret_key = "secret key"


PRODUCTS = [
        {'Item': 'CH1', 'Name': 'Chai', 'Price': 3.11, 'img': '/static/images/chai1.jpg'},
        {'Item': 'AP1', 'Name': 'Apples', 'Price': 6.00, 'img': '/static/images/apples1.jpg'},
        {'Item': 'CF1', 'Name': 'Coffee', 'Price': 11.23, 'img': '/static/images/coffee.jpg'},
        {'Item': 'MK1', 'Name': 'Milk', 'Price': 4.75, 'img': '/static/images/milk1.jpg'},
        {'Item': 'OM1', 'Name': 'Oatmeals', 'Price': 3.69, 'img': '/static/images/oatmeals1.jpg'}
    ]

DISCOUNT_CONFIG = {
    'CH1': ['CHMK'],
    'AP1': ['APPL'],
    'CF1': ['BOGO'],
    'MK1': [],
    'OM1': ['APOM']
}


def get_item_from_products(item_id):
    return next((i for i in PRODUCTS if i['Item'] == item_id))


def git_item_from_session_if_exist(code):
    return next((i for i in session['cart_item'] if i['code'] == code), None)


@app.route('/add', methods=['POST'])
def add_product_to_cart():
    _quantity = int(request.form['quantity'])
    _code = request.form['code']

    if not all([_quantity, _code]):
        return 'Error while adding item to cart'

    product_details = [
            {
                'name': get_item_from_products(_code)['Name'],
                'code': get_item_from_products(_code)['Item'],
                'quantity': _quantity,
                'price': get_item_from_products(_code)['Price'],
                'image': get_item_from_products(_code)['img'],
                'total_price': round(_quantity * get_item_from_products(_code)['Price'], 2)
            }
    ]

    session.modified = True

    if not session.get('cart_item'):
        all_total_price = 0
        all_total_quantity = 0

        session['cart_item'] = product_details
        all_total_quantity += _quantity
        all_total_price += _quantity * get_item_from_products(_code)['Price']
    else:
        key = git_item_from_session_if_exist(_code)

        if key:
            old_quantity = key['quantity']
            total_quantity = old_quantity + _quantity
            key['quantity'] = total_quantity
            key['total_price'] = round(total_quantity * get_item_from_products(_code)['Price'], 2)
        else:
            session['cart_item'].append(product_details[0])

        all_total_quantity = session['all_total_quantity'] + _quantity

    session['all_total_quantity'] = all_total_quantity

    run_discount_rules(session['cart_item'])

    session['all_total_price'] = round(
        sum(
            [i['total_price'] for i in session['cart_item']]
        ), 2
    )

    return redirect(url_for('.products'))


def run_discount_rules(cart_items):
    discount_result = []

    def update_discount(code, discount_price):
        item = git_item_from_session_if_exist(code)
        if not item:
            session['cart_item'].append(
                {
                    'code': code,
                    'total_price': -discount_price,
                    'image': '/static/images/discount.jpg',
                    'discount': True
                }
            )

        else:
            if discount_price != item['total_price']:
                item['total_price'] = -discount_price

    for item in cart_items:
        if item['code'] == 'CF1' and item['quantity'] // 2 >= 1:
            discount_price = item['quantity'] // 2 * get_item_from_products(item['code'])['Price']
            update_discount('BOGO', discount_price)

        if item['code'] == 'AP1' and item['quantity'] // 3 >= 1:
            discount_price = item['quantity'] // 3 * 4.5
            update_discount('APPL', discount_price)

        apples = git_item_from_session_if_exist('AP1')
        if item['code'] == 'OM1' and apples:
            discount_price = apples['total_price'] / 2
            update_discount('APOM', discount_price)

        milk = git_item_from_session_if_exist('MK1')
        if item['code'] == 'CH1' and milk:
            discount_price = get_item_from_products('MK1')['Price']
            update_discount('CHMK', discount_price)

    return discount_result


@app.route('/')
def products():
    return render_template('main.html', products=PRODUCTS)


@app.route('/empty')
def empty_cart():
    try:
        session.clear()
        return redirect(url_for('.products'))
    except Exception as e:
        print(e)


@app.route('/delete/<string:code>')
def delete_product(code):
    quantity_of_deleted_items = sum([
        i['quantity'] for i in session['cart_item'] if all(
            [i['code'] == code, i['code'] in DISCOUNT_CONFIG[code]]
        )
    ])
    price_of_deleted_items = sum([
        i['price'] for i in session['cart_item'] if all(
            [i['code'] == code, i['code'] in DISCOUNT_CONFIG[code]]
        )
    ])

    session['all_total_quantity'] = session['all_total_quantity'] - quantity_of_deleted_items
    session['all_total_price'] = session['all_total_price'] - (price_of_deleted_items * quantity_of_deleted_items)

    session['cart_item'] = [
        i for i in session['cart_item'] if all(
            [i['code'] != code, i['code'] not in DISCOUNT_CONFIG[code]]
        )
    ]
    run_discount_rules(session['cart_item'])
    return redirect(url_for('.products'))
