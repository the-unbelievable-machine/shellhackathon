#!/usr/bin/env python
# coding: utf-8

# # Shell Hackathon Submission
# 
# We concat the result file from 2019 and 2020. In addition we fix numerical isues by truncating the numerical values at 2 digits.

# In[ ]:


import pandas as pd


# In[ ]:


result_2019 = pd.read_csv("../data/processed/result_2019.csv")
result_2020 = pd.read_csv("../data/processed/result_2020.csv")


# In[ ]:


submission = pd.concat([result_2019, result_2020])


# In[ ]:


# We need to truncate the results. Otherwise the constraints are violated due to floating point issues
# see https://stackoverflow.com/a/49960574
def truncate(theNumber, theDigits):
    myDigits = 10 ** theDigits
    return (int(theNumber * myDigits) / myDigits)


# In[ ]:


submission['value'] = submission['value'].apply(lambda x: truncate(x,2))


# The following check shows, that after truncating our numerical values, no spurious negative results are left.

# In[ ]:


submission[submission["value"] < 0.0]


# Finally this is our complete result.

# In[ ]:


submission


# In[ ]:


# commented out, so we don't overwrite the result
# submission.to_csv("../data/processed/submission.csv")


# ![screenshot.png](attachment:screenshot.png)

# # The end

# In[ ]:




