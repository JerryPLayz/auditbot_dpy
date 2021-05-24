import os, sys, urllib, requests
import discord
from discord.utils import get
import datetime
import asyncio
import time
import logging
import traceback
import auth
import formatter as fmt
from zipfile import *

class BotReq:
    def __init__(self, packet, reqType=1, invoker=None, orgMessage=None): # 1 = get-ip
        self.packet = packet
        self.reqType = reqType
        self.invoker = invoker
        self.orgMessage = orgMessage

    def get_id(self):
        return self.packet.id

    def get_type(self):
        return self.reqType

ps = os.path.sep
cwd = os.getcwd()
print(cwd)

dateStr = str(datetime.datetime.now()).split(" ")
part = dateStr[0]
#                Hour                                 Minute
comp = str(dateStr[1].split(":")[0]) + "_" + str(dateStr[1].split(":")[1])
part += "_" + comp
dateStr = part

LOG_FORMAT = "%(levelname)s | %(asctime)s : %(message)s"
try:
    logging.basicConfig(filename=cwd+f"{ps}logs{ps}"+dateStr +"-py.log", level=logging.INFO, format=LOG_FORMAT)
except BaseException:
    os.mkdir(cwd+"{ps}logs")
    logging.basicConfig(filename=cwd+"{ps}logs{ps}"+dateStr +"-py.log", level=logging.INFO, format=LOG_FORMAT)

logger = logging.getLogger()

PREFIX = "AB>>"
tokenfile = open("token.txt")

client = discord.Client()
## This is the bot's secret token
token = tokenfile.readlines()[0]
tokenfile.close()

req_inProg = []

status = PREFIX + " Watching all of you...."

def print_n_log(msg="NOTSET", level=logging.INFO):
    if level == logging.INFO:
        logger.info(msg)
    elif level == logging.WARNING:
        logger.warning(msg)
    elif level == logging.ERROR:
        logger.error(msg)
    elif level == logging.CRITICAL:
        logger.critical(msg)
    print(f"{datetime.datetime.now()}: " + msg)

print_n_log("Logging initiated successfully")

async def perform_requests():
    try:
        while True:
            await asyncio.sleep(1)
            if len(req_inProg) > 0:
                req = req_inProg.pop(0)
                message = req.packet.content[len(PREFIX)+1::]

                
                if req.get_type() == 1: # requesting IP
                    print_n_log(f"{req.invoker} => REQ ipget")
                    
                    cont = req.packet.content
                    await req.packet.edit(content=cont.replace("[STANDBY]", "[QUERY]"))
                    #print("Query")
                    query = urllib.request.urlopen('https://ident.me')
                    cont = req.packet.content
                    await req.packet.edit(content=cont.replace("[QUERY]","[READ/DECODE]"))
                    #print("Decode")
                    ip = str(query.read().decode('utf8'))
                    cont = req.packet.content
                    await req.packet.edit(content=cont.replace("[READ/DECODE]", ip))
                    #print("Req Sucess")

                    
                elif req.get_type() == 2:
                    print_n_log(f"{req.invoker} => REQ credentials")
                    admin = auth.check_auth(req.invoker, file="auth-users.txt")
                    mod = auth.check_roles_for_moderator(req.invoker)
                    if admin == True:
                        await req.packet.edit(content="Your Access Level is **Server Administrator**")
                    elif mod == True:
                        await req.packet.edit(content="Your Access Level is **Discord Moderator**")
                    else:
                        await req.packet.edit(content="Your Access Level is **Standard User**")

                        
                elif req.get_type() == 3:
                    print_n_log(f"{req.invoker} => REQ audit")
                    message = req.orgMessage.content[len(PREFIX)+1::]
                    curDay = get_curTime().split("_")[0]
                    try:
                        comps = message.split(" ")[1::]
                        print(comps)
                        if len(comps) == 1:
                            if len(comps[0].split("-")) == 3:
                                curDay = comps[0]
                            else:
                                raise ArithmeticError(f"Incorrect Date Format for Audit: {comps[0]}")
                    except BaseException as BE:
                        exc = sys.exc_info()
                        print("An error occured in audit request. See log for details.")
                        write_exception(exc)
                        await req.packet.edit(content="Date was improperly formatted. Should be 'YYYY-MM-DD'")
            
                    string = f"audit_{curDay}.log"
                    
                    try:
                        await req.packet.channel.send(content=f"**Audit Log for {curDay}**", file=discord.File(fp=open(f"./logs/audit/{string}", "rb") ,filename=f"{string}"))
                        print_n_log(f"  {req.invoker} => Audit Request for date {curDay} being fulfilled.")
                    except FileNotFoundError as FNFE:
                        print("The file requested could not be found.")
                        print_n_log(f"  {req.invoker} => Audit Request could not be fulfilled: File does not exist.")
                        await req.packet.edit(content=f"ERROR | Audit Request could not be fulfilled: **File does not exist.**")

                    except BaseException as BE:
                        exc = sys.exc_info()
                        write_exception(exc)
                        print("An error occured in sending file. See log for more details.")
                        # Ignore
                        etype = exc[0]
                        val = exc[1]
                        traceObj = exc[2]
                        formatted = traceback.format_exception(etype=etype, value=val, tb=traceObj)
                        formattedStr = '\n'.join(formatted)
                        await req.packet.edit(content=f"""An error occured while sending file: ```py \n{formattedStr}```""")
                    #finally:
                    #    await req.packet.delete(delay=100)
                    #await req.orgMessage.delete(delay=4)
                    #await req.packet.delete(delay=2)
    except BaseException as BE:
        print("An error occured in the requests handler method. See the Console for details.")
        write_exception(sys.exc_info())
                                      
async def get_ex_ip():
    return urllib.request.urlopen('https://ident.me').read().decode('utf8')

##def check_authorized(User, filename="banned-users.txt"):
##     return bool(get_auth_users(filename).check_user(User.id))
##############################################################################
## Error Logging (Non-Discord Related)

def write_exception(exc_info, level=logging.ERROR):
    #logger.log(level, msg)
    etype = exc_info[0]
    val = exc_info[1]
    traceObj = exc_info[2]
    formatted = traceback.format_exception(etype=etype, value=val, tb=traceObj)
    formattedStr = '\n'.join(formatted)
    logger.log(level, msg=f"An error occured in a thread. Traceback follows:\n\n\t{formattedStr}\n")
    
@client.event
async def on_ready():
    print("## Audit Bot activated ##")
    await client.change_presence(activity=discord.Game(name=status))

@client.event
async def on_message(packet):
    raised_critical=False
    try:
        body = packet.content
        message = None
        keyword = None
        
        if body.startswith(PREFIX):
            message = body[len(PREFIX)+1::]
            keyword = message.split(" ")[0]
        else: # message was not directed at bot
            return 0

        if auth.check_auth(packet.author, file="banned-users.txt"): # false for unbanned players
            await packet.channel.send("You are not authorized to use this utility")
            print_n_log(f"Failed attempt by {packet.author} to access the Utility.")
            return 1

        #print(auth.check_roles_for_moderator(packet))
        #print(message)
        if message == "get-ip" and get_credentials(packet) == 2:
            resp = await packet.channel.send("IPGET: The IP of Server is `[STANDBY]`")
            req_inProg.append(BotReq(resp, 1, packet.author))

        if message=="raise-error" and get_credentials(packet) == 2:
            if auth.check_authorized(packet.author, file="auth-users.txt"):
                await packet.channel.send("Client-side has raised an error. Handle in progress...")
                raise BaseException("Forcible Raise Error by Client -> Authorized Test")
            else:
                await packet.channel.send("You are not authorized to do this.")
                print_n_log(f"Failed attempt by {packet.author} to raise an error.", logging.WARN)

        if message == "raise-critical" and get_credentials(packet) == 2:
            if auth.check_authorized(packet.author, file="auth-users.txt"):
                    await packet.channel.send("Client-side has raised a Critical Level Error. Handle in Progress...")
                    raised_critical = True
                    raise BaseException("Forcible Raise Critical by Client -> Authorized Test")
            else:
                await packet.channel.send("You are not authorized to do this.")
                print_n_log(f"Failed attempt by {packet.author} to raise a CRITICAL error.", logging.WARN)
        
        if message == "check-credential":
            print_n_log(f"User {packet.author} requested credential check.", logging.INFO)
            resp = await packet.channel.send("Checking your access level...")
            req_inProg.append(BotReq(resp, 2, packet.author, packet))

        if message == "help" and get_credentials(packet) >= 1:
            # mod = auth.check_roles_for_moderator(packet.author)
            print_n_log(f"User {packet.author} requested the help menu.")
            await packet.channel.send("Use **AB>> check-credential** to check your level of access to this bot's systems.\n"\
                                "Use **AB>> get-audit YYYY-MM-DD** to get an audit log for a specific day.\n"\
                                "Use **AB>> help** to see this menu again.")
            

        if keyword == "get-audit" and get_credentials(packet) >= 1:
            print_n_log(f"User {packet.author} (Auth: {get_credentials(packet)}) requested a audit file.", logging.INFO)
            resp = await packet.channel.send("Getting Audit File... Please wait...")
            req_inProg.append(BotReq(resp, 3, packet.author, packet))
            
            
        if keyword == "get-audit" and get_credentials(packet) < 1:
            await packet.channel.send("You do **not** have appropriate clearance to use this function.")
            print_n_log(f"User {packet.author} attempted and failed to access an audit log.", logging.WARN)
    except BaseException as BE:
        exc = sys.exc_info()
        print("An error occured. See log for details.")
        write_exception(exc)

    if raised_critical:
        packet.channel.send("This Critical Raise has been removed.")
        pass
        #await client.close() 
        #raise BaseException("Forcible Raise Critical by Client -> Authorized Test")


def get_credentials(packet):
    mod = auth.check_roles_for_moderator(packet.author)
    admin = auth.check_auth(packet.author, file="auth-users.txt")
    if admin:
        return 2
    elif mod:
        return 1
    else:
        return 0

def get_curTime():
    dateS = str(datetime.datetime.now()).split(" ")
    part = dateS[0]
    #                Hour                                 Minute                             Second
    comp = str(dateS[1].split(":")[0]) + "_" + str(dateS[1].split(":")[1]) + "_" + str(dateS[1].split(":")[2].split(".")[0])
    part += "_" + comp
    dateS = part
    return dateS


@client.event
async def on_message_delete(packet):
    curDay = get_curTime().split("_")[0]
    fileName = f"{cwd}{ps}logs{ps}audit{ps}audit_{curDay}.log"
    auditFile = open(fileName, mode='a')
    curTime = get_curTime()
    content = packet.content.replace("\n", "\\n")
    #print_n_log(f"DELETE| {curTime} |{packet.author} in {packet.channel}=> '{content}'\n")
    auditFile.write(f"DELETE| {curTime} |{packet.author} in {packet.channel}=> '{content}'\n")
    auditFile.close()
    


@client.event
async def on_bulk_message_delete(listOfPackets):
    curDay = get_curTime().split("_")[0]
    fileName = f"{cwd}{ps}logs{ps}audit{ps}audit_{curDay}.log"
    auditFile = open(fileName, mode='a')
    curTime = get_curTime()
    content = packet.content.replace("\n", "\\n")
    for packet in listOfPackets:
        #print_n_log(f"BULK_DELETE| {curTime} | {packet.author} in {packet.channel}=> '{content}'\n")
        auditFile.write(f"BULK_DELETE| {curTime} | {packet.author} in {packet.channel}=> '{content}'\n")
    auditFile.close()

@client.event
async def on_message_edit(packetBef, packetAft):
    curDay = get_curTime().split("_")[0]
    fileName = f"{cwd}{ps}logs{ps}audit{ps}audit_{curDay}.log"
    auditFile = open(fileName, mode='a')
    curTime = get_curTime()
    contentBef = packetBef.content.replace("\n", "\\n")
    contentAft = packetAft.content.replace("\n", "\\n")
    #print_n_log(f"EDIT| {curTime} | {packetBef.author} in {packetBef.channel}: '{contentBef}' <=TO=> '{contentAft}'\n")
    auditFile.write(f"EDIT| {curTime} | {packetBef.author} in {packetBef.channel}: '{contentBef}' <=TO=> '{contentAft}'\n")
    auditFile.close()

async def auto_zip_logs():
    auditpath = f".{ps}logs{ps}audit"
    logspath = f".{ps}logs"
    zipspath = f".{ps}zips"
    print("###Autozipper running###")
    try:
        while True:
            
            #print("ASYNC: Zipping Old Log Files...")
            
            print_n_log("ASYNC: Zipping Old Log Files")
            # Log Files
            with ZipFile(zipspath + f"{ps}oldlogs-py.zip", "a") as myZip:
                files = [file for file in os.listdir(logspath) if (".log" in file and file != dateStr+"-py.log")]
                ## add to zip file
                [myZip.write(logspath + f"{ps}{file}") for file in files]
                ## remove from logs folder.
                [os.remove(logspath + f"{ps}{file}") for file in files]

            # Audits
            with ZipFile(zipspath + f"{ps}oldaudits.zip", "a") as myZip:
                curDay = get_curTime().split("_")[0]
                files = [file for file in os.listdir(auditpath) if (".log" in file and file != "audit_" + curDay +".log")]
                ## add to zip file
                [myZip.write(auditpath + f"{ps}{file}") for file in files]
                ## remove from logs folder.
                [os.remove(auditpath + f"{ps}{file}") for file in files]
            await asyncio.sleep(86450)
    except BaseException as BE:
        exc = sys.exc_info()
        write_exception(exc)
        print("An error occured in Auto Zipper thread. See log for details. Exiting...")
    
# run request handler in seperate thread (background)
asyncio.get_event_loop().create_task(perform_requests())
asyncio.get_event_loop().create_task(auto_zip_logs())
# run main thread
first = True
while True:
    if first==False:
        time.sleep(60)
    try:
        client.run(token)
    except BaseException as BE:
        write_exception(sys.exc_info(), level=logging.CRITICAL)
        print_n_log("Attempting to restart through Reinitialisation of Client....")
        asyncio.new_event_loop() # need to specify
        try:
            client=discord.Client()
            client.run(token)
            
        except BaseException as BE:
            write_exception(sys.exc_info(), level=logging.CRITICAL)
            print_n_log("Attempting to restart through Asyncio library....")
            asyncio.get_event_loop().create_task(client.run(token))
            
        
    print("Bot Errored out for some reason... attempting to reconnect in 60s. (See log for details)")
    first=False
