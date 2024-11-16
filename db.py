import sqlite3 as lite
import datetime
import psutil


def wbfixData():

    con=lite.connect("wb.db")
    cur=con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS wb_data (id INTEGER PRIMARY KEY AUTOINCREMENT,VehicleNo TEXT,VehicleType TEXT,PartyName TEXT,Charges TEXT,Material TEXT,GrossWeight INTEGER,TareWeight INTEGER,GrossWeightDate TEXT,GrossWeightTime TEXT,TareWeightDate TEXT,TareWeightTime TEXT,Final TEXT)")
    con.commit()
    con.close()

def lastRst():

    con=lite.connect("wb.db")
    cur=con.cursor()
    cur.execute("SELECT seq FROM sqlite_sequence WHERE name='wb_data'")
    rst=cur.fetchone()[0]
    con.commit()
    con.close()
    return rst


def getsecond(id):

    con=lite.connect("wb.db")
    cur=con.cursor()
    cur.execute(f"SELECT * FROM wb_data WHERE id={int(id)} ")
    row=cur.fetchone()
    con.close()
    return row



def SaveWbData(data):
 
    con=lite.connect("wb.db")
    cur=con.cursor()
    cur.execute('''
        INSERT INTO wb_data (
            VehicleNo,
            VehicleType,
            PartyName,
            Charges,
            Material,
            GrossWeight,
            TareWeight,
            GrossWeightDate,
            GrossWeightTime,
            TareWeightDate,
            TareWeightTime,
            Final,
            NetWeight,
            NetWeightDate,
            NetWeightTime
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?)
    ''', data)
    con.commit()
    con.close()




def UpdateWbData(data):
    con = lite.connect("wb.db")
    cur = con.cursor()
    cur.execute('''
        UPDATE wb_data SET
            VehicleNo = ?,
            VehicleType = ?,
            PartyName = ?,
            Charges = ?,
            Material = ?,
            GrossWeight = ?,
            TareWeight = ?,
            GrossWeightDate = ?,
            GrossWeightTime = ?,
            TareWeightDate = ?,
            TareWeightTime = ?,
            Final = ?,
            NetWeight = ?,
            NetWeightDate = ?,
            NetWeightTime = ?
            
        WHERE id = ?
    ''', data)
    con.commit()
    con.close()



def fetch_data():
    con = lite.connect("wb.db")  # Replace "your_database.db" with your database file path
    cur = con.cursor()

    # Fetch data where Final column is set to "G" or "T"
    cur.execute("SELECT * FROM wb_data WHERE Final IN (?, ?)", ("G", "T"))
    data = cur.fetchall()

    # Close the database connection
    cur.close()
    con.close()

    # Return the fetched data
    return data





def GetAll():
    con=lite.connect("wb.db")
    cur=con.cursor()
    cur.execute("SELECT * FROM wb_data")
    rows=cur.fetchall()
    con.close()
    return rows


def Update_Seting(data):
    con=lite.connect("wb.db")
    cur=con.cursor()
    # Step 2: Prepare and execute the UPDATE query for the single row
    cur.execute("""UPDATE Setting SET
                                    CName = ?,
                                    Add1 = ?,
                                    Add2 = ?,
                                    PType = ?,
                                    SWPrint = ?,
                                    NCopyF1 = ?,
                                    NCopyF2 = ?,
                                    DP = ?,
                                    CPort = ?,
                                    BRate = ?,
                                    EString = ?,
	                                WDigits = ?,
	                                RShift = ?,
                                    camEN = ?,
                                    IPcam1 = ?,
                                    IPcam2 = ?,
                                    picEN = ?
	                                WHERE id = '1'""",data)
    con.commit()
    con.close()



def loadcom():
    con=lite.connect("wb.db")
    cur=con.cursor()
    cur.execute(f"SELECT * FROM Setting WHERE ID = '1' ")
    row=cur.fetchone()
    con.close()
    return row


def reset():
    con=lite.connect("wb.db")
    cur=con.cursor()
    cur.execute("DELETE FROM wb_data")
    cur.execute("UPDATE sqlite_sequence SET name = ?, seq = ? WHERE name='wb_data'",["wb_data",0])
    nrows = cur.rowcount
    con.commit()
    con.close()

    return nrows

def delone(delRst):
    con=lite.connect("wb.db")
    cur=con.cursor()
    cur.execute("SELECT seq FROM sqlite_sequence WHERE name='wb_data'")
    rst=cur.fetchone()[0]
    cur.execute(f"DELETE FROM wb_data WHERE id = {delRst}")
    if int(delRst)==int(rst):
        cur.execute("UPDATE sqlite_sequence SET name = ?, seq = ? WHERE name='wb_data'",["wb_data",(int(rst)-1)])
    nrows = cur.rowcount
    con.commit()
    con.close()

def Lcheck():

    con=lite.connect("wb.db")
    cur=con.cursor()
    cur.execute(f"SELECT * FROM cclc WHERE ID = '1' ")
    row=cur.fetchone()
    con.close()
    MAC=row[1]
    Ldate=row[2]
    today=datetime.datetime.today()
    xdate=today.strftime("%d-%m-%Y")
    xdate = datetime.datetime.strptime(xdate, "%d-%m-%Y").date() if xdate else None
    Ldate = datetime.datetime.strptime(Ldate, "%d-%m-%Y").date() if Ldate else None
    cmac=str(get_mac_address())

    if xdate<Ldate and (MAC==cmac or MAC=="JAI SHREE RAM"):
        return 1
    else:
        return 0



def get_mac_address():
    try:
        # Get a list of network interfaces
        interfaces = psutil.net_if_addrs()

        # Find the MAC address of the first Ethernet (LAN) interface available
        for interface, addresses in interfaces.items():
            for address in addresses:
                if address.family == psutil.AF_LINK:
                    return address.address
    except psutil.Error:
        pass

    return None



def Update_lic():
    mac=str(get_mac_address())
    today=datetime.datetime.today()
    xdate=today.strftime("%d-%m-%Y")
    xdate = datetime.datetime.strptime(xdate, "%d-%m-%Y").date()

    one_year_later = xdate + datetime.timedelta(days=370)
    one_year_later_str = one_year_later.strftime("%d-%m-%Y")
    data=[mac,one_year_later_str]
    con=lite.connect("wb.db")
    cur=con.cursor()
    cur.execute("""UPDATE cclc SET MAC = ?, LDATE = ? WHERE ID = '1'""",data)
    con.commit()
    con.close()
    return data

