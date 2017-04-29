"""
Config file read for pandas sql nest logger

Derek Rowland 2017
derek.a.rowland@gmail.com

"""
import sys
import matplotlib.pyplot as plt
from mysql.connector import (connection)

import argparse
from argparse import Namespace

#for config parsing
import os.path
import sys
import configparser



PROGNAME = "nestplotter.py"
PROGDESC = "Plot my nest data to pyplot"

DBADDR = ""
DBPORT = ""
DBUSERNAME = ""
DBPW = ""
DBDATABASE = ""

def getArgs():
    """
    get config file path
    """
    parser = argparse.ArgumentParser(prog=PROGNAME, description=PROGDESC)
    parser.add_argument("-c","--configfile",help="Configuration file path",required=True)
    return parser.parse_args()

def getfileConfig():
    """
    extract settings from file
    """
    global DBADDR
    global DBPORT
    global DBUSERNAME
    global DBPW
    global DBDATABASE
    
    #if (os.path.isfile(args.configfile))
    fileexists = os.path.isfile(args.configfile)
    
    if (not os.path.isfile(args.configfile)):
        sys.exit("Error: Argument input config file '" + args.configfile + "' does not exist.  Exiting script...")
        
    c = configparser.RawConfigParser()
    c.read(args.configfile)
    
    DBADDR = c.get('database', 'address').strip('"')
    DBPORT = c.get('database', 'port').strip('"')
    DBUSERNAME = c.get('database', 'username').strip('"')
    DBPW = c.get('database', 'passwd').strip('"')
    DBDATABASE = c.get('database', 'database').strip('"')
    
    print(DBADDR)
    print(DBUSERNAME)
    print(DBPW)
    print(DBPORT)
    print(DBDATABASE)
    
    if not checkdb():
        print("Error connecting to DB.... exiting...")
        sys.exit()

    qry = ("select target_type, time_stamp, target_temp_low, "
           "target_temp_high, current_temperature, ac_state, fan_state, "
           "heater_state, outside_temperature "
           " from nest_log order by "
           "time_stamp desc limit 5040;")
    print(qry)

    cnx = connection.MySQLConnection(
        user=DBUSERNAME,
        password=DBPW,
        port=DBPORT,
        host=DBADDR,
        database=DBDATABASE)

    cursor = cnx.cursor()
    cursor.execute(qry)

    results = cursor.fetchall()

    count = len(results)
    print("Found " + str(count) + " records")
    cursor = cnx.close()
    cnx.close()

    #settype = extract(results, 0)
    times = extract(results, 1)
    t_low = extract(results, 2)
    t_high = extract(results, 3)
    t_curr = extract(results, 4)
    st_ac = extract(results, 5)
    #st_fan = extract(results, 6)
    st_heat = extract(results, 7)
    t_out = extract(results, 8)

    plt.figure(1)
    plt.subplot(211)
    plt.plot(times, t_out, 'g', label='outside')
    plt.plot(times, t_curr, 'b', label='current')
    plt.plot(times, t_high, 'r', label='high setpt')
    plt.plot(times, t_low, 'c', label='low setpt')
    plt.ylabel('Temp(F)')
    plt.xlabel('Date / Hr')
    plt.title('Temperature vs Time')
    plt.grid(True)
    plt.legend(bbox_to_anchor=(1, 1))

    plt.subplot(212)
    plt.plot(times, st_ac, 'b', label='AC')
    plt.plot(times, st_heat, 'r', label='Heat')
    plt.ylabel('Run state')
    plt.xlabel('Date / Hr')
    plt.title('AC/Heater Run State')
    plt.legend(bbox_to_anchor=(1, 1))

    plt.subplots_adjust(hspace=0.5)

    plt.show()

    print("Done.")

def extract(results, index):
    """
    extract one subset of data
    """
    mylist = []
    indexer = 0
    for item in results:
        mylist.append(item[index])
        indexer += 1
    return mylist

def checkdb():
    """ Check database connection """
    cnx = connection.MySQLConnection()
    try:
        print("Testing database parameters...")
        # Open database connection
        cnx = connection.MySQLConnection(
            user=DBUSERNAME,
            password=DBPW,
            host=DBADDR,
            port=DBPORT,
            database=DBDATABASE,
            connection_timeout=1000)

        # prepare a cursor object using cursor() method
        cursor = cnx.cursor()
        cursor.execute("SELECT VERSION()")
        results = cursor.fetchone()
        cursor = cnx.close()
        cnx.close()

        # Check if anything at all is returned
        if results:
            print("    DB Version: " + str(results[0]))
            return True
        return False
    except connection.errors.InterfaceError:
        #print "ERROR IN CONNECTION"
        return False
    

#############
# MAIN
#############
def main(args):
    """
    Main routine
    """
    getfileConfig()
    
    


###########################
# PROG DECLARE
###########################
if __name__ == '__main__':
    args = getArgs()
    main(args)