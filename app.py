#!/usr/bin/env python3

from collections import OrderedDict
import datetime
import csv
import os


from peewee import *

db = SqliteDatabase('inventory.db')


class Product(Model):
    product_id = AutoField(primary_key=True)
    product_name = CharField(max_length=255, unique=True)
    product_quantity = IntegerField()
    product_price = IntegerField()
    date_updated = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


# a function that connects to a database and creates tables for it
def initialize():
    db.connect()
    db.create_tables([Product], safe=True)
    db.close()


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


# a function to read the inventory.csv file and create a variable by row in the db
def csv_to_database():
    with open('inventory.csv') as csvfile:
        inventory_reader = csv.DictReader(csvfile, delimiter=',')
        rows = list(inventory_reader)
        for row in rows:
            row['product_quantity'] = int(row['product_quantity'])
            row['product_price'] = float(row['product_price'].replace('$', '')) * 100
            row['date_updated'] = datetime.datetime.strptime(row['date_updated'], '%m/%d/%Y')
            try:
                Product.create(
                    product_name=row['product_name'],
                    product_price=row['product_price'],
                    product_quantity=row['product_quantity'],
                    date_updated=row['date_updated']
                ).save()
            # I saw how to write this code from another pythonista's Project 4 in their github:
            # https://github.com/daniellerg/CSV_Inventory_App
            except IntegrityError:
                item_record = Product.get(product_name=row['product_name'])
                item_record.product_name = row['product_name']
                item_record.product_quantity = row['product_quantity']
                item_record.product_price = row['product_price']
                item_record.date_updated = row['date_updated']
                item_record.save()


def display_loop():
    choice = None

    while choice != 'q':
        clear_console()
        print("Enter 'q' to quit")
        for key, value in menu.items():
            print('{} {}'.format(key, value.__doc__))
        choice = input('Action: ').lower().strip()

        if choice in menu:
            clear_console()
            menu[choice]()


def view_product():
    """View one of our fine products!"""
    store_products = Product.select().order_by(Product.product_id.desc())
    for product in store_products:
        timestamp = product.date_updated.strftime('%A %B  %d, %Y %I:%M%p')
        clear_console()
        price = (product.product_price / 100)
        print('=' * len(timestamp))
        # learned how to format only two decimal places through:
        # https://stackoverflow.com/questions/6149006/display-a-float-with-two-decimal-places-in-python
        print(" Product ID:", product.product_id, '\n',
              "Product Name:", product.product_name, '\n',
              "Product Price:", ('$' + str("{0:.2f}".format(price))), '\n',
              "Product Quantity:", product.product_quantity, '\n',
              timestamp)
        print('=' * len(timestamp))
        print('n) next product')
        print('q) return to main menu')
        print('d) delete product')

        next_action = input('Action: [Nqd] ').lower().strip()
        if next_action == 'q':
            break
        elif next_action == 'd':
            delete_product(product)


def add_product():
    """Add a product to the inventory"""
    print("Enter your product")
    new_product_name = input('What is the name of your product? ')
    new_product_price = input('How much is your product? Please use $ before your entry: ')
    new_product_price = int(float(new_product_price.replace('$', '')) * 100)
    new_product_quantity = input('How many products do you have? ')

    if new_product_quantity:
        if input('Save Entry? [yn] ').lower() != 'n':
            Product.create(product_name=new_product_name,
                           product_price=new_product_price,
                           product_quantity=new_product_quantity)
            print("Saved successfully!")


# A function to create a back_up csv
def create_back_up():
    """Back up your current inventory"""
    products = Product.select().order_by(Product.product_id.desc())
    with open('back_up.csv', 'a') as csvfile:
        fieldnames = ['product_name', 'product_price', 'product_quantity', 'date_updated']
        back_up_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        back_up_writer.writeheader()
        for product in products:
            back_up_writer.writerow({
                'product_name': product.product_name,
                'product_price': ('$' + str("{0:.2f}".format(product.product_price / 100))),
                'product_quantity': product.product_quantity,
                'date_updated': product.date_updated.strftime('%m/%d/%Y')
            })


def delete_product(product):
    """Delete an entry"""
    if input("Are you sure? [yN] ").lower() == 'y':
        product.delete_instance()
        print("Product deleted!")


# A menu to look at
menu = OrderedDict([
    ('v', view_product),
    ('a', add_product),
    ('b', create_back_up),
])

if __name__ == '__main__':
    initialize()
    csv_to_database()
    display_loop()
