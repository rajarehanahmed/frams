from django.db import models
from django.utils.translation import gettext as _

DAY_OF_THE_WEEK = {
    '0' : _(u'Monday'),
    '1' : _(u'Tuesday'),
    '2' : _(u'Wednesday'),
    '3' : _(u'Thursday'),
    '4' : _(u'Friday'),
    '5' : _(u'Saturday'),
    '6' : _(u'Sunday'),
}

class DayOfTheWeekField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices']=tuple(sorted(DAY_OF_THE_WEEK.items()))
        kwargs['max_length']=1 
        super(DayOfTheWeekField,self).__init__(*args, **kwargs)