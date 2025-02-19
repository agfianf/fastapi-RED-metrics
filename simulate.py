import random
from uuid import uuid4

from locust import HttpUser, between, task


class APIUser(HttpUser):
    """Simulates user behavior interacting with the API endpoints."""

    # Wait between 1 to 5 seconds between tasks
    wait_time = between(1, 5)

    def on_start(self):
        """Initialize user session data."""
        # Store some test product IDs for reuse
        self.test_products = [
            "15ca8c18-43d4-4da3-ad14-2dc127365b04",  # Normal case
            "05ca8c18-43d4-4da3-ad14-2dc127365b04",  # Not found case
            "55ca8c18-43d4-4da3-ad14-2dc127365b04",  # Timeout case
        ]

    @task(5)  # Higher weight for common read operations
    def list_products(self):
        """Simulate users browsing product listings."""
        page = random.randint(1, 15)
        limit = random.choice([10, 20, 50, 100])
        self.client.get(f"/api/v1/products?page={page}&limit={limit}")

    @task(3)
    def get_product_details(self):
        """Simulate users viewing individual product details."""
        product_id = random.choice(self.test_products)
        self.client.get(f"/api/v1/products/{product_id}")

    @task(1)  # Lower weight for write operations
    def create_product(self):
        """Simulate users creating new products."""
        payload = {
            "name": f"Test Product {random.randint(1, 1000)}",
            "description": "Automated test product",
            "price": random.uniform(10.0, 2000.0),
            "category": random.choice(["electronics", "books", "clothing"]),
        }
        self.client.post("/api/v1/products", json=payload)

    @task(1)
    def update_product(self):
        """Simulate users updating existing products."""
        product_id = random.choice(self.test_products)
        payload = {
            "name": f"Updated Product {random.randint(1, 1000)}",
            "description": "Updated test product",
            "price": random.uniform(10.0, 2000.0),
            "category": random.choice(["electronics", "books", "clothing"]),
        }
        self.client.put(f"/api/v1/products/{product_id}", json=payload)

    @task(2)
    def process_product(self):
        """Simulate heavy processing operations on products."""
        product_id = random.choice(self.test_products)
        self.client.post(f"/api/v1/products/{product_id}/process")

    @task(3)
    def ai_predict(self):
        """Simulate AI prediction requests."""
        texts = [
            "Analyze this customer feedback",
            "Process this long document",
            "Classify this text sample",
            "Summarize this article",
        ]
        payload = {
            "text": random.choice(texts),
            "model": "gpt-3.5-turbo",
            "parameters": {"temperature": 0.7},
        }
        # Randomly decide whether to simulate errors (20% chance)
        simulate_error = random.random() < 0.2
        self.client.post(
            f"/api/v1/ai/predict?simulate_error={simulate_error}",
            json=payload,
        )

    @task(2)
    def get_ai_prediction(self):
        """Simulate retrieving AI prediction results."""
        prediction_id = str(uuid4())
        # Randomly decide whether to simulate errors (10% chance)
        simulate_error = random.random() < 0.1
        self.client.get(
            f"/api/v1/ai/predict/{prediction_id}?simulate_error={simulate_error}",
        )


#
