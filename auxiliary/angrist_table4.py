# my results ar elike in the stata code but the table in Angrist is a tiny bit different
import itertools

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

data = pd.read_stata(r"data\cwhsc_new.dta")
data = data.loc[data["year"] >= 81].reset_index(drop=True)

# create cohort and year dummies
data = data.join(pd.get_dummies(data["year"], prefix="year"))
data = data.join(pd.get_dummies(data["byr"], prefix="byr"))

for birthyear in [50, 51, 52, 53]:
    data["ps_r" + str(birthyear)] = data["ps_r"] * (data["byr"] == birthyear)

data["alpha1"] = 0
data["alpha2"] = 0

# get the coefficients from the first stage for the two models
for race in [1, 2]:
    for source in ["TAXAB", "ADJ", "TOTAL"]:
        data_temp = data.loc[(data["race"] == race) & (data["type"] == source)]
        model1 = [
            "byr_51",
            "byr_52",
            "byr_53",
            "year_82",
            "year_83",
            "year_84",
            "ps_r",
        ]
        model2 = model1[:-1]
        model2.extend(["ps_r50", "ps_r51", "ps_r52", "ps_r53"])

        wls_model1 = smf.wls(
            formula="earnings ~ " + " + ".join(model1[:]),
            data=data_temp,
            weights=data_temp["iweight_old"],
        ).fit()
        data.loc[
            (data["race"] == race) & (data["type"] == source), "alpha1"
        ] = wls_model1.params["ps_r"]

        wls_model2 = smf.wls(
            formula="earnings ~ " + " + ".join(model2[:]),
            data=data_temp,
            weights=data_temp["iweight_old"],
        ).fit()
        for cohort in [50, 51, 52, 53]:
            data.loc[
                (data["race"] == race)
                & (data["type"] == source)
                & (data["byr"] == cohort),
                "alpha2",
            ] = wls_model2.params["ps_r" + str(cohort)]

# generate sample size column
cohort_ethnicity = list(itertools.product(np.arange(50, 54), np.arange(1, 3)))
sample = [351, 70, 16744, 5251, 17662, 5480, 17694, 5294]
for (cohort, ethnicity), size in zip(cohort_ethnicity, sample):
    data.loc[(data["byr"] == cohort) & (data["race"] == ethnicity), "smpl"] = size

# generate ............................. for the two models
data["term1"] = (
    data["alpha1"] ** 2 * data["ps_r"] * (1 - data["ps_r"]) * (1 / data["smpl"])
)
data["term2"] = (
    data["alpha2"] ** 2 * data["ps_r"] * (1 - data["ps_r"]) * (1 / data["smpl"])
)

data["intercept"] = 1
data["wts"] = 1 / data["iweight_old"] ** 0.5

# sort the dataframe
for number, name in enumerate(["TAXAB", "ADJ", "TOTAL"]):
    data.loc[data["type"] == name, "tctr"] = number + 1

data.sort_values(by=["byr", "tctr", "race", "interval", "year"], inplace=True)
data.set_index(["byr", "tctr", "race", "interval", "year"], inplace=True, drop=True)

# get transformed data for second stage regression
X1_columns = [
    "intercept",
    "byr_51",
    "byr_52",
    "byr_53",
    "year_82",
    "year_83",
    "year_84",
    "ps_r",
]
X2_columns = [
    "intercept",
    "byr_51",
    "byr_52",
    "byr_53",
    "year_82",
    "year_83",
    "year_84",
    "ps_r50",
    "ps_r51",
    "ps_r52",
    "ps_r53",
]
Y = data["earnings"].values.reshape((int(5304 / 4), 4, 1))
X1 = data[X1_columns].values.reshape((int(5304 / 4), 4, 8))
X2 = data[X2_columns].values.reshape((int(5304 / 4), 4, 11))
covmtrx = data[["ern81", "ern82", "ern83", "ern84"]].values.reshape(
    (int(5304 / 4), 4, 4)
)
term1 = data["term1"].values.reshape((int(5304 / 4), 4, 1))
term2 = data["term2"].values.reshape((int(5304 / 4), 4, 1))
wtvec = data["wts"].values.reshape((int(5304 / 4), 4, 1))

covmtrx1 = wtvec * covmtrx * np.transpose(wtvec, (0, 2, 1)) + term1
covmtrx2 = wtvec * covmtrx * np.transpose(wtvec, (0, 2, 1)) + term2

final1 = np.linalg.cholesky(np.linalg.inv(covmtrx1))
final2 = np.linalg.cholesky(np.linalg.inv(covmtrx2))

Y1 = np.matmul(np.transpose(final1, (0, 2, 1)), Y).reshape((5304, 1))
X1 = np.matmul(np.transpose(final1, (0, 2, 1)), X1).reshape((5304, 8))
data2 = pd.DataFrame(
    data=np.concatenate((Y1, X1), axis=1),
    index=data.index,
    columns=["earnings"] + X1_columns,
)

Y2 = np.matmul(np.transpose(final2, (0, 2, 1)), Y).reshape((5304, 1))
X2 = np.matmul(np.transpose(final2, (0, 2, 1)), X2).reshape((5304, 11))
data1 = pd.DataFrame(
    data=np.concatenate((Y2, X2), axis=1),
    index=data.index,
    columns=["earnings"] + X2_columns,
)

# Create empty table 4
table_4 = {}
statistic = ["Value", "Standard Error"]
index_beginning = pd.MultiIndex.from_product(
    [["Model 1"], np.arange(1950, 1954), statistic],
    names=["Model", "Cohort", "Statistic"],
)
index_beginning = index_beginning.append(
    pd.MultiIndex.from_tuples([("Model 1", "Chi Squared", "")])
)
index_end = pd.MultiIndex.from_product([["Model 2"], ["1950-53"], statistic])
index_end = index_end.append(
    pd.MultiIndex.from_tuples([("Model 2", "Chi Squared", "")])
)
index = index_beginning.append(index_end)
columns = ["FICA Taxable Earnings", "Adjusted FICA Earnings", "Total W-2 Compensation"]

# for loop to run regressions for the two models and fill table 4
for dummy, ethnicity in enumerate(["white", "nonwhite"]):
    table_4[ethnicity] = pd.DataFrame(index=index, columns=columns)
    new_dummy = dummy + 1

    for number, dataset in enumerate(columns):
        model1_result = smf.ols(
            formula="earnings ~ 0 +" + " + ".join(data1.columns[1:]),
            data=data1.loc[
                (slice(None), number + 1, new_dummy, slice(None), slice(None)), :
            ],
        ).fit()
        table_4[ethnicity].loc[
            ("Model 1", slice(None), "Value"), dataset
        ] = model1_result.params[-4:].values
        table_4[ethnicity].loc[("Model 1", slice(None), "Standard Error"), dataset] = (
            model1_result.bse[-4:].values / model1_result.mse_resid ** 0.5
        )
        table_4[ethnicity].loc[
            ("Model 1", "Chi Squared", slice(None)), dataset
        ] = model1_result.ssr

        model2_result = smf.ols(
            formula="earnings ~ 0 +" + " + ".join(data2.columns[1:]),
            data=data2.loc[
                (slice(None), number + 1, new_dummy, slice(None), slice(None)), :
            ],
        ).fit()
        table_4[ethnicity].loc[
            ("Model 2", slice(None), "Value"), dataset
        ] = model2_result.params[-1]
        table_4[ethnicity].loc[("Model 2", slice(None), "Standard Error"), dataset] = (
            model2_result.bse[-1] / model2_result.mse_resid ** 0.5
        )
        table_4[ethnicity].loc[
            ("Model 2", "Chi Squared", slice(None)), dataset
        ] = model2_result.ssr

    table_4[ethnicity] = table_4[ethnicity].astype(float).round(1)
