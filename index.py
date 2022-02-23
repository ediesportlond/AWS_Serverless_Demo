import mysql.connector

mydb = mysql.connector.connect(
    host="database1.cluster-cnracu88cr5f.us-east-1.rds.amazonaws.com",
    user="admin",
    password="Admin123",
    database="database1"
)

def check_for_entry(event):

    short = event["queryStringParameters"]["short"]

    mycursor = mydb.cursor()

    sql = "SELECT short FROM routes WHERE short = %s"
    adr = (short,)

    mycursor.execute(sql, adr)

    myresult = mycursor.fetchall()

    #false means entry does not exist
    if len(myresult) == 0:
        exists = False
    else:
        exists = True

    return {
        'statusCode': 200,
        'body': exists
    }


def handler(event, context):


    #retrieves parameter to determine how to handle request
    #new = will create new entry in DB
    #route = will redirect user to destination
    #check = check if suggested short name exists
 
    if "select" in event["queryStringParameters"]:
        select = event["queryStringParameters"]["select"]
    else:
        select = "route"
 
    if select == "new":

        #check if entry already exists before inserting to DB
        if check_for_entry(event)["body"]:
            return {
                'statusCode': 200,
                'body': "Entry already exists"
            }
        #retrieves the URL client wants to route to

        destination = event["queryStringParameters"]["url"]

        #retrieves name client would like to assign to url

        short = event["queryStringParameters"]["short"]

        mycursor = mydb.cursor()

        sql = "INSERT INTO routes (short, url) VALUES (%s, %s)"
        val = (short, destination)
        mycursor.execute(sql, val)

        mydb.commit()

        return {
            'statusCode': 200,
            'body': str(mycursor.rowcount) + " record inserted. https://jmny48wj33.execute-api.us-east-1.amazonaws.com/?s="  +short
        }
    elif select == "route":

        #retrieves parameter to find destination in DB
        short = event["queryStringParameters"]["s"]

        mycursor = mydb.cursor()

        sql = "SELECT url FROM routes WHERE short = %s"
        adr = (short,)

        mycursor.execute(sql, adr)

        myresult = mycursor.fetchall()

        #if no results on short reroute to error page
        if len(myresult) == 0:
            return {
                'statusCode': 302,
                'headers': {
                    "location": "https://shortenurl-s3bucket-16ku24jr432sv.s3.amazonaws.com/error.html" 
                }
            }

        return {
            'statusCode': 302,
            'headers': {
                "location": myresult[0][0]
            }
        }
    elif select == "check":

        return check_for_entry(event)

    else:
        #Reroutes to error page

        return {
            'statusCode': 302,
            'headers': {
                "location": "https://shortenurl-s3bucket-16ku24jr432sv.s3.amazonaws.com/error.html"
            }
        }

