import sys
import random
import datetime

products = [
    {'code': 'P001', 'name': 'Highlighter', 'price': 25.00, 'stock': 50},
    {'code': 'P002', 'name': 'Ruler', 'price': 15.00, 'stock': 50},
    {'code': 'P003', 'name': 'Correction Tape', 'price': 30.00, 'stock': 50},
    {'code': 'P004', 'name': 'Binder', 'price': 50.00, 'stock': 50},
    {'code': 'P005', 'name': 'Paper', 'price': 20.00, 'stock': 50}]

transactions = []

def product_code_exists(code):
    return any(p['code'] == code for p in products)

def positive_stock(value):
    try:
        number = float(value)
        return number if number >= 0 else None
    except:
        return None

def display_inventory():
    print("\n--- VIEW PRODUCTS ---")
    sorted_list = sorted(products, key=lambda p: p['code'])
    for p in sorted_list:
        print(f"Code: {p['code']} | Name: {p['name']} | Price: {p['price']} | Stock: {p['stock']}")
    return sorted_list

def add_product(code, name, price, stock=0):
    print("\n--- ADD PRODUCT ---")
    code = code.upper().strip()

    if product_code_exists(code):
        print("Product code already exists. Enter a unique code.")
        return False

    if price < 0 or stock < 0:
        print("Price and stock must be non-negative.")
        return False

    products.append({
        'code': code,
        'name': name.title(),
        'price': price,
        'stock': stock
    })

    print(f"Product {code} added successfully!")
    return True

def update_stock(code, quantity):
    print("\n--- UPDATE STOCK ---")
    code = code.upper().strip()

    for p in products:
        if p['code'] == code:
            if quantity < 0:
                print("Quantity cannot be negative!")
                return False

            p['stock'] = quantity
            print(f"Stock updated for {code}.")
            return True

    print("Product not found.")
    return False

def purchase_product(code, quantity):
    print("\n--- PURCHASE PRODUCT ---")

    code = code.upper().strip()
    product = next((p for p in products if p['code'] == code), None)

    if product is None:
        print("Product not found.")
        return False

    if quantity <= 0:
        print("Invalid quantity.")
        return False

    if product['stock'] < quantity:
        print("Insufficient stock.")
        return False

    product['stock'] -= quantity
    total = product['price'] * quantity

    receipt_no = random.randint(100000, 999999)
    now = datetime.datetime.now()

    transactions.append({
        'receipt': receipt_no,
        'code': code,
        'name': product['name'],
        'quantity': quantity,
        'total': total,
        'date': now
    })

    print("\n--- RECEIPT TRANSACTION ---")
    print(f"Receipt No.: {receipt_no}")
    print(f"Date: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Item: {product['name']}")
    print(f"Quantity: {quantity}")
    print(f"Unit Price: {product['price']}")
    print(f"Total: {total:.2f}")
    return True

def delete_product(code):
    print("\n--- DELETE PRODUCT ---")
    code = code.upper().strip()

    for p in products:
        if p['code'] == code:
            products.remove(p)
            print(f"Product {code} deleted successfully!")
            return True

    print("Product not found.")
    return False

def search_products(keyword):
    print("\n--- SEARCH RESULTS ---")
    keyword = keyword.lower()

    results = [p for p in products if keyword in p['name'].lower()]

    if results:
        for p in results:
            print(f"Code {p['code']} | Name: {p['name']} | Price: {p['price']} | Stock: {p['stock']}")
    else:
        print("No matching products found.")

    return results

def main():
    if len(sys.argv) > 1:
        print(f"Hello, {sys.argv[1]}! Welcome to UM MiniMart.")
    else:
        print("\nHello, Welcome to UM MiniMart!")

    while True:
        print("""
1. View Products
2. Add Product
3. Update Stock
4. Purchase Product
5. Delete Product
6. Search Product
7. View Transactions
8. Exit Program
""")

        choice = input("Enter a number (1-8): ")

        if choice == "1":
            display_inventory()

        elif choice == "2":
            code = input("Enter product code: ")
            name = input("Enter product name: ")
            price = positive_stock(input("Enter price: "))
            stock = positive_stock(input("Enter stock: "))

            if price is None or stock is None:
                print("Invalid input. Try again.")
            else:
                add_product(code, name, price, int(stock))

        elif choice == "3":
            code = input("Enter product code: ")
            qty = positive_stock(input("Enter new stock: "))
            if qty is None:
                print("Invalid input. Try again.")
            else:
                update_stock(code, int(qty))

        elif choice == "4":
            code = input("Enter product code: ")
            qty = positive_stock(input("Enter quantity: "))
            if qty is None:
                print("Invalid quantity. Try again.")
            else:
                purchase_product(code, int(qty))

        elif choice == "5":
            code = input("Enter product code: ")
            delete_product(code)

        elif choice == "6":
            keyword = input("Search keyword: ")
            search_products(keyword)

        elif choice == "7":
            print("\n--- RECEIPT TRANSACTIONS ---")
            if not transactions:
                print("No transactions yet. Purchase a product first.")
            else:
                for t in transactions:
                    print(f"{t['receipt']} | Code: {t['code']} | Name: {t['name']} | Quantity: {t['quantity']} | Total: {t['total']}")

        elif choice == "8":
            print("Exiting the program…")
            break

        else:
            print("Invalid choice! Enter a number (1–8).")

main()