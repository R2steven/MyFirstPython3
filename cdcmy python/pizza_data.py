# Ryan Stevens
# restevens52@gmail.com
#
# use python to organize some of len's pizza sales data

toppings = ["pepperoni", "pineapple", "cheese", "sausage", "olives", "anchovies", "mushrooms"]

prices = [2, 6, 1, 3, 2, 7, 2]
num_two_dollar_slices = prices.count(2)
print(num_two_dollar_slices)
num_pizzas = len(toppings)
print("We sell " + str(num_pizzas) + " different kinds of pizza!")
i = 0
pizza_and_prices = []
for i in range(0, len(toppings)):
    pizza_and_prices.append([prices[i], toppings[i]])
    i += 1
print(pizza_and_prices)
pizza_and_prices.sort(key=lambda row: (row[0], row[1]), reverse=True)
cheapest_pizza = pizza_and_prices[0]
priciest_pizza = pizza_and_prices[-1]
pizza_and_prices.pop(-1)
pizza_and_prices.append([2.5, "peppers"])
pizza_and_prices.sort(key=lambda row: (row[0], row[1]), reverse=True)
three_cheapest = pizza_and_prices[:3]
print(three_cheapest)
