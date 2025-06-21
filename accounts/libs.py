from django.utils import timezone
import math

def DatetimeNow(user):
    datetime_now = timezone.now()
    return datetime_now


def when_published(creation_date):
    if not creation_date:
        return ''

    now = timezone.now()
    
    diff= now - creation_date

    if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
        seconds= diff.seconds
        
        if seconds == 1:
            return str(seconds) + " ثانية"
        
        else:
            return str(seconds) + " ثواني"

        

    if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
        minutes= math.floor(diff.seconds/60)

        if minutes == 1:
            return str(minutes)  + " دقيقة"
        
        else:
            return str(minutes)  + " دقيقة"



    if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
        hours= math.floor(diff.seconds/3600)

        if hours == 1:
            return str(hours) + " ساعة"

        else:
            return str(hours) + " ساعات"

    # 1 day to 30 days
    if diff.days >= 1 and diff.days < 30:
        days= diff.days
    
        if days == 1:
            return str(days) + " يوم"

        else:
            return str(days) + " ايام"

    if diff.days >= 30 and diff.days < 365:
        months= math.floor(diff.days/30)
        

        if months == 1:
            return str(months) + " شهر"

        else:
            return str(months) + " اشهر"


    if diff.days >= 365:
        years= math.floor(diff.days/365)

        if years == 1:
            return str(years) + " سنة"

        else:
            return str(years) + " سنوات"

