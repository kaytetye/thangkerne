import csv
import json
from pathlib import Path
import shutil
from typing import List
from bs4 import BeautifulSoup
import pandas as pd


def get_categories():
    #  Get all the categories
    print("==== Getting categories")
    categories = {}
    with Path("../content/jila-kaytetye-admin/categories.csv").open("r") as categories_file:
        pd_reader = pd.read_csv(categories_file)
        keep_col = ['Id', 'Name', 'Image file name']
        categories_df = pd_reader[keep_col]
        for index, entry in categories_df.iterrows():
            categories[entry["Id"]] = ({"id": entry["Id"], "name": entry["Name"], "image": entry["Image file name"], "entries": []})
    return categories


def get_categories_entries():
    # Read all category-entry pairs as a list, also flip the col order
    print("==== Getting category entries")
    categories_entries = {}
    entries_categories = {}
    with Path("../content/jila-kaytetye-admin/categories_entries.csv").open("r") as categories_entries_file:
        csv_reader = csv.reader(categories_entries_file)
        next(csv_reader) # skip the header
        for row in csv_reader:
            category_id = int(row[0])
            entry_id = int(row[1])
            if category_id in categories_entries:
                categories_entries[category_id].append(entry_id)
            else:
                categories_entries[category_id] = [entry_id]
            if entry_id in entries_categories:
                entries_categories[entry_id].append(category_id)
            else:
                entries_categories[entry_id] = [category_id]
    return categories_entries, entries_categories


def get_entries():
    # Get all the entries and add entry ids to the category list
    print("==== Getting entries")
    # Id,Entry word,Word type,Translation,Description,Published?,Created at,Updated at,Image file name,Image content type,Image file size,Image updated at,Audio file name,Audio content type,Audio file size,Audio updated at,Extras,Display order,Sentence,Sentence translation,Scientific name,Admin only notes,Call audio file name,Call audio content type,Call audio file size,Call audio updated at,Sentence audio file name,Sentence audio content type,Sentence audio file size,Sentence audio updated at
    with Path("../content/jila-kaytetye-admin/entries.csv").open("r") as entries_file:
        csv_reader = pd.read_csv(entries_file)
        keep_col = ['Id', 'Entry word', 'Translation']
        entries = csv_reader[keep_col]
    return entries


def main():

    categories_output_path = Path("../output/categories")
    if categories_output_path.is_dir():
        shutil.rmtree(categories_output_path)
    categories_output_path.mkdir(parents=True, exist_ok=True)

    categories = get_categories()
    categories_entries, entries_categories = get_categories_entries()
    entries = get_entries()

    for cat_id in categories:
        print(categories[cat_id]["name"])
        cat_name = categories[cat_id]["name"].lower()
        # build a category page with BeautifulSoup
        category_menu_soup = BeautifulSoup(f'<p>{categories[cat_id]["name"]} menu</p><ul></ul>', "html.parser")
        for entry_id, cat_ids in entries_categories.items():
            if cat_id in cat_ids:
                # get the entry details
                entry = entries.loc[(entries["Id"] == entry_id)]
                word = entry["Entry word"].item()
                li_tag = category_menu_soup.new_tag("li")
                li_a_tag = category_menu_soup.new_tag("a", href=f"{word}.html")
                li_a_tag.string = word
                li_tag.append(li_a_tag)
                category_menu_soup.ul.append(li_tag)

        with categories_output_path.joinpath(f"{cat_name}.html").open("w") as html_output_file:
            html_output_file.write(category_menu_soup.prettify())


if __name__ == "__main__":
    main()
