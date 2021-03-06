from bs4 import BeautifulSoup
from jinja2 import Template
from pathlib import Path
from typing import Dict, List
import csv
import json
import pandas as pd
import shutil
from helpers import slugify, reset_path, custom_sort


def get_categories() -> Dict:
    #  Get all the categories
    print("==== Getting categories")
    categories = {}
    with Path("../content/jila-kaytetye-admin/categories.csv").open("r") as categories_file:
        pd_reader = pd.read_csv(categories_file)
        keep_col = ['Id', 'Name', 'Image file name']
        categories_df = pd_reader[keep_col]
        for index, entry in categories_df.iterrows():
            categories[entry["Id"]] = ({"id": entry["Id"], "name": entry["Name"], "image": entry["Image file name"]})
    return categories


def get_categories_entries() -> Dict:
    # Read all category-entry pairs as a list, also flip the col order
    print("==== Getting category entries")
    categories_entries = {}
    with Path("../content/jila-kaytetye-admin/categories_entries.csv").open("r") as categories_entries_file:
        csv_reader = csv.reader(categories_entries_file)
        next(csv_reader)  # skip the header
        for row in csv_reader:
            category_id = int(row[0])
            entry_id = int(row[1])
            if category_id in categories_entries:
                categories_entries[category_id].append(entry_id)
            else:
                categories_entries[category_id] = [entry_id]
    return categories_entries


def get_entries() -> Dict:
    # Get all the entries and add entry ids to the category list
    print("==== Getting entries")
    # * Id,
    # * Entry word,
    # Word type,
    # * Translation,
    # Description,
    # * Published?,
    # Created at,
    # Updated at,
    # * Image file name,
    # Image content type,
    # Image file size,
    # Image updated at,
    # * Audio file name,
    # Audio content type,
    # Audio file size,
    # Audio updated at,
    # Extras,
    # Display order,
    # * Sentence,
    # * Sentence translation,
    # * Scientific name,
    # Admin only notes,
    # * Call audio file name,
    # Call audio content type,
    # Call audio file size,
    # Call audio updated at,
    # Sentence audio file name,
    # Sentence audio content type,
    # Sentence audio file size,
    # Sentence audio updated at
    entries = {}
    with Path("../content/jila-kaytetye-admin/entries.csv").open("r") as entries_file:
        csv_reader = csv.DictReader(entries_file)
        for row in csv_reader:
            print(row)
            id = int(row["Id"])
            # Add row data to entry array here
            if row["Published?"] == "TRUE":
                entries[id] = {"id": id,
                               "word": row["Entry word"],
                               "translation": row["Translation"],
                               "published": row["Published?"],
                               "image_file_name": slugify(row["Image file name"]),
                               "audio_file_name": slugify((row["Audio file name"])),
                               "sentence": row["Sentence"],
                               "sentence_translation": row["Sentence translation"],
                               "scientific_name": row["Scientific name"],
                               "call_audio_file_name": slugify(row["Call audio file name"]),
                               "menu_slug": slugify(row["Entry word"]),
                               }
        return entries


def build_index_page(entries: Dict, project_output_path: Path):
    """
    Make HTML for the index page.

    :param entries:
    :param project_output_path:
    :return:
    """
    with open("../templates/index.html") as template_file:
        tm = Template(template_file.read())
        html = tm.render(entries=entries)
        with project_output_path.joinpath(f'index.html').open("w") as html_output_file:
            html_output_file.write(html)


def build_entry_pages(entries: Dict,
                      entries_output_path: Path,
                      project_output_path: Path,
                      menu: List[Dict]
                      ):
    """
    Make HTML for the entry pages.

    :param entries:
    :param entries_output_path:
    :param project_output_path:
    :param menu:
    :return:
    """
    # copy assets
    shutil.copytree("../templates/_assets",
                    project_output_path.joinpath("_assets"), dirs_exist_ok=True)
    shutil.copy("../templates/favicon.ico", project_output_path)

    with open("../templates/entry.html") as template_file:
        tm = Template(template_file.read())

    for index, entry in entries.items():
        # Pass row data here
        entry["menu"] = menu
        html = tm.render(entry)
        with entries_output_path.joinpath(f'{entry["word"]}.html').open("w") as html_output_file:
            html_output_file.write(html)


def copy_about_page(project_output_path: Path):
    shutil.copy("../templates/about.html", project_output_path)


def build_menu_highlight_css(entries: Dict, project_output_path: Path):
    with open("../templates/menu_highlight.css") as template_file:
        tm = Template(template_file.read())
        html = tm.render(entries=entries)
        with project_output_path.joinpath("_assets/menu_highlight.css").open("w") as css_output_file:
            css_output_file.write(html)


def build_menu_with_categories(categories: Dict, categories_entries: Dict, entries: Dict) -> List[Dict]:
    menu = []
    for index, category in categories.items():
        if category["id"] in categories_entries:
            sub_menu = {"name": category["name"], "entries": []}
            for entry_id in categories_entries[category["id"]]:
                # Entries might not contain this id if the entry is not published
                if entry_id in entries:
                    entry = entries[entry_id]
                    sub_menu["entries"].append({
                        "id": entry_id,
                        "text": entry["word"],
                        "slug": f'{entry["word"]}.html',
                        "image_file_name": entry["image_file_name"],
                        "menu_slug": entry["menu_slug"]
                    })
            custom_sort(sub_menu["entries"], "text")
            menu.append(sub_menu)
    return menu


def build_flat_menu(entries: Dict) -> List[Dict]:
    menu = []
    for key, entry in entries.items():
        print(entry)
        menu.append({
            "id": entry["id"],
            "text": entry["word"],
            "slug": f'{entry["word"]}.html',
            "image_file_name": entry["image_file_name"],
            "menu_slug": entry["menu_slug"]
        })
    custom_sort(menu, "text")
    return menu


def main():
    project_output_path = Path("../output")

    categories_output_path = Path("../output/categories")
    reset_path(categories_output_path)

    entries_output_path = Path("../output/entries")
    reset_path(entries_output_path)

    categories = get_categories()
    categories_entries = get_categories_entries()
    entries = get_entries()
    print(entries)

    menu = build_flat_menu(entries)

    copy_about_page(project_output_path=project_output_path)

    build_menu_highlight_css(entries=entries, project_output_path=project_output_path)

    build_index_page(entries=entries, project_output_path=project_output_path )

    build_entry_pages(entries=entries,
                      entries_output_path=entries_output_path,
                      project_output_path=project_output_path,
                      menu=menu
                      )


if __name__ == "__main__":
    main()
