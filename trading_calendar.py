from pandas.tseries.holiday import (AbstractHolidayCalendar, Holiday,
                                    USMartinLutherKingJr, USPresidentsDay,
                                    GoodFriday, USMemorialDay,
                                    USLaborDay, USThanksgivingDay,
                                    nearest_workday)


class USTradingCalendar(AbstractHolidayCalendar):
    rules = [
        Holiday('NewYearsDay', month=1, day=1, observance=nearest_workday),
        USMartinLutherKingJr,
        USPresidentsDay,
        GoodFriday,
        USMemorialDay,
        Holiday('USIndependenceDay', month=7, day=4, observance=nearest_workday),
        USLaborDay,
        USThanksgivingDay,
        Holiday('Christmas', month=12, day=25, observance=nearest_workday)
    ]
