import camelot
import pandas as pd
from datetime import datetime
import pytz
import json

lessons_key = {
    "GEO": "Geography",
    "RU": "Homeroom",
    "ANG": "English",
    "KEM": "Chemistry",
    "SLO": "Slovene",
    "MAT": "Math",
    "INF": "Informatics",
    "RAČ": "Computer Science",
    "LUM": "Art",
    "MAA": "Math AA",
    "MAI": "Math AI",
    "ŠVZ": "Physical Education",
    "ZGO": "History",
}

def extract_tables_from_pdf(pdf_path):
    tables = camelot.read_pdf(pdf_path, pages='all')
    return tables

def merge_tables(tables):
    chosen_tables = []
    if len(tables) > 1:
        for table in tables:
            if any("." in str(row[0]) for row in table.df.itertuples(index=False)):
                chosen_tables.append(table)
        
        return pd.concat([table.df for table in chosen_tables], ignore_index=True)
    elif len(tables) == 1:
        return tables[0].df
    else:
        return pd.DataFrame()

def align_classes(df: pd.DataFrame):
    current_class = None
    for row in df.iterrows():
        if row[1][0]: current_class = row[1][0]
        else: df.at[row[0], 0] = current_class
    return df

def parse_df(df: pd.DataFrame):
    parsed = {}
    for row in df.iterrows():
        if row[1][0] == "Razred":
            continue
        class_name = row[1][0]
        if class_name not in parsed:
            parsed[class_name] = []
        
        lesson = row[1][1]
        substitute = row[1][2]

        if "odpade" in substitute:
            substitute_type = "cancelled"
            substitute = "".join(substitute.split("\n")[1:]).replace("namesto", "").strip()
            substitute = {
                "prev_teacher": substitute.split(", ")[0],
                "prev_lesson": substitute.split(", ")[1]
            }
        else:
            substitute_type = "substitute"
            substitute_list = [s.strip() for s in substitute.split("\n")]
            substitute = [0, 1]
            if len(substitute_list) > 2:
                substitute[0] = " ".join(substitute_list[:substitute_list.index([s for s in substitute_list if "namesto" in s][0])])
                substitute[1] = " ".join(substitute_list[substitute_list.index([s for s in substitute_list if "namesto" in s][0]):])
            else:
                substitute[0] = substitute_list[0]
                substitute[1] = substitute_list[1]
            substitute = [s.replace("namesto", "").replace("(zaposlitev)", "").strip() for s in substitute]
            substitute = {
                "prev_teacher": substitute[1].strip().split(", ")[0],
                "prev_lesson": substitute[1].strip().split(", ")[1],
                "new_teacher": substitute[0].strip().split(", ")[0],
                "new_lesson": substitute[0].strip().split(", ")[1]
            }

        new_room = row[1][3]
        additional_info = row[1][4]

        parsed[class_name].append({
            "lesson": lesson,
            "substitute_type": substitute_type,
            "substitute": substitute,
            "new_room": new_room,
            "additional_info": additional_info
        })
    return parsed

def get_lessons(date, class_name=None):
    pdf_path = f"substitutes_{date.strftime('%Y-%m-%d')}.pdf"
    tables = extract_tables_from_pdf(pdf_path)
    merged_table = merge_tables(tables)
    merged_table = align_classes(merged_table)
    parsed_table = parse_df(merged_table)

    if not class_name:
        return parsed_table
    if class_name not in parsed_table:
        return []
    return parsed_table[class_name]

if __name__ == "__main__":
    # date = datetime.now(tz=pytz.timezone("Europe/Ljubljana"))
    date = datetime(2025, 3, 18, tzinfo=pytz.timezone("Europe/Ljubljana"))
    with open(f"lessons_{date.strftime('%Y-%m-%d')}.json", "w") as f:
        json.dump(get_lessons(date), f, indent=4, ensure_ascii=False)