import pymysql
from textblob import TextBlob

# Connect to XAMPP MySQL
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="sales_db"
)
cursor = conn.cursor()

# Sample dataset of customer reviews
sample_reviews = [
    "This software is absolutely fantastic! It works perfectly.",
    "Decent performance, but the user interface feels a bit dated.",
    "Horrible app. It crashes constantly and loses all my data.",
    "Customer service was incredibly helpful and fast!",
    "It is okay, but it lacks some advanced configurations.",
    "Very bad experience. Extremely slow and completely unusable."
]

insert_query = """
INSERT INTO customer_reviews (review_text, sentiment_label, sentiment_score) 
VALUES (%s, %s, %s)
"""

print("Analyzing sentiments and inserting data...")

for review in sample_reviews:
    # TextBlob calculates polarity score from -1.0 (very negative) to +1.0 (very positive)
    analysis = TextBlob(review)
    score = round(analysis.sentiment.polarity, 2)
    
    # Classify the label based on the score threshold
    if score > 0.1:
        label = "Positive"
    elif score < -0.1:
        label = "Negative"
    else:
        label = "Neutral"
        
    # Execute insertion
    cursor.execute(insert_query, (review, label, score))

conn.commit()
print(f"Successfully processed and pushed {len(sample_reviews)} reviews to customer_reviews table!")

cursor.close()
conn.close()