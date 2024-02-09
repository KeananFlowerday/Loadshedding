import GetSchedule as Schedule

load_shedding_times = Schedule.get_load_shedding_times()
if load_shedding_times:
    for day, times in load_shedding_times.items():
        print(day)
        for time_slot in times:
            print(time_slot)
        print()
