# for the CWHS data set I am missing the ingredients for cohort 1950
# for the SIPP I get different standard errors which is most likely due to the
# implementation of the WLS. I get the same results as in stata, though.
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

data_cwhsa = pd.read_stata(r"data\cwhsa.dta")

data_cwhsa = data_cwhsa.loc[
    (data_cwhsa["year"] == 70) & (data_cwhsa["byr"] >= 51),
    ["race", "byr", "interval", "vnu1"],
]

# create eligibility dummy
data_cwhsa["eligible"] = 0
data_cwhsa.loc[
    (
        (data_cwhsa["byr"] >= 44)
        & (data_cwhsa["byr"] <= 50)
        & (data_cwhsa["interval"] <= 39)
    )
    | ((data_cwhsa["byr"] == 51) & (data_cwhsa["interval"] <= 25))
    | (
        ((data_cwhsa["byr"] == 52) | (data_cwhsa["byr"] == 53))
        & (data_cwhsa["interval"] <= 19)
    ),
    "eligible",
] = 1

# create ethnicity dummy
data_cwhsa["white"] = 1 - pd.get_dummies(data_cwhsa["race"], drop_first=True)

data_cwhsa = data_cwhsa.groupby(["byr", "white", "eligible"])["vnu1"].sum()


data_dmdc = pd.read_stata(r"data\dmdcdat.dta")

# create eligibility dummy
data_dmdc["eligible"] = 0
data_dmdc.loc[
    (
        (data_dmdc["byr"] >= 44)
        & (data_dmdc["byr"] <= 50)
        & (data_dmdc["interval"] <= 39)
    )
    | ((data_dmdc["byr"] == 51) & (data_dmdc["interval"] <= 25))
    | (
        ((data_dmdc["byr"] == 52) | (data_dmdc["byr"] == 53))
        & (data_dmdc["interval"] <= 19)
    ),
    "eligible",
] = 1

# create ethnicity dummy
data_dmdc["white"] = 1 - pd.get_dummies(data_dmdc["race"], drop_first=True)

data_dmdc = data_dmdc.groupby(["byr", "white", "eligible"])["nsrvd"].sum()

# merge the two data sets
data_dmdc_cwsh = pd.merge(data_cwhsa, data_dmdc, on=["byr", "white", "eligible"])

nsrvd_all = (
    data_dmdc_cwsh.groupby(["white", "byr"])["nsrvd"]
    .sum()
    .to_frame()
    .rename(columns={"nsrvd": "nsrvd_all"})
)
vnu1_all = (
    data_dmdc_cwsh.groupby(["white", "byr"])["vnu1"]
    .sum()
    .to_frame()
    .rename(columns={"vnu1": "vnu1_all"})
)
data_dmdc_cwsh = data_dmdc_cwsh.join(pd.merge(nsrvd_all, vnu1_all, on=["byr", "white"]))

data_dmdc_cwsh["p_vet"] = data_dmdc_cwsh["nsrvd"] / (100 * data_dmdc_cwsh["vnu1"])
data_dmdc_cwsh["p_vet_all"] = data_dmdc_cwsh["nsrvd_all"] / (
    100 * data_dmdc_cwsh["vnu1_all"]
)
data_dmdc_cwsh["se_vet"] = (
    data_dmdc_cwsh["p_vet"] * (1 - data_dmdc_cwsh["p_vet"]) / data_dmdc_cwsh["vnu1"]
) ** 0.5
data_dmdc_cwsh["se_vet_all"] = (
    data_dmdc_cwsh["p_vet_all"]
    * (1 - data_dmdc_cwsh["p_vet_all"])
    / data_dmdc_cwsh["vnu1_all"]
) ** 0.5

table_2 = {}
for dummy, ethnicity in enumerate(["white", "nonwhite"]):
    new_dummy = 1 - dummy

    # Initialize a temporary table
    dataset = ["SIPP (84)", "DMDC/CWHS"]
    cohort = np.arange(1951, 1954)
    statistic = ["Value", "Standard Error"]
    index_end = pd.MultiIndex.from_product(
        [dataset, cohort, statistic], names=["Data Set", "Cohort", "Statistic"]
    )
    index_beginning = pd.MultiIndex.from_product(
        [[dataset[0]], [1950], statistic], names=["Data Set", "Cohort", "Statistic"]
    )
    index = index_beginning.append(index_end)
    table_2_temp = pd.DataFrame(
        index=index,
        columns=[
            "Sample",
            "P(Veteran)",
            "P(Veteran|eligible)",
            "P(Veteran|ineligible)",
            "P(V|eligible) - P(V|ineligible)",
        ],
    )

    # fill the table with values created through the DMDC/CWHS data set
    table_2_temp.loc[
        ("DMDC/CWHS", slice(None), "Value"),
        ["Sample", "P(Veteran)", "P(Veteran|eligible)"],
    ] = data_dmdc_cwsh.loc[
        (slice(None), new_dummy, 1), ["vnu1_all", "p_vet_all", "p_vet"]
    ].values
    table_2_temp.loc[
        ("DMDC/CWHS", slice(None), "Standard Error"),
        ["P(Veteran)", "P(Veteran|eligible)"],
    ] = data_dmdc_cwsh.loc[(slice(None), new_dummy, 1), ["se_vet_all", "se_vet"]].values
    table_2_temp.loc[
        ("DMDC/CWHS", slice(None), "Value"), "P(Veteran|ineligible)"
    ] = data_dmdc_cwsh.loc[(slice(None), new_dummy, 0), ["p_vet"]].values
    table_2_temp.loc[
        ("DMDC/CWHS", slice(None), "Standard Error"), "P(Veteran|ineligible)"
    ] = data_dmdc_cwsh.loc[(slice(None), new_dummy, 0), ["se_vet"]].values
    table_2_temp.loc[
        ("DMDC/CWHS", slice(None), "Value"), "P(V|eligible) - P(V|ineligible)"
    ] = (
        table_2_temp.loc[("DMDC/CWHS", slice(None), "Value"), "P(Veteran|eligible)"]
        - table_2_temp.loc[("DMDC/CWHS", slice(None), "Value"), "P(Veteran|ineligible)"]
    )
    table_2_temp.loc[
        ("DMDC/CWHS", slice(None), "Standard Error"), "P(V|eligible) - P(V|ineligible)"
    ] = (
        (
            table_2_temp.loc[
                ("DMDC/CWHS", slice(None), "Standard Error"), "P(Veteran|eligible)"
            ]
            ** 2
            + table_2_temp.loc[
                ("DMDC/CWHS", slice(None), "Standard Error"), "P(Veteran|ineligible)"
            ]
            ** 2
        )
        ** 0.5
    )

    # create table 2
    table_2[ethnicity] = table_2_temp

# read the SIPP data set
data_sipp = pd.read_stata(r"data\sipp2.dta")

for dummy, ethnicity in enumerate(["white", "nonwhite"]):
    for year in np.arange(1950, 1954):
        # fill table 2 with values from the SIPP data set
        data_temp = data_sipp.loc[
            (data_sipp["u_brthyr"] >= year - 1)
            & (data_sipp["u_brthyr"] <= year + 1)
            & (data_sipp["nrace"] == dummy)
        ]
        # run WLS regression
        wls = smf.wls(
            formula="nvstat ~ 1", data=data_temp, weights=data_temp["fnlwgt_5"]
        ).fit()
        coefficient = wls.params
        standard_error = wls.bse
        # extract sample size and fill table 2
        table_2[ethnicity].loc[("SIPP (84)", year, "Value"), "Sample"] = data_sipp.loc[
            (data_sipp["u_brthyr"] == year) & (data_sipp["nrace"] == dummy)
        ].shape[0]
        table_2[ethnicity].loc[
            ("SIPP (84)", year, slice(None)), "P(Veteran)"
        ] = coefficient.append(standard_error).values

        data_temp = data_sipp.loc[
            (data_sipp["u_brthyr"] >= year - 1)
            & (data_sipp["u_brthyr"] <= year + 1)
            & (data_sipp["nrace"] == dummy)
            & (data_sipp["rsncode"] == 1)
        ]
        wls = smf.wls(
            formula="nvstat ~ 1", data=data_temp, weights=data_temp["fnlwgt_5"]
        ).fit()
        coefficient = wls.params
        standard_error = wls.bse
        table_2[ethnicity].loc[
            ("SIPP (84)", year, slice(None)), "P(Veteran|eligible)"
        ] = coefficient.append(standard_error).values

        data_temp = data_sipp.loc[
            (data_sipp["u_brthyr"] >= year - 1)
            & (data_sipp["u_brthyr"] <= year + 1)
            & (data_sipp["nrace"] == dummy)
            & (data_sipp["rsncode"] != 1)
        ]
        wls = smf.wls(
            formula="nvstat ~ 1", data=data_temp, weights=data_temp["fnlwgt_5"]
        ).fit()
        coefficient = wls.params
        standard_error = wls.bse
        table_2[ethnicity].loc[
            ("SIPP (84)", year, slice(None)), "P(Veteran|ineligible)"
        ] = coefficient.append(standard_error).values

        # create last column for the SIPP data set in table 2
        table_2[ethnicity].loc[
            ("SIPP (84)", slice(None), "Value"), "P(V|eligible) - P(V|ineligible)"
        ] = (
            table_2[ethnicity].loc[
                ("SIPP (84)", slice(None), "Value"), "P(Veteran|eligible)"
            ]
            - table_2[ethnicity].loc[
                ("SIPP (84)", slice(None), "Value"), "P(Veteran|ineligible)"
            ]
        )
        table_2[ethnicity].loc[
            ("SIPP (84)", slice(None), "Standard Error"),
            "P(V|eligible) - P(V|ineligible)",
        ] = (
            (
                table_2[ethnicity].loc[
                    ("SIPP (84)", slice(None), "Standard Error"), "P(Veteran|eligible)"
                ]
                ** 2
                + table_2[ethnicity].loc[
                    ("SIPP (84)", slice(None), "Standard Error"),
                    "P(Veteran|ineligible)",
                ]
                ** 2
            )
            ** 0.5
        )

for ethnicity in ["white", "nonwhite"]:
    table_2[ethnicity] = table_2[ethnicity].astype(float).round(4)
    table_2[ethnicity] = table_2[ethnicity].fillna("")
