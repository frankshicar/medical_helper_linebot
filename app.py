from flask import Flask, request, abort, send_from_directory
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
import mysql.connector
from linebot.models import *
from datetime import datetime, date, timedelta
import tempfile, os
import time
import traceback
import pymysql
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
# localhost接不上
# 設定 MySQL 連接資訊
db_config = {
    'host': 'localhost',
    'port' : 3306,
    'user': 'root',
    'password': 'frank0403',
    'database': 'testdbstupid',
    'charset': 'utf8'
}

# # 測試資料庫連接函數
# def test_database_connection():
#     try:
#         # 連接 MySQL 資料庫
#         connection = mysql.connector.connect(**db_config)
#         return connection
#     except Exception as e:
#         print(f"Error connecting to database: {e}")
#         return None


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('/Users/frankshi/Desktop/linbotTest', 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    
# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# def fetch_inspection_appointments():
#     try:
#         # 建立資料庫連接
#         connection = pymysql.connect(**db_config)
        
#         # 創建cursor對象
#         with connection.cursor() as cursor:
#             # SQL查詢語句，選擇inspection_appointment表中的所有記錄
#             sql = "SELECT * FROM inspection_appointment"
            
#             # 執行SQL語句
#             cursor.execute(sql)
            
#             # 獲取所有查詢結果
#             results = cursor.fetchall()
            
#             # 處理查詢結果
#             for row in results:
#                 print(row)  # 印出每一條記錄，您可以根據需要進行調整或處理這些數據
                
#         # 關閉資料庫連接
#         connection.close()
#     except Exception as e:
#         print(f"發生錯誤: {e}")
#         # 在這裡處理任何異常，例如資料庫連接失敗等

# # 調用函數進行數據查詢
# fetch_inspection_appointments()
# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    reference_date = date.today()
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            if msg == "最近就診預約":
                sql = "SELECT * FROM medical_appointment"  # 假設只查詢一條記錄作為示例
                cursor.execute(sql)
                results = cursor.fetchall()  # 假設只需要一條記錄
                formatted_records =[]
                
                one_month_ago = reference_date - timedelta(days=30)
                for record in results:
                    record_date = record[3]  # 假设 record[3] 已经是 datetime.date 类型
                    if record_date > one_month_ago:
                    # 格式化记录并添加到列表中
                        formatted_record = f"檢查項目：{record[2]}, 日期：{record[3]}, 報到位置：{record[4]}, 採檢前準備：{record[5]}, 採檢注意事項：{record[6]}, 可送檢時間：{record[7]}"
                        formatted_records.append(formatted_record)
                reply_text = "\n".join(formatted_records)

                # 回復整理後的資料
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
            
            if msg == "最近就診紀錄":
                sql = "SELECT * FROM medical_record"  # 假設只查詢一條記錄作為示例
                cursor.execute(sql)
                results = cursor.fetchall()  # 假設只需要一條記錄
                formatted_records =[]
                
                one_month_ago = reference_date - timedelta(days=30)
                for record in results:
                    record_date = record[5]  # 假设 record[3] 已经是 datetime.date 类型
                    if record_date > one_month_ago:
                    # 格式化记录并添加到列表中
                        formatted_record = f"就診科系：{record[2]}, 就診科別：{record[3]}, 醫師名稱：{record[4]}, 就診日期：{record[5]}, 是否需要回診：{record[6]}"
                        formatted_records.append(formatted_record)
                if not formatted_records:
                    reply_text = "在過去一個月內沒有就診紀錄。"
                else:
                    reply_text = "\n".join(formatted_records)

                # 回復整理後的資料
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
            
            if msg == "最近檢查/健檢預約":
                sql = "SELECT * FROM inspection_appointment"  # 假設只查詢一條記錄作為示例
                cursor.execute(sql)
                results = cursor.fetchall()  # 假設只需要一條記錄
                formatted_records = []
                
                for record in results:
                    record_date = record[3]  # 假设 record[3] 已经是 datetime.date 类型
                    if record_date > reference_date:
                        # 格式化記錄並添加到列表中
                        formatted_record = f"檢查項目：{record[2]}, 日期：{record[3]}, 報到位置：{record[4]}, 採檢前準備：{record[5]}, 採檢注意事項：{record[6]}, 可送檢時間：{record[7]}"
                        formatted_records.append(formatted_record)
                # 使用換行符將格式化後的記錄連接成一個字符串
                reply_text = "\n".join(formatted_records)

                # 回復整理後的資料
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
            
            if msg == "最近檢查/健檢紀錄":
                sql = "SELECT * FROM inspection_records"  # 假設查詢所有記錄
                cursor.execute(sql)
                results = cursor.fetchall()  # 獲取所有記錄

                # 初始化一個列表來保存格式化後的記錄
                formatted_records = []

                # 遍歷查詢結果，格式化每條記錄
                for record in results:
                    # 將每條記錄格式化為特定的字符串格式，這裡僅作為示例
                    formatted_record = f"檢查項目：{record[2]}, 日期：{record[3]}, 付款方式：{record[4]}, 狀態：{record[5]}"
                    formatted_records.append(formatted_record)

                # 使用換行符將格式化後的記錄連接成一個字符串
                reply_text = "\n".join(formatted_records)

                # 回復整理後的資料
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

    except Exception as e:
        print(f"發生錯誤: {e}")
        # 可以選擇回應錯誤信息給用戶
        # line_bot_api.reply_message(event.reply_token, TextSendMessage(text="發生錯誤"))


@handler.add(PostbackEvent)
def handle_postback(event):
    print(event.postback.data)

@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)
        
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)





# from flask import Flask, request, send_from_directory
# import os

# app = Flask(__name__)

# @app.route('/callback', methods=['POST'])
# def callback():
#     # 在這裡加入處理 POST 請求的邏輯
#     # 例如，解析和響應 LINE Bot 的數據
#     return 'Callback received', 200


# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory('/Users/frankshi/Desktop/linbotTest', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=80, debug=False)
