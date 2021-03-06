# AUTOGENERATED! DO NOT EDIT! File to edit: 01_fontsampler.ipynb (unless otherwise specified).

__all__ = ['create_font_annotations']

# Cell
import glob
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import random
import re
from typing import Union

# Cell
from sklearn.preprocessing import MultiLabelBinarizer
import pandas as pd

# Cell
def create_font_annotations(data_path: str = "data/webfonts.json", api_key: str = None,
    save_path = "data/google-fonts-annotation.csv") -> pd.DataFrame:
    """Get Google Fonts metadata either from the API using `api_key` or from
       a local file at `data_path` and save the data as csv in `save_path`.
       Also returns the data frame."""

    assert api_key is not None or data_path is not None

    if data_path is not None:
        # Use JSON already downloaded
        df = pd.read_json(data_path)
    else:
        # Download json data once
        url = f"https://www.googleapis.com/webfonts/v1/webfonts?key={api_key}"
        df = pd.read_json(url, orient='')

    # flatten the JSON hierarchy (easier to handle this way)
    df = pd.json_normalize(df['items'])

    # select only the columns we need
    cols = ['family', 'variants', 'subsets', 'category']
    df = df[cols]
    # df.head(5)

    # Remove any space from family string so that it matchs with file name convention.
    df.family = [name.replace(' ', '') for name in df.family]

    mlb = MultiLabelBinarizer()

    # one-hot encoding + prefix
    df = df.join(pd.DataFrame(mlb.fit_transform(df.pop('variants')),
                            columns=[x for x in mlb.classes_],
                            index=df.index))
    df = df.join(pd.DataFrame(mlb.fit_transform(df.pop('subsets')),
                            columns=['subsets_' + x for x in mlb.classes_],
                            index=df.index))
    df = df.join(pd.get_dummies(df['category'], prefix="category")).drop(['category'], axis=1)

    col_names = {
        "100": "thin",
        "100italic": "thinitalic",
        "200": "extralight",
        "200italic": "extralightitalic",
        "300": "light",
        "300italic": "lightitalic",
        "400": "regular",
        "regular": "regular",
        "400italic": "italic",
        "italic": "italic",
        "500": "medium",
        "500italic": "mediumitalic",
        "600": "semibold",
        "600italic": "semibolditalic",
        "700": "bold",
        "700italic": "bolditalic",
        "800": "extrabold",
        "800italic": "extrabolditalic",
        "900": "black",
        "900italic": "blackitalic"
    }
    col_names = {k:f'variants_{v}' for k, v in col_names.items()}

    df = df.rename(col_names, axis='columns')

    # Export csv
    if not save_path.endswith(".csv"):
        save_path += ".csv"
    df.to_csv(save_path, index=False)

    return df
