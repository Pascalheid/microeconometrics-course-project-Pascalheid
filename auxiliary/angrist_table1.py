import pandas as pd

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
earn_nz = data["vmn1"] / (1 - data["vfin1"])
data["wt_nz"] = data["vnu1"] * (1 - data["vfin1"])

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
