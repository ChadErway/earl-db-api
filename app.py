from flask import Flask, request, jsonify
import mysql.connector
import os

print("📦 Imports loaded")

app = Flask(__name__)
print("🚀 Flask app created")

db_config = {
    'host': os.environ.get('DB_HOST'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASS'),
    'database': os.environ.get('DB_NAME')
}
print("🔧 DB config loaded")


@app.route("/")
def home():
    return "EARL DB API is running."


@app.route("/lookup/part", methods=["GET"])
def lookup_part():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400

    try:
        print("🔍 Lookup via /lookup/part:", query)

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT sku, value AS name
            FROM catalog_product_entity
            JOIN catalog_product_entity_varchar 
              ON catalog_product_entity.entity_id = catalog_product_entity_varchar.entity_id
            WHERE sku LIKE %s OR value LIKE %s
            LIMIT 1
        """, (f"%{query}%", f"%{query}%"))

        result = cursor.fetchone()
        print("📦 Lookup result:", result)

        cursor.close()
        conn.close()

        if not result:
            return jsonify({"reply": f"Sorry, I couldn’t find anything matching '{query}'."})

        sku = result['sku']
        reply = f"That matches RF Engine part #{sku}. Here’s the link: https://rfecomm.com/catalogsearch/result/?q={sku}"
        return jsonify({"reply": reply})

    except Exception as e:
        print("❌ Error in /lookup/part:", str(e))
        return jsonify({"error": "Database lookup failed"}), 500


@app.route("/webhook", methods=["POST"])
def tawk_webhook():
    print("📣 /webhook route triggered")

    data = request.json
    print("📩 Incoming webhook payload:", data)

    message = data.get("message", "").strip()
    print("📨 Extracted message:", message)

    if not message:
        return jsonify({"reply": "No message received."})

    try:
        print("🔍 Running DB query for:", message)

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT sku, value AS name
            FROM catalog_product_entity
            JOIN catalog_product_entity_varchar 
              ON catalog_product_entity.entity_id = catalog_product_entity_varchar.entity_id
            WHERE sku LIKE %s OR value LIKE %s
            LIMIT 1
        """, (f"%{message}%", f"%{message}%"))

        result = cursor.fetchone()
        print("📦 Webhook query result:", result)

        cursor.close()
        conn.close()

        if not result:
            return jsonify({"reply": "Hmm… I’ll admit, that one’s got me stumped. Let’s get a human involved."})

        sku = result['sku']
        reply = f"That matches RF Engine part #{sku}. Here’s the link: https://rfecomm.com/catalogsearch/result/?q={sku}"
        return jsonify({"reply": reply})

    except Exception as e:
        print("❌ Error in /webhook:", str(e))
        return jsonify({"reply": "Sorry, something went wrong while checking that part. Let’s get a human involved."})


if __name__ == "__main__":
    print("🧠 Launching EARL…")
    app.run(debug=True, host="0.0.0.0", port=10000)
