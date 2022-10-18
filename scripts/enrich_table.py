#! python3 enrich_table.py

import pandas as pd
import math
from pathlib import Path
from typing import List


def searching_all_files(directory: Path):
    file_list = []  # A list for storing files existing in directories

    for x in directory.iterdir():
        if x.is_file():
            file_list.append(x)
        # else:
        #    file_list.append(searching_all_files(directory/x))
    return file_list


table_df = pd.read_json(Path(Path(__file__).parent, "nshm_science_reports_metadata_table.json"), orient='table')

folder_path = Path('/home/chrisbc/Downloads/finals')
found_reports = searching_all_files(folder_path)
print(table_df)

report_numbers = table_df['Report Number'].tolist()
report_names = []


def normalise_report_number(repnum: str) -> str:
    return repnum.replace(' ', '').replace('/', '-')


def match_report_number(report_names: List[Path], report_number: str):
    try:
        if math.isnan(float(report_number)):
            return None
    except (ValueError):
        pass
    for repname in report_names:
        if repname.name.startswith(normalise_report_number(report_number)):
            return repname.name
    return None


for report_num in report_numbers:
    report_names.append(match_report_number(found_reports, report_num))

# print( report_names )

df2 = pd.DataFrame(report_names, columns=['filename'])

# print(df2)

table_df = table_df.merge(df2, left_index=True, right_index=True)

# print(table_df)
# print(table_df['filename'])


table_df.to_json('nshm_science_reports_metadata_table_new.json', orient='table', indent=2)

# with open("nshm_science_reports_metadata_table_new.json", 'w') as f:
#     f.write(json.dumps(jsondata, indent=2))
