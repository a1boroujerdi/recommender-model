import random
import csv
from datetime import datetime, timedelta

# ------------ configurable master data ------------ #
phones = [
    ("iPhone 13 mini", 599),
    ("iPhone 13", 699),
    ("iPhone 13 Pro", 899),
    ("iPhone 14", 799),
    ("iPhone 14 Plus", 899),
    ("iPhone 14 Pro", 999),
    ("iPhone 14 Pro Max", 1099),
    ("iPhone 15", 899),
    ("iPhone 15 Pro", 1099),
    ("iPhone 15 Pro Max", 1199),
]

phone_accessories = [
    ("MagSafe Charger", 39),
    ("MagSafe Battery Pack", 99),
    ("Lightning to USB-C Cable", 19),
    ("20W USB-C Power Adapter", 19),
    ("AirPods (2nd Gen)", 129),
    ("AirPods Pro (2nd Gen)", 249),
    ("AirPods Max", 549),
    ("Silicone Case", 59),
    ("Leather Case", 69),
    ("Tempered Glass Protector (2-pack)", 14.99),
]

laptops = [
    ("MacBook Air M2 13-inch", 1099),
    ("MacBook Air M3 15-inch", 1299),
    ("MacBook Pro 14-inch M3 Pro", 1999),
    ("MacBook Pro 16-inch M3 Max", 3499),
]

laptop_accessories = [
    ("USB-C to MAGSAFE 3 Cable 2 m", 49),
    ("USB-C Digital AV Multiport Adapter", 69),
    ("Magic Mouse", 79),
    ("Magic Keyboard with Touch ID", 149),
]

monitors = [
    ("Apple Studio Display Standard Glass", 1599),
    ("LG UltraFine 5K 27-inch", 1299),
    ("Dell UltraSharp 27 4K USB-C Hub Monitor", 649),
]
batteries = [("AA Batteries (4-pack)", 3.84), ("AAA Batteries (4-pack)", 2.99)]

cities = [
    ("New York City", "NY", "10001"),
    ("Los Angeles", "CA", "90001"),
    ("San Francisco", "CA", "94016"),
    ("Seattle", "WA", "98101"),
    ("Boston", "MA", "02215"),
    ("Austin", "TX", "73301"),
    ("Dallas", "TX", "75001"),
    ("Atlanta", "GA", "30301"),
    ("Portland", "OR", "97035"),
]

street_names = [
    "1st", "2nd", "3rd", "4th", "5th", "6th", "7th",
    "8th", "9th", "10th", "11th", "12th", "Center",
    "Maple", "Oak", "Pine", "Cedar", "Hill", "Sunset",
    "Ridge", "Spruce", "Elm", "Jackson", "Lincoln", "Willow",
]

# ------------ helper functions ------------ #
def random_date(start, end):
    """random datetime between start and end"""
    delta = end - start
    seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=seconds)

def random_address():
    num = random.randint(10, 999)
    street = random.choice(street_names)
    kind = random.choice(["St", "Ave", "Rd", "Blvd", "Ln"])
    city, state, zipc = random.choice(cities)
    return f'{num} {street} {kind}, {city}, {state} {zipc}'

# ------------ dataset generation ------------ #
records = []
order_id = 1
start_date = datetime(2024, 1, 1, 0, 0, 0)
end_date = datetime(2024, 12, 31, 23, 59, 59)

# 1) every phone with every compatible accessory (nested loop)
for phone_name, phone_price in phones:
    for acc_name, acc_price in phone_accessories:
        order_time = random_date(start_date, end_date).strftime("%m/%d/%y %H:%M")
        address = random_address()
        # phone row
        records.append([
            order_id, phone_name, 1, phone_price, order_time, address
        ])
        # accessory row
        qty = random.randint(1, 2)
        records.append([
            order_id, acc_name, qty, acc_price, order_time, address
        ])
        order_id += 1

# 2) every laptop with every accessory
for lap_name, lap_price in laptops:
    for acc_name, acc_price in laptop_accessories:
        order_time = random_date(start_date, end_date).strftime("%m/%d/%y %H:%M")
        address = random_address()
        records.append([order_id, lap_name, 1, lap_price, order_time, address])
        qty = random.randint(1, 2)
        records.append([order_id, acc_name, qty, acc_price, order_time, address])
        order_id += 1

# 3) monitor + batteries combos
for mon_name, mon_price in monitors:
    for bat_name, bat_price in batteries:
        order_time = random_date(start_date, end_date).strftime("%m/%d/%y %H:%M")
        address = random_address()
        records.append([order_id, mon_name, 1, mon_price, order_time, address])
        qty = random.randint(1, 4)
        records.append([order_id, bat_name, qty, bat_price, order_time, address])
        order_id += 1

# 4) a bunch of random single-item orders for realism
for _ in range(2000):
    order_time = random_date(start_date, end_date).strftime("%m/%d/%y %H:%M")
    address = random_address()
    product, price = random.choice(
        phones + phone_accessories + laptops + laptop_accessories + monitors + batteries
    )
    qty = 1 if product.startswith(("iPhone", "MacBook", "Apple Studio Display", "LG", "Dell")) else random.randint(1, 3)
    records.append([order_id, product, qty, price, order_time, address])
    order_id += 1

# ------------ write to CSV ------------ #
header = ["Order ID", "Product", "Quantity Ordered", "Price Each", "Order Date", "Purchase Address"]

with open("synthetic_sales.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(records)

print(f"Generated {len(records)} rows → synthetic_sales.csv")
