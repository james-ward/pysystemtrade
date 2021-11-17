import cProfile
import pstats
from pstats import SortKey

import syscore

from sysdata.data_blob import dataBlob
from sysproduction.reporting.api import reportingApi

data = dataBlob(log_name="profile")
reporting_api = reportingApi(data, calendar_days_back=1)

reporting_api.table_of_roll_data()

#print(dataBlob._get_class_prefix.cache_info())
print(syscore.text.camel_case_split.cache_info())

"""
cProfile.run('reporting_api.table_of_roll_data()', "rolls")


p = pstats.Stats('rolls')
p.sort_stats(SortKey.CUMULATIVE).print_stats(30)

p.sort_stats(SortKey.TIME).print_stats(30)

p.sort_stats(SortKey.CALLS).print_stats(30)

# Get cache info
#print(reporting_api.table_of_roll_data.get_normalised_smoothed_volumes_of_contract_list.get_cache_info())
"""
