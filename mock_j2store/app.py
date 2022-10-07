import math
from pathlib import Path
import pickle
import uuid

from flask import Flask, render_template, url_for, abort, request, redirect


MARKET_ITEMS = []
CART = []


def init_market_items():
    with Path("market-items.pkl").open("rb") as file:
        MARKET_ITEMS = pickle.load(file)

    # Rewrite src URL
    items = []
    for item in MARKET_ITEMS:
        src = item["src"]
        src = src.replace("%20", "_").replace("1_f", "f").replace("Customs_", "customs_")
        item["src"] = f"static{src}"
        items.append(item)
    MARKET_ITEMS = items

    return MARKET_ITEMS


MARKET_ITEMS = init_market_items()

app = Flask(__name__)


@app.template_filter("vatu_price")
def vatu_price(price: int) -> str:
    return "VT{:,}".format(price)


# @app.before_first_request
# def setup_app():
#     global MARKET_ITEMS
#     MARKET_ITEMS = init_market_items()


@app.before_request
def set_user():
    pass


@app.get("/customs/customs-sale")
def start():
    return render_template("sale-open.html")
    # return render_template("sale-closed.html")


@app.get("/customs-online-sale")
def get_market():
    ITEMS_PER_PAGE = 24
    start = int(request.args.get("start"))
    if start > len(MARKET_ITEMS):
        return render_template("market-no-items.html")
    end = min(len(MARKET_ITEMS), start + ITEMS_PER_PAGE)
    items = MARKET_ITEMS[start:end]
    current_page = start // ITEMS_PER_PAGE
    total_pages = math.ceil(len(MARKET_ITEMS) / ITEMS_PER_PAGE)
    pagination = {
        "current_page": current_page,
        "total_pages": total_pages,
        "start": None,
        "prev": None,
        "next": None,
        "end": None,
    }
    for num, i in enumerate(range(total_pages)):
        if i == current_page:
            pagination[i + 1] = None
        else:
            pagination[i + 1] = url_for("get_market", start=i * ITEMS_PER_PAGE)

    return render_template(
        # "customs-online-sale.html",
        "market.html",
        items=items,
        pagination=pagination,
    )


@app.get("/customs-online-sale/<string:item>")
def get_market_item(item: str):
    id = int(item.split("-", 1)[0])
    try:
        market_item = list(filter(lambda i: i["id"] == id, MARKET_ITEMS))[0]
    except IndexError:
        abort(404)
    return render_template(
        "market_item.html",
        item=market_item,
    )


@app.get("/component/j2store/carts")
def get_cart():
    return render_template("cart.html", items=CART)


@app.get("/component/j2store/carts/clearCart")
def get_clear_cart():
    CART = []
    return redirect(url_for("get_cart"))


@app.post("/component/j2store/carts/addItem")
def post_add_item():
    quantity = int(request.form.get("product_qty"))
    product_id = int(request.form.get("product_id"))
    option = request.form.get("option")
    view = request.form.get("view")
    task = request.form.get("task")
    ajax = request.form.get("ajax")
    # csrf token - not mocked
    _return = request.form.get("return")

    # get market item for addtional details - fail if missing
    market_item = next(filter(lambda i: i["id"] == product_id, MARKET_ITEMS))

    item = next(filter(lambda i: i.product_id == product_id, CART), None)
    if item is None:
        cartitem_id = uuid.uuid4().hex  # XXX use uuid to create random cart id
        unit_price = int(market_item["unit_price"])
        CART.append(
            dict(
                cartitem_id=cartitem_id,
                product_id=product_id,
                name=market_item["name"],
                unit_price=unit_price,
                quantity=quantity,
                subtotal=unit_price * quantity,
            )
        )
    else:
        item["quantity"] += quantity
        item["subtotal"] = item["unit_price"] * item["quantity"]
    return "Item Added", 200


@app.get("/component/j2store/carts/remove")
def get_remove_item():
    id = request.args.get("cartitem_id")
    CART = list(filter(lambda i: i.id != id, CART))
    return redirect(url_for("get_cart"))


@app.get("/component/j2store/checkout")
def get_checkout():
    return render_template("checkout.html")


@app.post("/component/j2store/carts")
def post_cart():
    """Handle payment."""
    view = request.form.get("view")
    assert view == "checkout", "unexpected view value"
    task = request.form.get("task")
    if task == "billing_address":
        return render_template("raw_cart_task_billing_address.html")
    elif task == "billing_address_validate":
        return ""
    elif task == "shipping_payment_method":
        return render_template("raw_cart_task_shipping_payment_validate.html")
    elif task == "shipping_payment_method_validate":
        return ""
    elif task == "confirm":
        return render_template("raw_cart_task_confirm.html")
    elif task == "confirmPayment":
        return ""
    else:
        abort(400)
