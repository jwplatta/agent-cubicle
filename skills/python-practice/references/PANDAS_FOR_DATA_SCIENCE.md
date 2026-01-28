# Essential Pandas Functions and Techniques for Data Cleaning and Exploration

## 1. Quick Dataset Overview (First Look)
- `df.head()` / `df.tail()` → preview rows
- `df.shape` → (rows, columns)
- `df.columns` → column names
- `df.dtypes` → data types per column
- `df.info()` → types, null counts, memory usage
- `df.describe()` → summary stats for numeric columns
- `df.describe(include="all")` → summary stats for everything

## 2. Understanding Missing Data
- `df.isna()` / `df.isnull()` → detect missing values
- `df.notna()` → detect non-missing values
- `df.isna().sum()` → missing count per column
- `df.isna().mean()` → missing rate per column
- `df.dropna()` → remove missing rows or columns
- `df.fillna(value)` → fill missing values
- `df.interpolate()` → fill missing values using interpolation

Techniques:
- Drop columns with too many nulls
- Fill numeric columns with mean or median
- Fill categorical columns with mode or `"Unknown"`

## 3. Cleaning Column Names and Text
- `df.rename(columns={...})`
- `df.columns.str.lower()`
- `df.columns.str.strip()`
- `df.columns.str.replace(" ", "_")`

Text cleaning for string columns:
- `df["col"].str.strip()`
- `df["col"].str.lower()` / `df["col"].str.upper()`
- `df["col"].str.replace(pattern, replacement, regex=True)`
- `df["col"].str.contains("x")`
- `df["col"].str.extract(r"...")`

## 4. Fixing Data Types
- `df.astype(type)` → convert type
- `pd.to_numeric(df["col"], errors="coerce")`
- `pd.to_datetime(df["col"], errors="coerce")`
- `df["col"].dt.year` / `df["col"].dt.month` / `df["col"].dt.day`

Useful helpers:
- `df.select_dtypes(include="number")`
- `df.select_dtypes(include=["object", "category"])`

## 5. Detecting and Removing Duplicates
- `df.duplicated()` → True/False per row
- `df.duplicated().sum()` → count duplicates
- `df.drop_duplicates()` → remove duplicates
- `df.drop_duplicates(subset=["col1", "col2"])`

## 6. Filtering Rows
- `df[df["col"] > 5]`
- `df[df["col"].isin([...])]`
- `df[df["col"].between(a, b)]`
- `df[df["col"].str.contains("abc", na=False)]`

Readable alternative:
- `df.query("col > 5 and other_col == 'yes'")`

## 7. Sorting and Selecting Data
- `df.sort_values("col")`
- `df.sort_values(["col1", "col2"], ascending=[True, False])`
- `df.nlargest(10, "col")`
- `df.nsmallest(10, "col")`

Column and row selection:
- `df[["col1", "col2"]]`
- `df.loc[rows, cols]` → label-based
- `df.iloc[rows, cols]` → position-based

## 8. Handling Outliers and Bad Values
- `df["col"].quantile([0.01, 0.99])`
- `df["col"].clip(lower, upper)` → cap values

Replacing values:
- `df.replace({0: np.nan})`
- `df["col"].where(condition, other_value)`

## 9. Value Counts and Frequency Exploration
- `df["col"].value_counts()`
- `df["col"].value_counts(normalize=True)` → percentages
- `df["col"].nunique()`
- `df["col"].unique()`

## 10. Grouping and Aggregations
- `df.groupby("col").size()`
- `df.groupby("col")["num"].mean()`
- `df.groupby(["col1", "col2"]).agg({"num": ["mean", "sum", "count"]})`

Useful technique:
- `df.groupby("col").transform("mean")`
  (adds group-level stats back to original rows)

## 11. Creating and Editing Columns
- `df["new"] = ...`
- `df.assign(new_col=...)`

Conditional logic:
- `np.where(condition, value_if_true, value_if_false)`
- `df["col"].map(dict)` → map categories to values
- `df["col"].apply(func)` → slower but flexible

Binning:
- `pd.cut(df["age"], bins=[0, 18, 35, 60, 100])`
- `pd.qcut(df["income"], q=4)` → quartiles

## 12. Merging and Joining DataFrames
- `pd.merge(df1, df2, on="id", how="inner")`
- `pd.merge(df1, df2, on="id", how="left")`
- `df.join(other_df)`
- `pd.concat([df1, df2], axis=0)` → stack rows
- `pd.concat([df1, df2], axis=1)` → add columns

## 13. Reshaping Data
- `df.melt(id_vars=[...], value_vars=[...])` → wide to long
- `df.pivot(index=..., columns=..., values=...)`
- `df.pivot_table(..., aggfunc="mean")`

## 14. Exploratory Correlations and Checks
- `df.corr(numeric_only=True)`
- `df["a"].corr(df["b"])`
- `df.groupby("col")["num"].describe()`

## 15. Simple Visualization
- `df["col"].hist()`
- `df["col"].plot(kind="box")`
- `df.plot.scatter(x="a", y="b")`

## 16. Performance and Clean Work Habits
- `df.copy()` → avoid unintended side effects
- Prefer `df.loc[mask, "col"] = value` over chained indexing
- Use vectorized operations instead of loops
  - `df["col"] + 1` instead of `df["col"].apply(...)`

## Workflow
1. `df.head()`, `df.info()`, `df.describe()`
2. Check missing values with `df.isna().sum()`
3. Fix data types using `to_datetime`, `to_numeric`, `astype`
4. Clean strings and categories
5. Remove duplicates
6. Explore distributions with `value_counts` and `groupby`
7. Merge or reshape if needed
8. Identify and handle outliers