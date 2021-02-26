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


def view_product(search_query=None):
    """View one of our fine products!"""
    store_products = Product.select().order_by(Product.product_id.desc())

    if search_query:
        store_products = store_products.where(Product.product_id == search_query)

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
        search_products()
        break


def search_products():
    """Search products by their Product ID"""
    print("To quit, enter q.")
    search_query = input('Search by Product ID: ')
    # Fix the infinite loop here
    while search_query != 'q':
        try:
            search_query = int(search_query)
        except ValueError:
            print("Not found. Please try again")
            search_query = input('Search by Product ID: ')
        else:
            if search_query < 1 or search_query > Product.select().count():
                print("Oops! You need to select a number within 1 and {}".format(Product.select().count()))
                search_query = input('Search by Product ID: ')
            else:
                view_product(search_query)
                break


def add_product():
    """Add a product to the inventory"""
    print("Enter your product")
    new_product_name = input('What is the name of your product? ')

    new_product_price = input('How much is your product? Please use $ before your entry: ')
    while True:
        try:
            new_product_price = int(float(new_product_price.replace('$', '')) * 100)
        except ValueError:
            print("Be sure to add the $ and no spaces in the dollar amount (ex. $2.99)")
            new_product_price = input('How much is your product? Please use $ before your entry: ')
        else:
            break

    new_product_quantity = input('How many products do you have? ')
    while True:
        try:
            new_product_quantity = int(new_product_quantity)
        except ValueError:
            print("Please only put in an integer")
            new_product_quantity = input('How many products do you have? ')
        else:
            break

    if new_product_name and input('Save Entry? [yn] ').lower() != 'n':
        try:
            Product.create(
                product_name=new_product_name,
                product_price=new_product_price,
                product_quantity=new_product_quantity
            )
            print("Saved successfully!")
        # I saw how to write this code from another pythonista's Project 4 in their github:
        # https://github.com/daniellerg/CSV_Inventory_App
        except IntegrityError:
            print("That item has already been added to the inventory.")
            duplicate_record = Product.get(product_name=new_product_name)
            duplicate_record.product_name = new_product_name
            duplicate_record.product_quantity = new_product_quantity
            duplicate_record.product_price = new_product_price
            duplicate_record.save()
        next_step()
    else:
        print("Entry was not saved")
        next_step()


# A function to create a back_up csv
def create_back_up():
    """Back up your current inventory"""
    products = Product.select().order_by(Product.product_id.desc())
    with open('back_up.csv', 'w') as csvfile:
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
    print("Your inventory has been saved to a back up file!")
    next_step()


def next_step():
    next_action = input('Press ENTER/RETURN to return to main menu').lower().strip()
    if next_action:
        display_loop()


menu = OrderedDict([
    ('v', view_product),
    ('a', add_product),
    ('b', create_back_up),
])

if __name__ == '__main__':
    initialize()
    csv_to_database()
    display_loop()
