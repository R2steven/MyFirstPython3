# Ryan Stevens
# restevens52@gmail.com
#
# shipping is a function meant to determine the cheapest shipping option for
# customers trying to send packages with sal's shipping.


weight = 14

weight_key = [2, 6, 10]  # the weight conditions
# ground shipping prices for weight(lbs)=w : w<=2, 2<w<=6, 6<w<=10, w>10, flat rate
g_shipping = [1.5, 3.0, 4.0, 4.75, 20.0]
# premium flat rate
pg_shipping = 125.0
# Drone shipping prices for weight(lbs)=w : w<=2, 2<w<=6, 6<w<=10, w>10, flat rate
d_shipping = [4.5, 9.0, 12.0, 14.25, 0.0]


def weight_index(wgt):
    w_index = 0
    for w_value in weight_key:
        if wgt > w_value:
            w_index += 1
    return w_index


def ship_price(w_index, s_method):
    if isinstance(s_method, list):
        s_price = s_method[w_index] * weight + s_method[4]
    elif not isinstance(s_method, list):
        s_price = 125.0
    else:
        s_price = None
    return s_price


def cheapest(wgt):
    prices = [ship_price(weight_index(weight), g_shipping),
              ship_price(weight, pg_shipping),
              ship_price(weight_index(weight), d_shipping)]
    minimum = min(prices)
    return minimum, prices.index(minimum)


print(cheapest(weight))
