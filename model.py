import os
import threading
import warnings
import difflib
import pandas as pd
from flask import Flask, request, jsonify
from mlxtend.frequent_patterns import apriori, association_rules

# ── silence noisy warnings ────────────────────────────────────────────────────
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ── app & globals ─────────────────────────────────────────────────────────────
app = Flask(__name__)

df = None
product_list: list[str] = []
rules = None

# ── data helpers ──────────────────────────────────────────────────────────────
def load_data(csv_path: str = "Updated_sales.csv") -> None:
    """Read CSV and populate df & product_list."""
    global df, product_list
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["Order ID", "Product"])
    df["Order ID"] = df["Order ID"].astype(str)
    product_list = df["Product"].unique().tolist()


def train_model(min_support: float = 0.01, min_confidence: float = 0.1) -> None:
    """Compute frequent itemsets & association rules, store in global `rules`."""
    global df, rules
    basket = (
        df.groupby(["Order ID", "Product"])["Product"]
        .count()
        .unstack()
        .fillna(0)
        .astype(bool)  # bool dtype keeps mlxtend happy
    )
    freq_sets = apriori(basket, min_support=min_support, use_colnames=True)
    rules = association_rules(freq_sets, metric="confidence",
                              min_threshold=min_confidence)
    rules.sort_values("lift", ascending=False, inplace=True)


def fuzzy_match(text: str, choices: list[str]) -> str | None:
    """Return closest product name or None."""
    m = difflib.get_close_matches(text, choices, n=1, cutoff=0.0)
    return m[0] if m else None


# ── background cold-start training ────────────────────────────────────────────
def cold_start() -> None:
    try:
        load_data()
        train_model(min_support=1e-5, min_confidence=1e-5)
        print(f"✅ Model trained – {len(product_list)} products.")
    except Exception as e:
        print("❌ Cold-start training failed:", e)


# ── HTTP routes ───────────────────────────────────────────────────────────────
@app.route("/health")
def health() -> tuple:
    # As soon as Flask is up we answer 200 – Coolify’s health-check passes
    return jsonify({"status": "running"}), 200


@app.route("/")
def home() -> tuple:
    return jsonify({"message": "Welcome to the Product Recommendation API!"}), 200


@app.route("/recommend")
def recommend() -> tuple:
    if rules is None:
        return jsonify({"error": "Model is still loading, try again shortly."}), 503

    product_name = request.args.get("product", "").strip()
    if not product_name:
        return jsonify({"error": "Please provide a product name"}), 400

    matched = fuzzy_match(product_name, product_list)
    if not matched:
        return jsonify({"error": "No matching product found"}), 404

    subset = rules[rules["antecedents"].apply(lambda x: matched in x)] \
              .sort_values("confidence", ascending=False)

    recs: list[str] = []
    for _, row in subset.iterrows():
        recs += [item for item in row["consequents"]
                 if item != matched and item not in recs]

    return (
        jsonify(
            {
                "input_product": product_name,
                "matched_product": matched,
                "recommendations": recs[:5],
            }
        ),
        200,
    )


@app.route("/add_order", methods=["POST"])
def add_order() -> tuple:
    global df, product_list

    data = request.get_json() or {}
    order_id = data.get("order_id")
    products = data.get("products")

    if not order_id or not products:
        return jsonify({"error": "Missing order_id or products"}), 400

    try:
        new_rows = [{"Order ID": order_id, "Product": p} for p in products]
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        product_list.extend(p for p in products if p not in product_list)
        df.to_csv("Updated_sales.csv", index=False)

        # quick incremental retrain (very low thresholds)
        train_model(min_support=1e-5, min_confidence=1e-5)

        return (
            jsonify(
                {
                    "message": "Order added and model retrained",
                    "order_id": order_id,
                    "products": products,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": f"Failed to process order: {e}"}), 500


# ── main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # kick off background trainer *before* the server starts
    threading.Thread(target=cold_start, daemon=True).start()

    port = int(os.getenv("FLASK_RUN_PORT", 80))
    app.run(host="0.0.0.0", port=port)
