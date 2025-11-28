import sys
import random
import datetime

products = [{'code': 'P001', 'name': 'Highlighter', 'price': 25.00, 'stock': 50},
            {'code': 'P002', 'name': 'Ruler', 'price': 15.00, 'stock': 50},
            {'code': 'P003', 'name': 'Correction Tape', 'price': 30.00, 'stock': 50},
            {'code': 'P004', 'name': 'Binder', 'price': 50.00, 'stock': 50},
            {'code': 'P005', 'name': 'Paper', 'price': 20.00, 'stock': 50}]

transactions = []


def product_code_exists(code):
    return any(p['code'] == code for p in products)

def display_inventory():
    print('\n--- VIEW PRODUCTS ---')
    sorted_products = sorted(products, key=lambda p: p['code'])
    for product in sorted_products:
        print(f"Product Code: {product['code']} | Name: {product['name']} | Price: {product['price']} | Stock: {product['stock']}")
        return sorted_products

def add_product(code, name, price, stock = 0):
    print('\n--- ADD A PRODUCT ---')
    product_code = input('Enter product code: ').upper().strip()
    if product_code_exists(product_code):
        print('Product code already exists! Enter a unique code.')
        return False
    name = input('Enter product name: ').title()
    price = float(input('Enter product price: '))
    stock = int(input('Enter product stock: '))
    products.append({'code': product_code, 'name': name, 'price': price, 'stock': stock})
    print(f'Product Code: {product_code} | Name: {name} | Price: {price} | Stock: {stock} added successfully!')
    return True

def update_product(code, stock):
    print('\n--- UPDATE A PRODUCT ---')
    code = input('Enter product code: ').upper().strip()
    for product in products:
        if product['code'] == code:
            new_code = input('Enter new product code: ').upper().strip()
            if new_code != code and product_code_exists(new_code):
                print('New product code already exists! Enter a unique code.')
                return False
            stock = int(input('Enter new product stock: '))
            product['code'] = new_code
            product['stock'] = stock
            print(f'Product Code: {new_code} updated successfully!')
            return True
    print('Product code not found! Try again.')
    return False


def purchase_product(code, quantity):
    print('\n--- PURCHASE A PRODUCT ---')
    product_code = input('Enter product code: ').upper().strip()
    product = next((p for p in products if p['code'] == product_code), None)
    if product is None:
        print('Product code not found! Try again.')
        return
    quantity = int(input('Enter quantity: '))
    if product['stock'] >= quantity:
        total_price = product['price'] * quantity
        product['stock'] -= quantity
        transaction = {
            'product_code': product_code,
            'name': product['name'],
            'quantity': quantity,
            'price': product['price'],
            'total_price': total_price,
            'date': datetime.datetime.now()
        }
        transactions.append(transaction)
        print(
            f'Purchased Item:\n{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n{product["name"]}\n{quantity}\n{product["price"]}\n{total_price:.2f}')
    else:
        print('Insufficient stock! Quantity exceeds available stock.')


def delete_product():
    print('\n--- DELETE A PRODUCT ---')
    product_code = input('Enter product code: ').upper().strip()
    for product in products:
        if product['code'] == product_code:
            products.remove(product)
            print(f'Product Code: {product_code} deleted successfully!')
            return
    print('Product code not found! Try again.')


def search_product(keyword):
    print('\n--- SEARCH A PRODUCT ---')
    search_key = input('Enter product name: ').title()
    for product in products:
        if search_key in product['name'].title():
            print(
                f"Product Code: {product['code']} | Name: {product['name']} | Price: {product['price']} | Stock: {product['stock']}")
    if not products:
        print('No products match the searched name! Try again.')


def transaction_receipts():
    print('\n--- VIEW TRANSACTIONS ---')
    for transaction in transactions:
        date_str = transaction['date'].strftime('%Y-%m-%d %H:%M:%S')
        print(
            f"Product ID: {transaction['product_id']} | Name: {transaction['name']} | Quantity: {transaction['quantity']} | Total Price: {transaction['total_price']:.2f} | Date: {date_str}")
    if not transactions:
        print('No transactions found! Purchase a product first.')
        return

def exit_program():
    print('\nExiting the program...')
    sys.exit(0)

while True:
    print('\nHello, Welcome to UM MiniMart!')
    print('''\t1. Add a product
\t2. View products
\t3. Update a product
\t4. Purchase a product
\t5. View transactions
\t6. Delete a product
\t7. Search a product
\t8. Exit the program''')

    choice = input('Choose an action to perform (1-8): ')

    if choice == '1':
        display_inventory
    elif choice == '2':
        add_product()
    elif choice == '3':
        update_product()
    elif choice == '4':
        purchase_product()
    elif choice == '5':
        delete_product()
    elif choice == '6':
        search_product()
    elif choice == '7':
        transaction_receipts()
    elif choice == '8':
        exit_program()
    else:
        print('Invalid choice! Choose (1-8) only.')