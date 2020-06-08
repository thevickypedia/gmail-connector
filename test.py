from datetime import datetime
from datetime import timedelta
# 6 Jun 2020 at 20:29:35 -0700 (PDT)
# 7 Jun 2020 at 04:45:43 -0700 (PDT)
date_str = '7 Jun 2020 at 04:45:43'
datetime_obj = datetime.strptime(date_str, "%d %b %Y at %H:%M:%S") + timedelta(hours=2)
print(datetime_obj.strftime("on %A, %B %d at %Y %I:%M %p"))
