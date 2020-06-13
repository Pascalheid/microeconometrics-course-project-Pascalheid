import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.formula.api as smf


# recreate Figure 3
# load data set
data = pd.read_stata(r"data\cwhsc_new.dta")

# drop some variables
data = data.loc[(data["year"] >= 81) & (data["race"] == 1) & (data["type"] == "TOTAL")]
data.reset_index(inplace=True, drop=True)

# create dummies for year and birth year
data = pd.concat([data, pd.get_dummies(data["year"], prefix="year")], axis=1)
data = pd.concat([data, pd.get_dummies(data["byr"], prefix="byr")], axis=1)

# get earnings residuals
columns = [
    "year_81",
    "year_82",
    "year_83",
    "year_84",
    "byr_50",
    "byr_51",
    "byr_52",
    "byr_53",
]
formula = "earnings ~ " + " + ".join(columns[:])
data["ernres"] = smf.ols(formula=formula, data=data).fit().resid

# obtain mean of the earnings residual by interval and birth year
ernres2 = data.groupby(["byr", "interval"])["ernres"].mean().to_frame()
data = pd.merge(data, ernres2, how="outer", on=["byr", "interval"])

# get probability residuals
columns = ["byr_50", "byr_51", "byr_52", "byr_53"]
formula = "ps_r ~ " + " + ".join(columns[:])
data["pres"] = smf.ols(formula=formula, data=data).fit().resid

# look at it only for the year 1981
data = data.loc[data["year"] == 81]

# get fitted values for linear fit plot
fitted_values = smf.ols(formula="ernres_y ~ pres", data=data).fit().predict()

# plot earnings residuals on probablity residuals
fig, ax = plt.subplots()
ax.scatter(x=data["pres"], y=data["ernres_y"])
ax.plot(data["pres"], fitted_values, color="red")
ax.set_ylim([-3100, 3100])
ax.set_xlim([-0.09, 0.17])
ax.set_ylabel("Earnings Residual")
ax.set_xlabel("Probability Residual")
fig
