"""
Generate realistic retail dataset for portfolio demonstration.
Creates 10,000+ transactions that look like real retail data.
"""
import csv
import random
from datetime import datetime, timedelta

# Realistic product catalog (Bangladesh/German retail)
PRODUCTS = [
    {"id": "SKU001", "name": "Red T-Shirt", "category": "T-Shirt", "base_price": 29.99},
    {"id": "SKU002", "name": "Blue T-Shirt", "category": "T-Shirt", "base_price": 29.99},
    {"id": "SKU003", "name": "White T-Shirt", "category": "T-Shirt", "base_price": 24.99},
    {"id": "SKU004", "name": "Black Polo", "category": "T-Shirt", "base_price": 39.99},
    {"id": "SKU005", "name": "Slim Fit Jeans", "category": "Jeans", "base_price": 79.99},
    {"id": "SKU006", "name": "Regular Jeans", "category": "Jeans", "base_price": 69.99},
    {"id": "SKU007", "name": "Ripped Jeans", "category": "Jeans", "base_price": 89.99},
    {"id": "SKU008", "name": "White Sneakers", "category": "Sneakers", "base_price": 129.99},
    {"id": "SKU009", "name": "Black Sneakers", "category": "Sneakers", "base_price": 119.99},
    {"id": "SKU010", "name": "Running Shoes", "category": "Sneakers", "base_price": 99.99},
    {"id": "SKU011", "name": "Little Black Dress", "category": "Dress", "base_price": 99.99},
    {"id": "SKU012", "name": "Summer Dress", "category": "Dress", "base_price": 79.99},
    {"id": "SKU013", "name": "Party Dress", "category": "Dress", "base_price": 149.99},
    {"id": "SKU014", "name": "Winter Jacket", "category": "Jacket", "base_price": 149.99},
    {"id": "SKU015", "name": "Leather Jacket", "category": "Jacket", "base_price": 199.99},
    {"id": "SKU016", "name": "Denim Jacket", "category": "Jacket", "base_price": 129.99},
]

STORES = [
    {"id": "Berlin_01", "city": "Berlin", "type": "flagship"},
    {"id": "Hamburg_02", "city": "Hamburg", "type": "mall"},
    {"id": "Munich_01", "city": "Munich", "type": "mall"},
    {"id": "Frankfurt_01", "city": "Frankfurt", "type": "outlet"},
    {"id": "Online_Store", "city": "Online", "type": "ecommerce"},
]

def generate_transactions(num_days=30, avg_daily_txns=350):
    """Generate realistic transaction data."""
    transactions = []
    start_date = datetime.now() - timedelta(days=num_days)
    
    for day in range(num_days):
        current_date = start_date + timedelta(days=day)
        
        # Weekend has more sales
        is_weekend = current_date.weekday() >= 5
        daily_txns = int(avg_daily_txns * (1.4 if is_weekend else 1.0))
        daily_txns += random.randint(-50, 50)  # Random variation
        
        for _ in range(daily_txns):
            product = random.choice(PRODUCTS)
            store = random.choice(STORES)
            
            # Time distribution (more sales in afternoon/evening)
            hour = random.choices(
                range(10, 22),
                weights=[1, 2, 3, 4, 5, 6, 7, 8, 9, 8, 6, 4]
            )[0]
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            txn_time = current_date.replace(hour=hour, minute=minute, second=second)
            
            # Price variations (discounts, etc.)
            price = product["base_price"] * random.uniform(0.85, 1.0)
            quantity = random.choices([1, 2, 3], weights=[70, 25, 5])[0]
            
            transactions.append({
                "transaction_id": f"TXN-{txn_time.strftime('%Y%m%d')}-{random.randint(10000, 99999)}",
                "timestamp": txn_time.isoformat(),
                "store_id": store["id"],
                "store_city": store["city"],
                "product_id": product["id"],
                "product_name": product["name"],
                "category": product["category"],
                "unit_price": round(price, 2),
                "quantity": quantity,
                "total_amount": round(price * quantity, 2),
                "payment_method": random.choice(["Credit Card", "Debit Card", "Cash", "Mobile Pay"]),
            })
    
    return transactions

def save_to_csv(transactions, filename):
    """Save transactions to CSV."""
    if not transactions:
        return
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=transactions[0].keys())
        writer.writeheader()
        writer.writerows(transactions)
    
    print(f"✅ Generated {len(transactions)} transactions")
    print(f"📁 Saved to: {filename}")

if __name__ == "__main__":
    print("🔄 Generating realistic retail dataset...")
    transactions = generate_transactions(num_days=30, avg_daily_txns=350)
    save_to_csv(transactions, "retail_transactions_30days.csv")
    
    # Print sample
    print("\n📊 Sample data:")
    for t in transactions[:3]:
        print(f"  {t['transaction_id']}: {t['product_name']} x{t['quantity']} = ${t['total_amount']}")
