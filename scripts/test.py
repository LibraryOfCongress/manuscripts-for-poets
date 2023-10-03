# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from pprint import pprint
from utilities import *

dateString = "1866 to 1953"
# dateString = "1953-01-01 to 1953-12-31"
startDate, endDate = getDateRange(dateString)
deltaDays = (endDate - startDate).days
print(deltaDays)
