from db import app,mysql  
from dotenv import load_dotenv
load_dotenv()

@app.route('/getGalletas', methods=['GET'])
def getGalletas():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM galletas')
    data = cur.fetchall()
    cur.close()
    print(data)
    return str(data)