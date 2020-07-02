import numpy as np
import pandas as pd


def background_negative_green(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    if val == "":
        color = "white"
    elif val < -200:
        color = "#009900"
    elif -200 <= val < -150:
        color = "#00cc00"
    elif -150 <= val < -100:
        color = "#80ff80"
    elif -100 <= val < -50:
        color = "#b3ffb3"
    elif -50 <= val < 0:
        color = "#e6ffe6"
    else:
        color = "white"

    return f"background-color: {color}"


def p_value_star(data, rows, columns):
    if isinstance(data.loc[rows, columns], pd.Series):
        data_temp = data.loc[rows, columns].to_frame()
        for index in np.arange(0, data_temp.shape[0], 2):
            if abs(data_temp.iloc[index] / data_temp.iloc[index + 1])[0] > 1.96:
                data_temp.iloc[index] = str(data_temp.iloc[index][0]) + "*"
            else:
                pass
    else:
        data_temp = data.loc[rows, columns]

        for index in np.arange(0, data_temp.shape[0], 2):
            for column in np.arange(0, data_temp.shape[1]):
                if (
                    abs(
                        data_temp.iloc[index, column]
                        / data_temp.iloc[index + 1, column]
                    )
                    > 1.96
                ):
                    data_temp.iloc[index, column] = (
                        str(data_temp.iloc[index, column]) + "*"
                    )
                else:
                    pass

    data.loc[rows, columns] = data_temp

    return data
