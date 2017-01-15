import speechhelper
from speechhelper import listen
from speechhelper import say

from google.cloud import language

menu = {
"pizza": {"size":["small", "medium", "large"], "type":["veg", "cheese", "pepperoni"]},
"garlic bread":{"size":["small", "large"]},
"drink":{"type":["coke", "fanta"]}
}

sample_order = {
"pizza":{"size":"small", "type":"veg", "number":5},
"garlic_bread":{"size":"small", "number":3}
}


#returns
def missing_item_info(order):
    for order_item in order:
        properties = menu[order_item]
        print "Properties of item: ", properties
        for prop in properties:
            if prop not in order[order_item]:
                print "Missing prop found: ", prop
                print "Property missing in order item: ", order_item
                return order_item, prop
        if (not("number" in order[order_item])):
            return order_item, "number"
    return "comp", "comp"

def brain(text):
    print 'Calling google APIs for NLP now.....'
    language_client = language.Client()
    document = language_client.document_from_text(text)
    entities = document.analyze_entities()
    annotations = document.annotate_text()
    return entities, annotations.tokens

def confirm_order(order):
    say("Repeating your order:")
    for item in order:
        say(str(order[item]["number"]))
        for prop in order[item]:
            if prop != "number":
                say("%s" % (order[item][prop]))
        say(item + "s")

def fill_item_details(order, item_name, tokens):
    print "Menu ", menu
    for token in tokens:
        if token.part_of_speech == "NUM" or token.part_of_speech == "PUNCT":
            order[item_name]["number"]=token.text_content
        else:
            for prop in menu[item_name].keys():
                values = menu[item_name][prop]
                print "Fill item details ", prop, values
                if(token.text_content in values):
                    order[item_name][prop] = token.text_content

def take_empty_order(order):
    say("What would you like to order?")
    text = listen()
    items, tokens = brain(text)
    for item in items:
        item_name = item.name.lower()
        print item_name
        if item_name[-1] =='s':
            item_name = item_name[:-1]
        if item_name in menu:
            order[item_name]={}
            fill_item_details(order, item_name, tokens)
        else:
            say("We don't serve %s" % (item.name))
    print "===== Order so far ====", order


def take_order(order, item , prop):
    if prop != "number":
        allowed_values = menu[item][prop]
        temp_string = ""
        for value in allowed_values:
            temp_string = temp_string + value + ", "
        say("What %s of %s. We serve %s" % (prop, item, temp_string))
    else:
        say("How many %ss?" % (item))
    text = listen()
    items, tokens = brain(text)
    fill_item_details(order, item, tokens)
    print "===== Order so far ====", order

def is_order_empty(order):
    if order == {}:
        return True
    else:
        return False

def waiter(order):
    while True:
        if is_order_empty(order):
            print "No order yet"
            take_empty_order(order)

        else:
            print "Checking for missing items"
            item, prop = missing_item_info(order)
            print "Missing Item ", item, prop
            if item != "comp":
                take_order(order, item, prop)
            else:
                print "Item complete"
                confirm_order(order)
                return


def main():
    speechhelper.initialize()
    order = {}
    waiter(order)


if __name__ == "__main__":
    main()
