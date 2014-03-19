#!/usr/bin/python3
'''
    holds class for the time table maker
'''

import sys

class TimeTableMaker:
    '''
        eases the way to make time tables
    '''

    def __init__(self, input_string):
        self.time_string = input_string
        self.str_arr = self.time_string.split(';')
        if len(self.str_arr) != 3:
            self.help_message()
        tmp = self.str_arr[0].split(':')
        self.start = (int(tmp[0]), int(tmp[1]))
        self.pause = int(self.str_arr[1])
        self.times = self.str_arr[2].split(',')
        self.result = ''

    @staticmethod
    def help_message():
        '''
            prints help message
        '''
        print('please provide an input string like 14:00;10;2x30,40 -> ' +
                '\n14:00-14:30\n14:40-15:10\n15:20-16:00')

    @staticmethod
    def add_time(hours, minutes, time):
        '''
            calculates the end time after a start time
            XX:XX plus minutes
        '''
        hours += (minutes + time) // 60
        hours = hours % 24
        minutes = (minutes + time) % 60
        return hours, minutes

    def add_result(self, hours, minutes, char):
        '''
            adds time value to result with end char
        '''
        str_hours = str(hours)
        str_minutes = str(minutes)
        if len(str_hours) < 2:
            str_hours = '0' + str_hours
        if len(str_minutes) < 2:
            str_minutes = '0' + str_minutes
        self.result += str_hours + ':' + str_minutes + char

    def prepare_time_table(self):
        '''
            creates the time table from the input string
        '''
        for i in range(0, len(self.times)):
            if self.times[i].find('x') != -1:
                tmp = self.times[i].split('x')
                time = int(tmp[1])
                for i in range(0, int(tmp[0])):
                    self.add_result(self.start[0], self.start[1], '-')
                    self.start = self.add_time(self.start[0], self.start[1]
                            , time)

                    self.add_result(self.start[0], self.start[1], '\n')
                    self.start = self.add_time(self.start[0], self.start[1]
                            , self.pause)
            else:
                self.add_result(self.start[0], self.start[1], '-')
                self.start = self.add_time(self.start[0], self.start[1]
                        , int(self.times[i]))

                self.add_result(self.start[0], self.start[1], '\n')
                self.start = self.add_time(self.start[0], self.start[1]
                        , self.pause)

    def print_time_table(self):
        '''
            returns time table string from input
        '''
        self.prepare_time_table()
        print(self.result)

if __name__ == '__main__':
    ttm = TimeTableMaker(sys.argv[1])
    ttm.print_time_table()
