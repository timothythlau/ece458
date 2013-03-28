import MySQLdb as sql   
import sys

con = None

def createUser(email, pw):
    try:
    
        con = sql.connect('localhost', 'testuser', 'test623', 'testdb')

        with con:

            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS \
                Users(Id INT PRIMARY KEY AUTO_INCREMENT, email VARCHAR(128), password VARCHAR(128))")
            cur.execute("INSERT INTO Users(email, password) VALUES('{0}', '{1}')".format(email, pw))

    except con.Error, e:

        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)

    finally:

        if con:
            con.close()
