import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

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

data_cpi = pd.read_stata(r"data\cpi_angrist1990.dta")
data = pd.merge(data, data_cpi, on="year")

data = data.loc[data["type"] == "TAXAB"]

# create earnings variable and weights for weighted average
data["earnings"] = data["vmn1"] / (1 - data["vfin1"])
data["weights"] = data["vnu1"] * (1 - data["vfin1"])

# create earnings in 1978 terms
data["cpi"] = (data["cpi"] / data.loc[data["year"] == 78, "cpi"].mean()).round(3)
data["real_earnings"] = data["earnings"] / data["cpi"]

# adjust earnings like in paper
for cohort, addition in [(50, 3000), (51, 2000), (52, 1000)]:
    data.loc[data["byr"] == cohort, "real_earnings"] = (
        data.loc[data["byr"] == cohort, "real_earnings"] + addition
    )

# get groupby weighted means
table = data.fillna(0)

# drop groups where the weight sums to zero
sum_group_weights = (
    table.groupby(["race", "byr", "year", "eligible"])["weights"].sum().to_frame()
)
nonzero_weights_index = sum_group_weights.loc[sum_group_weights["weights"] != 0].index
table.set_index(["race", "byr", "year", "eligible"], inplace=True)
table = table.loc[nonzero_weights_index]
data_temp = table.groupby(["race", "byr", "year", "eligible"]).apply(
    lambda x: np.average(x[["real_earnings"]], weights=x["weights"], axis=0)
)
data_temp = pd.DataFrame(
    data_temp.to_list(), columns=["real_earnings"], index=data_temp.index
)

# create dataframe for figure 2
difference = pd.DataFrame(index=data_temp.index, columns=["difference"])
difference = difference.loc[(slice(None), slice(None), slice(None), 0), :]
difference.reset_index("eligible", drop=True, inplace=True)
difference["difference"] = (
    data_temp.loc[(slice(None), slice(None), slice(None), 1), :].values
    - data_temp.loc[(slice(None), slice(None), slice(None), 0), :].values
)

difference.reset_index("year", inplace=True)
data_temp.reset_index("year", inplace=True)

# create figure 1
fig1, (ax1, ax2) = plt.subplots(1, 2)
legend_lines = [
    Line2D([0], [0], color="red", lw=2),
    Line2D([0], [0], color="black", lw=2),
]
for ethnicity, axis in [(1, ax1), (2, ax2)]:
    for cohort in [50, 51, 52, 53]:
        axis.plot(
            "year",
            "real_earnings",
            data=data_temp.loc[(ethnicity, cohort, 0), :],
            marker=".",
            color="red",
        )
        axis.plot(
            "year",
            "real_earnings",
            data=data_temp.loc[(ethnicity, cohort, 1), :],
            marker=".",
            color="black",
        )
    axis.xaxis.set_ticks(np.arange(66, 85, 2))
    axis.set_xlabel("Year")
    axis.legend(legend_lines, ["ineligible", "elgible"])
ax1.set_ylabel("Whites Earnings in 1978 Dollars")
ax2.set_ylabel("Nonwhites Earnings in 1978 Dollars")
fig1.tight_layout()

# create figure 2
fig2, axs = plt.subplots(
    4, 2, sharex=True, sharey=True, gridspec_kw={"hspace": 0}, constrained_layout=True
)
for ethnicity in [1, 2]:
    for row, cohort in enumerate([50, 51, 52, 53]):
        axs[row, ethnicity - 1].plot(
            "year", "difference", data=difference.loc[(ethnicity, cohort), :]
        )
        if ethnicity == 1:
            axs[row, ethnicity - 1].set_ylabel("19" + str(cohort))
        axs[row, ethnicity - 1].axhline(0, color="black", linestyle="--", linewidth=1)

axs[0, 0].xaxis.set_ticks(np.arange(66, 85, 2))
axs[0, 0].set_title("Whites")
axs[0, 1].set_title("Nonwhites")
fig2.suptitle("Difference in earnings by cohort and ethnicity", fontsize=13)
