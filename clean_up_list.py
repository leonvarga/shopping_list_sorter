import json
import os
import argparse
import re


def append_match_to_bracket(item, match):
    old_item = item
    if match is not None:
        assert len(match.groups()) == 1
        print(match.span(0))
        item = ''.join([e for i, e in enumerate(item) if i not in list(range(match.span(0)[0], match.span(0)[1]))])
        end_bracket_pos = item.find(")")

        if end_bracket_pos > -1:
            item = item[:end_bracket_pos] + ", "+ match.group(0) + item[end_bracket_pos:]
        else:
            item += (f"({match.group(0)})")
        print(f"Adapted {old_item} to {item}")

    return item

def remove_match(item, match):
    old_item = item
    if match is not None:
        assert len(match.groups()) == 1
        print(match.span(0))
        item = ''.join([e for i, e in enumerate(item) if i not in list(range(match.span(0)[0], match.span(0)[1]))])

        print(f"Adapted {old_item} to {item}")

    return item


if __name__ == '__main__': 
    parser = argparse.ArgumentParser("Sort your shopping list by the sections of the supermarket")
    parser.add_argument("shopping_list_path", type=str, help="Line-separated item list. Amount values in parentheses will be ignored for matching.")
    opt = parser.parse_args()

    if os.path.exists(opt.shopping_list_path):
        cleaned_list = []
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

            match = re.search(r"(\([en]\))", item)
            item = remove_match(item, match)

            match = re.search(r"^[^\(]*([0-9]+[ ]*[kK]*g) ", item)
            item = append_match_to_bracket(item, match)

            match = re.search(r"^[^\(]*([0-9]+[ ]*[mM]*l) ", item)
            item = append_match_to_bracket(item, match)

            match = re.search(r"^[^\(]*([0-9]+[ ]*[TE]L) ", item)
            item = append_match_to_bracket(item, match)

            match = re.search(r"^[^\(]*([0-9]+) ", item)
            item = append_match_to_bracket(item, match)

            match = re.search(r"^[^\(]*(grün[e]*)", item)
            item = append_match_to_bracket(item, match)

            match = re.search(r"^[^\(]*(gemischt[es]*)", item)
            item = append_match_to_bracket(item, match)

            match = re.search(r"(granuliert)", item)
            item = append_match_to_bracket(item, match)

            match = re.search(r"(Bio-)", item)
            item = append_match_to_bracket(item, match)

            match = re.search(r"(unbehandelt)", item)
            item = append_match_to_bracket(item, match)

            match = re.search(r"(große) ", item)
            item = append_match_to_bracket(item, match)

            match = re.search(r"(schwarzer) ", item)
            item = append_match_to_bracket(item, match)

            match = re.search(r"(weißer) ", item)
            item = append_match_to_bracket(item, match)

            item_cleaned = []
            bracket_pos = item.find('(')
            bracket_pos = bracket_pos if bracket_pos > 0 else len(item)
            for i in range(bracket_pos):
                s = item[i]
                if s != ',':
                    item_cleaned.append(s)
            item_cleaned += item[bracket_pos:]
            item = ''.join(item_cleaned)


            while item[0] == ' ':
                item = item[1:]

                              
            cleaned_list.append(item)

        print("## Cleaned List ##\n")
        print("\n".join(cleaned_list))
        open("/tmp/list_cleaned", 'w').write("\n".join(cleaned_list))





