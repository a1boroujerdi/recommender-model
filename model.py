import pandas as pd
from flask import Flask, request, jsonify
import difflib

from mlxtend.frequent_patterns import apriori, association_rules

app = Flask(__name__)

df = None
product_list = []
rules = None

def load_data(csv_path='Updated_sales.csv'):
    global df, product_list
    df = pd.read_csv(csv_path)

    df = df.dropna(subset=['Order ID', 'Product'])
    df['Order ID'] = df['Order ID'].astype(str)

    product_list = df['Product'].unique().tolist()

def train_model(min_support=0.01, min_confidence=0.1):

    global df, rules

    basket = df.groupby(['Order ID','Product'])['Product'].count().unstack().fillna(0)

    basket = basket.applymap(lambda x: 1 if x > 0 else 0)



    frequent_itemsets = apriori(basket, min_support=min_support, use_colnames=True)

    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)

    rules.sort_values("lift", ascending=False, inplace=True)

def fuzzy_match(user_input, product_list):
    matches = difflib.get_close_matches(user_input, product_list, n=1, cutoff=0.0)
    return matches[0] if matches else None



@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Product Recommendation API!"})


@app.route('/recommend', methods=['GET'])
def recommend():

    product_name = request.args.get('product', '').strip()
    if not product_name:
        return jsonify({'error': 'Please provide a product name'}), 400

    if rules is None or df is None:
        return jsonify({'error': 'Model has not been trained yet'}), 400


    matched_product = fuzzy_match(product_name, product_list)
    if not matched_product:
        return jsonify({'error': 'No matching product found'}), 404

    subset = rules[rules['antecedents'].apply(lambda x: matched_product in x)]

    subset = subset.sort_values('confidence', ascending=False)


    recommended_items = []
    for _, row in subset.iterrows():

        for item in list(row['consequents']):
            if item != matched_product and item not in recommended_items:
                recommended_items.append(item)


    top_recommendations = recommended_items[:5]
    return jsonify({
        'input_product': product_name,
        'matched_product': matched_product,
        'recommendations': top_recommendations
    })
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/add_order', methods=['POST'])
def add_order():
    global df, product_list
    data = request.get_json()
    order_id = data.get('order_id')
    products = data.get('products')

    if not order_id or not products:
        return jsonify({"error": "Missing order_id or products"}), 400

    try:

        new_rows = []
        for prod in products:
            new_rows.append({
                'Order ID': order_id,
                'Product': prod
            })
        new_df = pd.DataFrame(new_rows)


        df = pd.concat([df, new_df], ignore_index=True)


        for p in products:
            if p not in product_list:
                product_list.append(p)


        df.to_csv('Updated_sales.csv', index=False)

        train_model(min_support=0.00001, min_confidence=0.00001)

        return jsonify({
            "message": "Order added and model retrained successfully",
            "order_id": order_id,
            "products": products
        })
    except Exception as e:
        return jsonify({"error": f"Failed to process order: {str(e)}"}), 500

if __name__ == '__main__':
    load_data('Updated_sales.csv')
    train_model(min_support=0.00001, min_confidence=0.00001)

    print("Model loaded and trained.")
    print("Available products:", product_list)
    app.run(host='0.0.0.0', port=80) 
