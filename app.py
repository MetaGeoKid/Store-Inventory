#!/usr/bin/env python3

from collections import OrderedDict
import datetime
import csv
import os
import sys

from peewee import *

db = SqliteDatabase('inventory.db')


class Product(Model):
    product_id = AutoField(primary_key=True)
    product_name = CharField(max_length=255, unique=True)
    product_quantity = IntegerField()
    product_price = IntegerField()
    data_updated = DateTimeField(default=datetime.datetime.now)


    class Meta:
        database = db


# a function that connects to a database and creates tables for it
def initialize():
    db.connect()
    db.create_tables([Product], safe=True)


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# a function to read the inventory.csv file and create a variable by row in the db
def csv_to_database():
    with open('inventory.csv', newline='') as csvfile:
        inventory_reader = csv.DictReader(csvfile, delimiter=',')
        rows = list(inventory_reader)
        for row in rows[1:20]:
            row['product_quantity'] = int(row['product_quantity'])
            row['product_price'] = float(row['product_price'].replace('$','')) * 100
            row['date_updated'] = datetime.datetime.strptime(row['date_updated'], '%m/%d/%Y')
            Product.create(
                product_name=row['product_name'],
                product_price=row['product_price'],
                product_quantity=row['product_quantity'],
                date_updated=row['date_updated']
            ).save()
"""
            except IntegrityError:
                item_record = Product.get(product_name=row['product_name'])
                item_record.product_name = row['product_name']
                item_record.product_quantity = row['product_quantity']
                item_record.product_price = row['product_price']
                item_record.date_updated = row['date_updated']
                item_record.save()
"""

# A function to display the menu



# A function to view a product



# A function to search for a product by ID



# A function to add an item to the db



# A function to create a back_up db

"""
# A menu to look at
menu = OrderedDict([
    ('a', add_product),
    ('v', view_product),
    ('b', back_up)
])
"""
if __name__ == '__main__':
    initialize()
    csv_to_database()
