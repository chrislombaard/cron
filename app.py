#!/usr/bin/python

"""
A management command for the running of various cron tasks.

~ Lyst Programming Assignment ~ 03/08/2019

Note: I did some extra checks, just so that you can see that I take all edge cases into
      consideration when attempting to solve a problem. I split the application into multiple
      functions, since I wanted the code to be as functional as possible, and then once the code
      works well, tidy it up.

      Lastly, I followed pep8 formatting as much as possible.
"""
import sys


def validate_input(current_time):
    """
    Validates the current time input that is provided by the user in the command line.
    Based on the spec given, the input needs to adhere to <HH:MM>.
    :param current_time: The current time string passed through the command line args.
    """
    params = current_time.split(':')
    if len(params) != 2:
        print("Error: Please only input in the format <HH:MM>.")
        exit(1)

    for param in params:
        if not param.isdigit():
            print("Error: Current time input should only be valid integers. [0-9][0-9]:[0-9][0-9]")
            exit(1)

    # Ensure the params are casted to integers so that we can work with them.
    hour = int(params[0])
    minute = int(params[1])

    if hour < 0 or hour > 24:
        print("Error: HH must be between [0-24]")
        exit(1)

    if minute < 0 or minute > 60:
        print("Error: MM must be between [0-60]")
        exit(1)

    return {"hour": hour, "minute": minute}


def validate_task(params):
    """
    Validates the task string that is passed through the config file.
    :param params: The first param is the minute_past_hour, second param is the
    hour_of_day, and last is the command string.
    """
    if len(params) != 3:
        print("Error: Each task in the config file must have 3 arguments.")
        exit(1)

    minute_past_hour = params[0]
    if not minute_past_hour.isdigit() and minute_past_hour != '*':
        print("Error: (Minute past the hour) field in the config must be a "
              "valid integer between [0-60] or '*'")
        exit(1)

    hour_of_day = params[1]
    if not hour_of_day.isdigit() and hour_of_day != '*':
        print("Error: (Hour of the day) field in the config must be a "
              "valid integer between [0-24] or '*'")
        exit(1)

    if hour_of_day.isdigit():
        if int(hour_of_day) > 24 or int(hour_of_day) < 0:
            print("Error: (Hour of the day) field in the config must be a "
                  "valid integer between [0-24] or '*'")
            exit(1)

    command = params[2]
    if command.strip() not in ["/bin/run_me_daily",
                               "/bin/run_me_hourly",
                               "/bin/run_me_every_minute",
                               "/bin/run_me_sixty_times"]:
        print("Error: Invalid command field: " + command)
        exit(1)

    return {
        "minute_past_hour": minute_past_hour,
        "hour_of_day": hour_of_day,
        "command": command
    }


def calculate(current_time, kwargs):
    """
    Calculates the earliest time that a task will run, based on the current time,
    and HH:MM parameters.
    :param current_time: The current time object containing keys for 'hour' and 'minute'.
    :param kwargs: The rest of the parameters from the config file tasks, i.e minute_past_hour,
    hour_of_day and the command.
    """
    minute_past_hour = kwargs.get("minute_past_hour")
    hour_of_day = kwargs.get("hour_of_day")
    command = kwargs.get("command")

    # Set default values
    tense = "today"
    hour = "00"
    minute = "00"

    current_hour = int(current_time["hour"])
    current_minute = int(current_time["minute"])

    if minute_past_hour == "*" and hour_of_day == "*":
        # First case, where both fields are supposed to run on each value.
        # Defaults to current time.
        hour = current_hour
        minute = current_minute
    elif minute_past_hour.isdigit() and hour_of_day == "*":
        # Second case, where the task must run for every minute, not hour.
        # In this case we set the hour to the current hour, but check if the
        # clock ticks over to the next day.
        if current_hour == 24:
            hour = "00"
            tense = "tomorrow"
        else:
            hour = current_hour
        minute = minute_past_hour
    elif minute_past_hour == "*" and hour_of_day.isdigit():
        # Third case where the task needs to run for each minute of the hour selected,
        # In this case, we check if the hour_of_day is greater than the current hour,
        # then we know it will run today, else it will run tomorrow.
        if int(hour_of_day) > current_hour:
            hour = hour_of_day
            tense = "today"
        else:
            hour = current_hour
            tense = "tomorrow"
    else:
        # The third and last case, where the task has to run at a specific hour and minute
        # Here we need to check if the current hour is greater than the hour_of_day, then we know
        # the task needs to run the next day. If not, then it will most probably run today,
        # except for the edge case where the hour_of_day is 24. Then we know it will only run the
        # next day.
        # Lol, sorry for all the comments, just trying to be thorough :)
        if int(hour_of_day) < current_hour:
            tense = "tomorrow"
            hour = int(hour_of_day)
        else:
            if int(hour_of_day) == 24:
                hour = "00"
                tense = "tomorrow"
            else:
                hour = hour_of_day
                tense = "today"
        minute = int(minute_past_hour)

    # In some cases, if in the config, a user puts 0 instead of 00, we just correct for that here.
    hour = "00" if hour == 0 else str(hour)
    minute = "00" if minute == 0 else str(minute)

    calculated_time = hour + ":" + minute + " " + tense + " - " + command

    # We strip away the newline, since the output spec specifically does not show any newlines.
    return calculated_time.strip("\n")


def main():
    # Here we grab the args passed in via the command line.
    # As well as the file that was piped through to the stdin.
    args = sys.argv
    file = sys.stdin

    # Some basic checks for the command line inputs
    if len(args) != 2:
        print("Please enter the right number of arguments.")
        exit(1)

    # Validate the current time input, (I know this wasn't indicated in the spec, but I felt it
    # was something that would have had to be done if this code would need to make it to
    # production.
    current_time = validate_input(current_time=args[1])

    # Run through each line of the config file, split the config tasks based on whitespace
    # Then validate the task params, (Again, not specifically indicated in the spec, but felt that
    # I should add it :)
    for task in file:
        params = task.split(' ')
        kwargs = validate_task(params)

        # Print final output
        print(calculate(current_time=current_time, kwargs=kwargs))


if __name__ == "__main__":
    main()
