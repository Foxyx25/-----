
def process_order(order):
    total = sum(order["items"])
    discount = order["discount"]
    if discount["type"] == "percent":
        total -= total * (discount["value"]/100)
    elif discount["type"] == "fixed":
        total -= discount["value"]

    if total < 2000:
        total += 300

    return round(total, 2)

def test_process_order():
    order1 = {
        "items": [700, 900],
        "discount": {"type": "percent", "value": 10}
    }
    assert process_order(order1) == 1740.0  # 1600 -10% + 300

    order2 = {
        "items": [1000, 1200],
        "discount": {"type": "fixed", "value": 500}
    }
    assert process_order(order2) == 2000.0  # 2200 - 500 + доставка

    order3 = {
        "items": [300, 300],
        "discount": {"type": "percent", "value": 50}
    }
    assert process_order(order3) == 600.0  # 600 - 50% = 300 + доставка 300

    print("✅ Все тесты пройдены!")


# 🚀 Запуск тестов
test_process_order()