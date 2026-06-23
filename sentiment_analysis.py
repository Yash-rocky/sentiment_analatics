import streamlit as st
import pandas as pd
import pymysql
from textblob import TextBlob

# --- Page Configuration ---
st.set_page_config(
    page_title="Advanced NLP Sentiment Analytics", 
    page_icon="🧠", 
    layout="wide"
)

# Dynamic Theme-Aware Styling for KPI Blocks
st.markdown("""
<style>
    [data-testid="stMetric"] {
        background-color: var(--background-color); 
        padding: 15px;
        border-radius: 8px;
        border: 1px solid var(--secondary-background-color); 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
        color: var(--text-color) !important; 
    }
</style>
""", unsafe_allow_html=True)

# Helper function to establish connection
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="sales_db",
        autocommit=True
    )

# --- Database Fetching Function ---
def fetch_sentiment_data():
    try:
        conn = get_db_connection()
        query = "SELECT id, review_text, sentiment_label, sentiment_score FROM customer_reviews ORDER BY id DESC"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Database Connection Error: {e}")
        return pd.DataFrame()

# --- Title Header ---
st.title("🧠 Advanced Text Analytics Engine")
st.subheader("Interactive Natural Language Processing & Database Hub")
st.markdown("---")

# --- Feature 1: Live Text Tester Sandbox ---
st.markdown("### 🧪 Real-time Sentiment Sandbox")
with st.expander("Expand to analyze and insert custom text live", expanded=False):
    user_input = st.text_area("Type custom customer feedback here:", placeholder="e.g., I absolutely love the speed, but the UI is confusing...")
    
    if st.button("Analyze & Compute Sentiment"):
        if user_input.strip():
            # NLP Processing
            blob = TextBlob(user_input)
            score = round(blob.sentiment.polarity, 2)
            
            if score > 0.1:
                label = "Positive"
                st.success(f"👍 **Polished Result:** Positive Sentiment (Score: {score})")
            elif score < -0.1:
                label = "Negative"
                st.error(f"👎 **Polished Result:** Negative Sentiment (Score: {score})")
            else:
                label = "Neutral"
                st.info(f"😐 **Polished Result:** Neutral Sentiment (Score: {score})")
            
            # Save directly to XAMPP database
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                insert_query = "INSERT INTO customer_reviews (review_text, sentiment_label, sentiment_score) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (user_input, label, score))
                conn.close()
                st.toast("Record successfully written to XAMPP database!", icon="💾")
            except Exception as db_err:
                st.error(f"Failed to commit text to database: {db_err}")
        else:
            st.warning("Please type something before analyzing.")

st.markdown("---")

# Load Existing Data from XAMPP
df = fetch_sentiment_data()

if not df.empty:
    # --- Feature 2: Smart Data Engineering (Word Length Metric) ---
    df['Word Count'] = df['review_text'].apply(lambda x: len(str(x).split()))

    # --- Sidebar Filter Control Panel ---
    st.sidebar.header("🕹️ Analytics Filters")
    st.sidebar.markdown("Slice database metrics dynamically:")
    
    # Class Filter
    selected_labels = st.sidebar.multiselect(
        "Filter by Sentiment Class:",
        options=df['sentiment_label'].unique(),
        default=df['sentiment_label'].unique()
    )
    
    # Range Slider for explicit Polarity Scores (-1.0 to 1.0)
    score_range = st.sidebar.slider(
        "Filter by Exact Polarity Score:",
        min_value=-1.0, max_value=1.0,
        value=(-1.0, 1.0), step=0.1
    )
    
    # Apply Sidebar Constraints
    df_filtered = df[
        (df['sentiment_label'].isin(selected_labels)) & 
        (df['sentiment_score'] >= score_range[0]) & 
        (df['sentiment_score'] <= score_range[1])
    ]

    # --- Top KPIs Ribbon ---
    total_feedback = len(df_filtered)
    counts = df_filtered['sentiment_label'].value_counts()
    
    pos_count = counts.get('Positive', 0)
    neg_count = counts.get('Negative', 0)
    avg_score = df_filtered['sentiment_score'].mean() if total_feedback > 0 else 0.0
    avg_words = df_filtered['Word Count'].mean() if total_feedback > 0 else 0.0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Filtered Total", total_feedback)
    m2.metric("Positive Volume", pos_count)
    m3.metric("Negative Volume", neg_count)
    m4.metric("Avg Review Length", f"{int(avg_words)} words")

    st.markdown("### 📊 Distribution Framework & Metrics")

    # --- Main Visuals Row ---
    left_graphics, right_ledger = st.columns([2, 3])

    with left_graphics:
        st.markdown("#### **Sentiment Class Frequencies**")
        st.bar_chart(counts, color="#2980b9", height=280)
        
        # New Feature 3: Scatter Trend (Word Count vs Sentiment Score)
        st.markdown("#### **Review Length vs Sentiment Intensity**")
        st.scatter_chart(df_filtered, x='Word Count', y='sentiment_score', color='#e74c3c', height=280)

    with right_ledger:
        st.markdown("#### **Active Database Records**")
        # Format columns cleanly for full visibility
        st.dataframe(
            df_filtered[['id', 'review_text', 'sentiment_label', 'sentiment_score', 'Word Count']], 
            use_container_width=True, 
            height=600
        )
        
        # Quick CSV Download Option
        csv_data = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Filtered Sentiment Data (CSV)",
            data=csv_data,
            file_name="sentiment_analytics_export.csv",
            mime="text/csv"
        )
else:
    st.warning("⚠️ No data discovered. Please ensure XAMPP is active and run your ingestion file.")