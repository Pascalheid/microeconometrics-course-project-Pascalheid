# for the last second to last column I get different standard errors as this difference
# directly transfers from table 2
import numpy as np
import pandas as pd

from auxiliary.angrist_table1 import table1
from auxiliary.angrist_table2 import table2

# create data frame for table 3
cohort = np.arange(1950, 1953)
year = np.arange(1981, 1985)
statistic = ["Value", "Standard Error"]
index = pd.MultiIndex.from_product(
    [cohort, year, statistic], names=["Cohort", "Year", "Statistic"]
)
draft_eligible = np.full(3, "Draft Eligibility Effects in Current $")
not_draft_eligible = np.full(2, "")
first_level = np.concatenate((draft_eligible, not_draft_eligible))
second_level = np.array(
    [
        "FICA Earnings",
        "Adjusted FICA Earnings",
        "Total W-2 Earnings",
        "P(V|eligible) - P(V|ineligible)",
        "Service Effect in 1978 $",
    ]
)
columns = pd.MultiIndex.from_arrays(
    [first_level, second_level], names=["First Level", "Second Level"]
)
table_3 = {}
table_3["white"] = pd.DataFrame(index=index, columns=columns)
table_3["nonwhite"] = pd.DataFrame(index=index, columns=columns)

# fill table 3 with results from table 1 and 2
table_1 = table1()
table_2 = table2()
for ethnicity in ["white", "nonwhite"]:
    table_3[ethnicity].loc[
        :, (slice(None), ["FICA Earnings", "Total W-2 Earnings"])
    ] = (
        table_1[ethnicity]
        .loc[(slice(81, 84), slice(None)), (slice(None), slice(50, 52))]
        .values.reshape((24, 2), order="F")
    )

    for number in year:
        table_3[ethnicity].loc[
            (slice(None), number, slice(None)),
            (slice(None), "P(V|eligible) - P(V|ineligible)"),
        ] = (
            table_2[ethnicity]
            .loc[
                ("SIPP (84)", [1950, 1951, 1952], slice(None)),
                "P(V|eligible) - P(V|ineligible)",
            ]
            .values
        )

# fill table 3 with new values
data = pd.read_stata(r"data\cwhsc_new.dta")
data_cpi = pd.read_stata(r"data\cpi_angrist1990.dta")
data = pd.merge(data, data_cpi, on="year")

data["cpi"] = (data["cpi"] / data.loc[data["year"] == 78, "cpi"].mean()).round(3)
data["cpi2"] = data["cpi"] ** 2
data["smplsz"] = data["nj"] - data["nj0"]
data = data.loc[(data["year"] >= 81) & (data["byr"] >= 50) & (data["byr"] <= 52)]

# get variance
data["var"] = 1 / data["iweight_old"] * data["smplsz"] * data["cpi2"]
# create real earnings
data["nomearn"] = data["earnings"] * data["cpi"]
# create eligibilty
data["eligible"] = 0
data.loc[
    ((data["byr"] == 50) & (data["interval"] == 1))
    | ((data["byr"] == 51) & (data["interval"] <= 25))
    | (((data["byr"] == 52) | (data["byr"] == 53)) & (data["interval"] <= 19)),
    "eligible",
] = 1

# create ethnicity dummy
data["white"] = 1 - pd.get_dummies(data["race"], drop_first=True)

sumwt = (
    data.groupby(["white", "byr", "year", "eligible", "type"])["smplsz"]
    .sum()
    .to_frame()
    .rename(columns={"smplsz": "sumwt"})
)
data = pd.merge(
    data, sumwt, how="outer", on=["white", "byr", "year", "eligible", "type"]
)

data["var_cm"] = 1 / data["sumwt"] * data["var"]
# get weighted average
data = data.groupby(["white", "byr", "year", "eligible", "type"]).apply(
    lambda x: np.average(
        x[["var_cm", "nomearn", "earnings", "cpi"]], weights=x["smplsz"], axis=0
    )
)
data = pd.DataFrame(
    data.to_list(), columns=["var_cm", "nomearn", "earnings", "cpi"], index=data.index
)
data = data.loc[(slice(None), slice(None), slice(None), slice(None), "ADJ"), :]
data.reset_index("type", drop=True, inplace=True)

for dummy, ethnicity in enumerate(["white", "nonwhite"]):
    new_dummy = 1 - dummy
    table_3[ethnicity].loc[
        (slice(None), slice(None), "Value"), (slice(None), "Adjusted FICA Earnings")
    ] = (
        data.loc[(new_dummy, slice(None), slice(None), 1), "nomearn"].values
        - data.loc[(new_dummy, slice(None), slice(None), 0), "nomearn"].values
    )

    table_3[ethnicity].loc[
        (slice(None), slice(None), "Standard Error"),
        (slice(None), "Adjusted FICA Earnings"),
    ] = (
        (
            data.loc[(new_dummy, slice(None), slice(None), 1), "var_cm"].values
            + data.loc[(new_dummy, slice(None), slice(None), 0), "var_cm"].values
        )
        ** 0.5
    )

for dummy, ethnicity in enumerate(["white", "nonwhite"]):
    new_dummy = 1 - dummy
    for stat in statistic:
        table_3[ethnicity].loc[
            (slice(None), slice(None), stat), (slice(None), "Service Effect in 1978 $")
        ] = table_3[ethnicity].loc[
            (slice(None), slice(None), stat), (slice(None), "Adjusted FICA Earnings")
        ].values.flatten() / (
            table_3[ethnicity]
            .loc[
                (slice(None), slice(None), "Value"),
                (slice(None), "P(V|eligible) - P(V|ineligible)"),
            ]
            .values.flatten()
            * data.loc[(new_dummy, slice(None), slice(None), 0), "cpi"].values
        )

    table_3[ethnicity].loc[:, (slice(None), "P(V|eligible) - P(V|ineligible)")] = (
        table_3[ethnicity]
        .loc[:, (slice(None), "P(V|eligible) - P(V|ineligible)")]
        .astype(float)
        .round(3)
    )
    table_3[ethnicity].loc[
        (slice(None), slice(1982, 1984), slice(None)),
        (slice(None), "P(V|eligible) - P(V|ineligible)"),
    ] = ""
    table_3[ethnicity].loc[
        :, ~table_3[ethnicity].columns.isin([("", "P(V|eligible) - P(V|ineligible)")])
    ] = (
        table_3[ethnicity]
        .loc[
            :,
            ~table_3[ethnicity].columns.isin([("", "P(V|eligible) - P(V|ineligible)")]),
        ]
        .astype(float)
        .round(1)
    )
