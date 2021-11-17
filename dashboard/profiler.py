import cProfile
import pstats
from pstats import SortKey

from sysdata.data_blob import dataBlob
from sysproduction.reporting.api import reportingApi

data = dataBlob(log_name="profile")
reporting_api = reportingApi(data, calendar_days_back=1)

cProfile.run('reporting_api.table_of_roll_data()', "rolls")


p = pstats.Stats('rolls')
p.sort_stats(SortKey.CUMULATIVE).print_stats(30)
