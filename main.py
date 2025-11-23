import requests, os, sys, json, time, asyncio, socket, ssl, random, threading
from concurrent.futures import ThreadPoolExecutor
import aiohttp
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from google.protobuf.timestamp_pb2 import Timestamp

# Imports from your custom modules
# Make sure Pb2 folder and protobuf_decoder folder exist!
from xC4 import *
from xHeaders import *
from Pb2 import DEcwHisPErMsG_pb2, MajoRLoGinrEs_pb2, PorTs_pb2, MajoRLoGinrEq_pb2, sQ_pb2, Team_msg_pb2

# --- GLOBAL VARIABLES (For app.py integration) ---
online_writer = None
whisper_writer = None
key = None
iv = None
region = None
TarGeT = None
bot_uid = None

# Logic Flags
spam_room = False
fast_spam_running = False
fast_spam_task = None
custom_spam_running = False
custom_spam_task = None

# --- HELPER FUNCTIONS ---

def get_random_color():
    colors = ["[FF0000]", "[00FF00]", "[0000FF]", "[FFFF00]", "[00FFFF]", "[FFFFFF]"]
    return random.choice(colors)

async def encrypted_proto(encoded_hex):
    k = b'Yg&tc%DEuh6%Zc^8'
    i = b'6oyZDr22E3ychjM%'
    cipher = AES.new(k, AES.MODE_CBC, i)
    padded_message = pad(encoded_hex, AES.block_size)
    return cipher.encrypt(padded_message)

async def GeNeRaTeAccEss(uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "User-Agent": await Ua(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_id": "100067"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as response:
            if response.status != 200: return None, None
            d = await response.json()
            return d.get("open_id"), d.get("access_token")

async def EncRypTMajoRLoGin(open_id, access_token):
    major_login = MajoRLoGinrEq_pb2.MajorLogin()
    major_login.event_time = str(datetime.now())[:-7]
    major_login.game_name = "free fire"
    major_login.client_version = "1.118.1"
    major_login.open_id = open_id
    major_login.access_token = access_token
    major_login.platform_id = 1
    major_login.client_ip = "127.0.0.1"
    # Basic required fields to avoid large proto block errors
    major_login.sys_comp_id = "1" 
    string = major_login.SerializeToString()
    return await encrypted_proto(string)

async def MajorLogin(payload):
    url = "https://loginbp.ggblueshark.com/MajorLogin"
    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 10;)",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB51"
    }
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers, ssl=ssl_context) as response:
            if response.status == 200: return await response.read()
            return None

async def DecRypTMajoRLoGin(data):
    proto = MajoRLoGinrEs_pb2.MajorLoginRes()
    proto.ParseFromString(data)
    return proto

async def GetLoginData(base_url, payload, token):
    url = f"{base_url}/GetLoginData"
    headers = {'Authorization': f"Bearer {token}"}
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers, ssl=ssl_context) as response:
            if response.status == 200: return await response.read()
            return None

async def DecRypTLoGinDaTa(data):
    proto = PorTs_pb2.GetLoginData()
    proto.ParseFromString(data)
    return proto

async def xAuThSTarTuP(target, token, timestamp, k, i):
    uid_hex = hex(target)[2:]
    ts = await DecodE_HeX(timestamp)
    enc_token = token.encode().hex()
    enc_pkt = await EnC_PacKeT(enc_token, k, i)
    pkt_len = hex(len(enc_pkt) // 2)[2:]
    
    header = "00000000"
    if len(uid_hex) == 9: header = "0000000"
    elif len(uid_hex) == 10: header = "000000"
    
    return f"0115{header}{uid_hex}{ts}00000{pkt_len}{enc_pkt}"

# --- TASKS ---

async def fast_emote_spam(uids, emote_id, k, i, r):
    print(f"Starting Spam: {emote_id}")
    for _ in range(25):
        for uid in uids:
            try:
                pkt = await Emote_k(int(uid), int(emote_id), k, i, r)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', pkt)
            except Exception as e:
                print(f"Spam Error: {e}")
        await asyncio.sleep(0.1)

# --- TCP CONNECTIONS (Clean Indentation) ---

async def TcPOnLine(ip, port, k, i, auth_token):
    global online_writer
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            online_writer = writer
            writer.write(bytes.fromhex(auth_token))
            await writer.drain()
            print("Connected to Online Server")
            
            while True:
                data2 = await reader.read(9999)
                if not data2: break
                
                # Group/Squad Logic - Fixed Indentation
                if data2.hex().startswith('0500') and len(data2.hex()) > 1000:
                    try:
                        # Corrected print statements and logic
                        raw_data = data2.hex()[10:]
                        packet = await DeCode_PackEt(raw_data)
                        print(f"Group Packet Received: {len(raw_data)}")
                        
                        packet_json = json.loads(packet)
                        OwNer_UiD, CHaT_CoDe, SQuAD_CoDe = await GeTSQDaTa(packet_json)
                        
                        # Join Chat
                        JoinCHaT = await AutH_Chat(3, OwNer_UiD, CHaT_CoDe, k, i)
                        if whisper_writer:
                            writer.write(JoinCHaT) # Sending to online writer sometimes needed for specific packets
                            await writer.drain()

                        msg = f'[B][C]{get_random_color()}\n- Bot Connected'
                        P = await SEndMsG(0, msg, OwNer_UiD, OwNer_UiD, k, i)
                        # Normally sent via chat writer, but sometimes mirrored
                        
                    except Exception as e:
                        print(f"Group Logic Error: {e}")

            writer.close()
            await writer.wait_closed()
        except Exception as e:
            print(f"Online TCP Error: {e}")
            online_writer = None
        await asyncio.sleep(2)

async def TcPChaT(ip, port, auth_token, k, i, login_data, ready_event, r):
    global whisper_writer, region
    region = r
    
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            whisper_writer = writer
            writer.write(bytes.fromhex(auth_token))
            await writer.drain()
            print("Connected to Chat Server")
            ready_event.set()
            
            # Clan Auth
            if hasattr(login_data, 'Clan_ID') and login_data.Clan_ID:
                print(f"Joining Clan Chat: {login_data.Clan_ID}")
                pk = await AuthClan(login_data.Clan_ID, login_data.Clan_Compiled_Data, k, i)
                writer.write(pk)
                await writer.drain()

            while True:
                data = await reader.read(9999)
                if not data: break
                
                # Chat logic placeholder
                # Removed complex logic to prevent indentation errors during copy-paste
                # app.py will handle commands via Telegram

            writer.close()
            await writer.wait_closed()
        except Exception as e:
            print(f"Chat TCP Error: {e}")
            whisper_writer = None
        await asyncio.sleep(2)

# --- MAIN EXECUTION ---

async def MaiiiinE():
    global key, iv, region, TarGeT, bot_uid
    
    # Credentials (replace if needed, but these match your logs)
    Uid = '4305911449'
    Pw = 'E02E1426DB672AF77AF0711890BC0EA9B6B2B3FDDE261C73ABBDECD73C0BD0F1'
    
    print("Generating Access Token...")
    open_id, access_token = await GeNeRaTeAccEss(Uid, Pw)
    if not open_id:
        print("Error: Invalid Credentials or Account Banned")
        return

    print("Performing Major Login...")
    pyl = await EncRypTMajoRLoGin(open_id, access_token)
    resp = await MajorLogin(pyl)
    if not resp:
        print("Error: Major Login Failed (No Response)")
        return

    auth = await DecRypTMajoRLoGin(resp)
    if not auth.token:
        print("Error: Login Failed (No Token)")
        return
        
    url = auth.url
    token = auth.token
    TarGeT = auth.account_uid
    bot_uid = TarGeT
    key = auth.key
    iv = auth.iv
    timestamp = auth.timestamp
    region = auth.region
    
    print(f"Logged In as UID: {TarGeT} | Region: {region}")

    login_data_raw = await GetLoginData(url, pyl, token)
    if not login_data_raw:
        print("Error: Failed to get Login Data")
        return
        
    login_data = await DecRypTLoGinDaTa(login_data_raw)
    
    online_ip, online_port = login_data.Online_IP_Port.split(":")
    chat_ip, chat_port = login_data.AccountIP_Port.split(":")
    
    auth_token_hex = await xAuThSTarTuP(int(TarGeT), token, int(timestamp), key, iv)
    
    ready_event = asyncio.Event()
    
    # Start Tasks
    task1 = asyncio.create_task(TcPChaT(chat_ip, chat_port, auth_token_hex, key, iv, login_data, ready_event, region))
    await ready_event.wait()
    task2 = asyncio.create_task(TcPOnLine(online_ip, online_port, key, iv, auth_token_hex))
    
    await asyncio.gather(task1, task2)

if __name__ == '__main__':
    # This block allows testing main.py directly
    asyncio.run(MaiiiinE())
					  
