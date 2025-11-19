"""Minimal, dependency-free sample data generator for smoke tests.

This script creates a CSV at data/input/sample_sales.csv with the
essential columns used by the analysis scripts. It's intentionally
small and uses only the standard library so it can run without
installing pandas or other heavy packages.
"""
import csv
import os
import random
from datetime import datetime, timedelta


def generate_csv(path, n_records=1000):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    start = datetime(2023, 1, 1)
    regions = ['North', 'South', 'East', 'West']
    categories = ['Electronics', 'Clothing', 'Food', 'Books']
    payment_methods = ['Credit', 'Debit', 'Cash', 'Mobile']

    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        header = [
            'date', 'region', 'product_category', 'product_name',
            'sales_amount', 'quantity', 'customer_id', 'discount_percent',
            'payment_method'
        ]
        writer.writerow(header)

        for i in range(n_records):
            row_date = start + timedelta(hours=i)
            region = random.choice(regions)
            category = random.choice(categories)
            product = f'Product_{i%100}'
            sales_amount = round(random.uniform(10, 1000), 2)
            quantity = random.randint(1, 50)
            customer_id = f'CUST_{i%500}'
            discount = random.choice([0, 5, 10, 15, 20])
            payment = random.choice(payment_methods)

            writer.writerow([
                row_date.isoformat(), region, category, product,
                sales_amount, quantity, customer_id, discount, payment
            ])


if __name__ == '__main__':
    out = 'data/input/sample_sales.csv'
    print(f'Generating {out} (1000 records)')
    generate_csv(out, n_records=1000)
    print('Done. Files created:')
    print(f' - {out}')
