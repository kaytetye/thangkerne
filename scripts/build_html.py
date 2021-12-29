from bs4 import BeautifulSoup
from jinja2 import Template
from pathlib import Path
from typing import Dict, List
import csv
import json
import pandas as pd
import shutil
from helpers import slugify, reset_path


def get_categories():
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


def get_categories_entries():
    # Read all category-entry pairs as a list, also flip the col order
    print("==== Getting category entries")
    categories_entries = {}
    entries_categories = {}
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
            if entry_id in entries_categories:
                entries_categories[entry_id].append(category_id)
            else:
                entries_categories[entry_id] = [category_id]
    return categories_entries, entries_categories


def get_entries():
    # Get all the entries and add entry ids to the category list
    print("==== Getting entries")
    entries = {}
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
    with Path("../content/jila-kaytetye-admin/entries.csv").open("r") as entries_file:
        csv_reader = csv.DictReader(entries_file)
        for row in csv_reader:
            id = int(row["Id"])
            # Add row data to entry array here
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
                           }
    return entries


def build_category_pages(categories: Dict,
                         entries_categories: Dict,
                         entries: Dict,
                         categories_output_path: Path,
                         project_output_path: Path
                         ):
    """
    Make HTML for the category pages.

    :param categories:
    :param entries_categories:
    :param entries:
    :param categories_output_path:
    :param project_output_path:
    :return:
    """
    for cat_id in categories:
        print(categories[cat_id]["name"])
        cat_name = categories[cat_id]["name"].lower()
        # Build a category page with BeautifulSoup
        category_soup = BeautifulSoup(f'<p>{categories[cat_id]["name"]} menu</p><ul></ul>', "html.parser")
        for entry_id, cat_ids in entries_categories.items():
            if cat_id in cat_ids:
                # Build a link with the entry word
                entry = entries[entry_id]
                word = entry["word"]
                li_tag = category_soup.new_tag("li")
                li_a_tag = category_soup.new_tag("a", attrs={"href": f"../entries/{word}.html", "class": "entry-link"})
                li_a_tag.string = word
                li_tag.append(li_a_tag)
                category_soup.ul.append(li_tag)

        with categories_output_path.joinpath(f"{cat_name}.html").open("w") as html_output_file:
            html_output_file.write(category_soup.prettify())


def build_entry_pages(entries: Dict,
                      entries_output_path: Path,
                      project_output_path: Path
                      ):
    """
    Make HTML for the entry pages.

    :param entries:
    :param entries_output_path:
    :param project_output_path:
    :return:
    """
    # copy assets
    shutil.copytree("../templates/_assets",
                    project_output_path.joinpath("_assets"), dirs_exist_ok=True)

    with open("../templates/entry.html") as template_file:
        tm = Template(template_file.read())

    for index, entry in entries.items():
        # Pass row data here
        print(entry)
        html = tm.render(entry)
        with entries_output_path.joinpath(f'{entry["word"]}.html').open("w") as html_output_file:
            html_output_file.write(html)


def main():
    project_output_path = Path("../output")

    categories_output_path = Path("../output/categories")
    reset_path(categories_output_path)

    entries_output_path = Path("../output/entries")
    reset_path(entries_output_path)

    categories = get_categories()
    categories_entries, entries_categories = get_categories_entries()
    entries = get_entries()

    print(entries)

    build_category_pages(categories=categories,
                         entries_categories=entries_categories,
                         entries=entries,
                         categories_output_path=categories_output_path,
                         project_output_path=project_output_path
                         )

    build_entry_pages(entries=entries,
                      entries_output_path=entries_output_path,
                      project_output_path=project_output_path
                      )


if __name__ == "__main__":
    main()
