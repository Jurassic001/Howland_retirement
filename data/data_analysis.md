# data_analysis
This document contains observations, possible clues, and conclusions drawn from data relating to the mystery

## Results
With an RBQL query on `howland_ratings.csv`, we can see that Mr. Howland has never posted a rating for a Humphrey Bogart movie. This is likely to prevent students from narrowing down possible movie options.

Here is the query in question, if you're interested. Remember to check the "input table has header" option:
```sql
SELECT a1 JOIN hb_movies.csv on a1 == b1
```
