import numpy as np
import pandas as pd


def table1():
    data = pd.read_stata(r"data\cwhsa.dta")
    data["type"] = "TAXAB"

    temp_data = pd.read_stata(r"data\cwhsb.dta")
    data = data.append(temp_data)

    data = data.loc[(data["year"] > 65) & (data["byr"] >= 50)]

    # create eligibility dummy
    data["eligible"] = 0
    data.loc[
        ((data["byr"] >= 44) & (data["byr"] <= 50) & (data["interval"] <= 39))
        | ((data["byr"] == 51) & (data["interval"] <= 25))
        | (((data["byr"] == 52) | (data["byr"] == 53)) & (data["interval"] <= 19)),
        "eligible",
    ] = 1

    # create ethnicity dummy
    data = pd.concat([data, pd.get_dummies(data["race"], prefix="race")], axis=1)
    data.rename(columns={"race_1": "white", "race_2": "nonwhite"}, inplace=True)

    # mean and weights for nonzeros
    data["earn_nz"] = data["vmn1"] / (1 - data["vfin1"])
    data["wt_nz"] = data["vnu1"] * (1 - data["vfin1"])

    data.loc[data["type"] == "TAXAB", "type"] = "FICA"
    # create variance
    var = data["vsd1"] ** 2
    # variance of nonzero cells
    data["var_nz"] = var * (data["vnu1"] / data["wt_nz"])

    # adjust index for groupby
    wtmult = pd.DataFrame()
    wtmult["wtmult"] = (
        1 / data.groupby(["white", "byr", "year", "eligible", "type"])["wt_nz"].sum()
    )
    data = pd.merge(
        data, wtmult, how="outer", on=["white", "byr", "year", "eligible", "type"]
    )

    data["var_cm"] = data["wtmult"] * data["var_nz"]

    # get groupby weighted means
    data_temp = data.fillna(0)

    # drop groups where the weight sums to zero
    sum_group_weights = (
        data_temp.groupby(["white", "byr", "year", "eligible", "type"])["wt_nz"]
        .sum()
        .to_frame()
    )
    nonzero_weights_index = sum_group_weights.loc[sum_group_weights["wt_nz"] != 0].index
    data_temp.set_index(["white", "byr", "year", "eligible", "type"], inplace=True)
    data_temp = data_temp.loc[nonzero_weights_index]
    data_temp = data_temp.groupby(["white", "byr", "year", "eligible", "type"]).apply(
        lambda x: np.average(x[["var_cm", "earn_nz"]], weights=x["wt_nz"], axis=0)
    )
    data_temp = pd.DataFrame(
        data_temp.to_list(), columns=["var_cm", "earn_nz"], index=data_temp.index
    )

    index_eligible = (slice(None), slice(None), slice(None), 1, slice(None))
    index_non_eligible = (slice(None), slice(None), slice(None), 0, slice(None))
    treatment_effect = data_temp.loc[index_eligible, "earn_nz"].reset_index(
        "eligible", drop=True
    ) - data_temp.loc[index_non_eligible, "earn_nz"].reset_index("eligible", drop=True)

    standard_errors = (
        data_temp.loc[index_eligible, "var_cm"].reset_index("eligible", drop=True)
        + data_temp.loc[index_non_eligible, "var_cm"].reset_index("eligible", drop=True)
    ) ** 0.5

    table_1 = {}
    for dummy, ethnicity in enumerate(["white", "nonwhite"]):
        new_dummy = 1 - dummy
        # extract treatment effect and their standard errors
        treatment_effect_temp = treatment_effect.loc[new_dummy, :, :, :].reset_index(
            "white", drop=True
        )
        standard_errors_temp = standard_errors.loc[new_dummy, :, :, :].reset_index(
            "white", drop=True
        )

        # get dataframes into the right shape for table 1
        treatment_effect_temp = treatment_effect_temp.unstack(
            level=["type", "byr"]
        ).sort_index(level="type", axis=1)
        treatment_effect_temp["Statistic"] = "Average"
        treatment_effect_temp.set_index(
            "Statistic", drop=True, append=True, inplace=True
        )

        standard_errors_temp = standard_errors_temp.unstack(
            level=["type", "byr"]
        ).sort_index(level="type", axis=1)
        standard_errors_temp["Statistic"] = "Standard Error"
        standard_errors_temp.set_index(
            "Statistic", drop=True, append=True, inplace=True
        )

        # Create table 1
        year = np.arange(66, 85)
        statistic = ["Average", "Standard Error"]
        index = pd.MultiIndex.from_product(
            [year, statistic], names=["year", "Statistic"]
        )
        table_1_temp = pd.DataFrame(index=index, columns=treatment_effect_temp.columns)
        table_1_temp.loc[(slice(None), "Average"), :] = treatment_effect_temp
        table_1_temp.loc[(slice(None), "Standard Error"), :] = standard_errors_temp
        table_1_temp = table_1_temp.astype(float).round(2)
        table_1_temp.fillna("", inplace=True)

        table_1[ethnicity] = table_1_temp

    return table_1
