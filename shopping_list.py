import json
import os
import argparse

DB_PATH = 'shopping_list_db.json'

def save_db(db):
    json.dump(db, open(DB_PATH, 'w'))


def standarize_name(item: str):
    item_simplified = item.lower()
    parenthesis_pos = item.find(chr(40))
    if parenthesis_pos > 0:
        item_simplified = item_simplified[:parenthesis_pos]
    item_simplified = item_simplified.replace(' ', '')

    return item_simplified

def find_item_section(item_simplified: str, db):
    for item in db['items']:
        if item['name'] == item_simplified:
            return item['section']
    return None

def ask_user_decision(question, options= ['y', 'n'], allow_number=False):
    decision = None
    is_valid = False

    while not is_valid:
        decision = input(question + "\n")
        if decision is not None:
            if decision in options:
                is_valid = True
                continue
            if allow_number and decision.isnumeric():
                is_valid = True
                continue
        else:
            is_valid = False
    return decision

def ask_user_for_section(db):
    def _get_section_str(section_id, section):
        return f"[{section_id}]: {section}"

    nl = '\n'

    question = f"These are the available sections: \n {nl.join([_get_section_str(section_id, section) for section_id, section in enumerate(db['sections'])])}\n"
    question += "In which section does this item belong? (Please provide the id of the section or add a new with 'a')\n" 

    selection = ''
    
    if len(db['sections']) == 0:
        return 'a'

    while not (selection.isnumeric() or selection == 'a'):
        selection = input(question)
    return selection

def print_sections(db):
    def _get_section_str(section_id, section):
        return f"[{section_id}]: {section}"

    nl = '\n'

    question = f"These are the available sections: \n {nl.join([_get_section_str(section_id, section) for section_id, section in enumerate(db['sections'])])}\n"
    question += "In which section does this item belong? (Please provide the id of the section or add a new with 'a')\n" 
    print(question)



def ask_user_for_section_order(db):
    def _get_section_str(section_id, section):
        return f"[{section_id}]: {section}"

    nl = '\n'

    question = f"These are the available sections: \n {nl.join([_get_section_str(section_id, section) for section_id, section in enumerate(db['sections'])])}\n"
    question += f"The old order was: {' '.join([str(i) for i in db['section_order_old']])}\n"
    question += "Which is the section order? (Please provide a space-separated list of the section ids)\n" 

    order = ''

    while order == '' or len(order.split(' ')) < 0:
        order = input(question)

    return [int(o) for o in order.split(' ') if len(o) > 0]


def handle_item(item, db):
    item_simplified = standarize_name(item)
    item_section = None
    print(f"'{item}'")
    print(f"# {item} not found in item db")
    print_sections(db)
    ui_add_new = ask_user_decision("? Add a new item? (#/n/e/s)", ['s', 'n', 'e'], allow_number=True)

    if ui_add_new == 'e':
        item_simplified = standarize_name(input("Please provide the desired item name:"))
        item_section = find_item_section(item_simplified, db)
    elif ui_add_new == 's':
        ui_section_name = input("? Provide a section name: ")
        db['sections'].append(ui_section_name)
        item_section = len(db['sections']) - 1 

        opt.override_section_order = True
        if len(db['section_order']) > 0:
            db['section_order_old'] = db['section_order']
            db['section_order'] = []
    elif ui_add_new.isnumeric():
        item_section = ui_add_new
    else:
        print(f"! Ignore {item} for sorted shopping list")
        return False

    if item_section is not None:
        db['items'].append(
            {
                'name': item_simplified,
                'section': int(item_section)
            })
        save_db(db)

    return item_section


if __name__ == '__main__': 
    parser = argparse.ArgumentParser("Sort your shopping list by the sections of the supermarket")
    parser.add_argument("shopping_list_path", type=str, help="Line-separated item list. Amount values in parentheses will be ignored for matching.")
    parser.add_argument("--override_section_order", action='store_true', required=False, default=False)
    opt = parser.parse_args()

    if os.path.exists(DB_PATH):
        db = json.load(open(DB_PATH, 'r'))
        print("# Loaded database.")
    else:
        db = {
            'sections': [],
            'items': [],
            'section_order': []
        }
    save_db(db)

    if os.path.exists(opt.shopping_list_path):
        print(f"# Use shopping list: {opt.shopping_list_path}")
        item_section_map = []

        shopping_list_file = open(opt.shopping_list_path, "r").readlines()

        for item in shopping_list_file:
            item = item.replace('\n', '')

            if len(item.replace(" ", "")) == 0:
                print("# Ignore empty row")
                continue

            if item.startswith('#') or item.startswith('!'):
                print(f"# Ignore comment: {item}")
                continue


            item_simplified = standarize_name(item)
            item_section = find_item_section(item_simplified, db)

            while item_section is None:
                item_section = handle_item(item, db)
                if item_section == False:
                    item_section = None
                    break

            item_section_map.append({'item': item, 'section': item_section})

        section_order = [i for i in range(len(db['sections']))]
        if len(db['section_order']) == 0 or opt.override_section_order:
            db['section_order'] = ask_user_for_section_order(db)
            save_db(db)
        section_order = db['section_order']
        
        print("\n\n\t### Sorted Shopping List ###")
        for cur_section in section_order:
            items_in_section = []
            for item_mapping in item_section_map:
                if item_mapping['section'] is not None and int(item_mapping['section']) == int(cur_section):
                    items_in_section.append(item_mapping['item'])
            if len(items_in_section) > 0:
                print(f"## Section: {db['sections'][cur_section]}")
                items_in_section = sorted(items_in_section)
                for item in items_in_section:
                    print(item)
                print()

        missing_section_items = []
        for item_mapping in item_section_map:
            if not (item_mapping['section'] in section_order or item_mapping['section'] is None):
                print(item_mapping)
                missing_section_items.append(item_mapping['item'])

        if len(missing_section_items) > 0:
            print("## Missing section")
            for m in missing_section_items:
                print(m)

        if len([i for i in item_section_map if i['section'] is None]) > 0:
            print("## Unsorted")
            for item_mapping in item_section_map:
                if item_mapping['section'] is None:
                    print(item_mapping['item'])
    else:
        print("# No shopping list")

    print("# Done.")
    save_db(db)

