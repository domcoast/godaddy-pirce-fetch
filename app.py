from flask import Flask, request, jsonify
import httpx
from bs4 import BeautifulSoup
from urllib.parse import unquote

app = Flask(__name__)

DEFAULT_SESSION_COOKIE = "nr2vFwWGCLQAiCPKzqd5Y82naDFN8jSGlwK8Pn4nx7,rFgYSe7ilVMNp7tjEBFBwiTEhUG3kZbtJCTOrEUUn10q78YUBPP82UuXEIeOnxpGxcH,1nx4IzEX8Ld04Ef2l"

@app.route("/getPrice", methods=["GET"])
def get_price():
    domain = request.args.get("domain")
    session_cookie = request.args.get("session_id", DEFAULT_SESSION_COOKIE)
    if not domain:
        return jsonify({"error": "Missing 'domain' query parameter"}), 400

    session_cookie = unquote(session_cookie)

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": f"ExpiredDomainssessid={session_cookie}"
    }

    url = f"https://member.expireddomains.net/domain/{domain}"

    try:
        with httpx.Client(headers=headers, timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            price_cell = soup.find("td", string="Price")
            if price_cell:
                price_value = price_cell.find_next_sibling("td")
                if price_value:
                    price = price_value.get_text(strip=True)
                    return jsonify({"domain": domain, "price": price})
                else:
                    return jsonify({"error": "Price value cell not found"}), 404
            else:
                return jsonify({"error": "'Price' label not found"}), 404

    except httpx.RequestError as e:
        return jsonify({"error": f"Request error: {str(e)}"}), 500
    except httpx.HTTPStatusError as e:
        return jsonify({"error": f"HTTP error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
