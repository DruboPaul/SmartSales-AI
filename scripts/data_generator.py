import csv
import json
import time
import random
import datetime
from faker import Faker # You might need to install this: pip install faker

# Setup
fake = Faker()
PRODUCT_CATEGORIES = ['T-Shirt', 'Jeans', 'Sneakers', 'Dress', 'Jacket']
STORES = ['Berlin_01', 'Hamburg_02', 'Munich_01', 'Online_Store']

def generate_product():
    return {
        'product_id': fake.uuid4(),
        'category': random.choice(PRODUCT_CATEGORIES),
        'price': round(random.uniform(10.0, 150.0), 2),
        'cost': round(random.uniform(5.0, 80.0), 2),
        'timestamp': datetime.datetime.now().isoformat()
    }

# --- MODE 1: BATCH (Generate a CSV file) ---
def generate_batch_csv(filename='daily_sales.csv', num_rows=1000):
    print(f"📦 Generating {num_rows} rows for Batch Pipeline...")
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['transaction_id', 'store_id', 'product_id', 'category', 'price', 'quantity', 'timestamp'])
        
        for _ in range(num_rows):
            prod = generate_product()
            writer.writerow([
                fake.uuid4(),
                random.choice(STORES),
                prod['product_id'],
                prod['category'],
                prod['price'],
                random.randint(1, 5), # Quantity
                fake.date_time_between(start_date='-1d', end_date='now').isoformat()
            ])
    print(f"✅ Saved to {filename}")

# --- MODE 2: STREAMING (Print real-time JSON) ---
def start_streaming(interval=1):
    print("⚡ Starting Real-Time Stream (Press Ctrl+C to stop)...")
    try:
        while True:
            # Simulate a sale
            sale = generate_product()
            sale['transaction_id'] = fake.uuid4()
            sale['store_id'] = random.choice(STORES)
            
            # This JSON is what you would send to Pub/Sub
            message_json = json.dumps(sale)
            print(f"🚀 Sending Event: {message_json}")
            
            time.sleep(random.uniform(0.1, interval))
    except KeyboardInterrupt:
        print("\n🛑 Stream stopped.")

if __name__ == "__main__":
    print("select mode:")
    print("1. Generate Batch CSV (for Airflow Project)")
    print("2. Start Real-Time Stream (for Pub/Sub Project)")
    choice = input("Enter 1 or 2: ")
    
    if choice == '1':
        generate_batch_csv()
    elif choice == '2':
        start_streaming()
