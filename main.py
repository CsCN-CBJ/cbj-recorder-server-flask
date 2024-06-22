from datetime import datetime
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from config import *
import localConfig
import logging
from cbjLibrary.log import initLogger
from sqlUtils import RecorderSql
from options import *

app = Flask(__name__)
CORS(app, supports_credentials=True)

baseLogger = initLogger(LOG_PATH, BASE_LOGGER_NAME)
logger = logging.getLogger(API_LOGGER_NAME)
sql = RecorderSql(logging.getLogger(STORAGE_LOGGER_NAME))


def verifyToken(func):
    """验证POST的token"""

    def wrapper(*args, **kwargs):
        token = request.json.get(VERIFICATION_COOKIE_NAME)
        logger.info(f"function: {func.__name__}, token: {token}")
        if token is None or token != localConfig.LOGIN_PASSWD:
            return make_response("verification failed")
        return func(*args, **kwargs)

    return wrapper


@app.route("/options", methods=["GET"])
def getOptions():
    """获取所有选项"""
    # 获取前序选项
    logger.info(f"get options: {request.args}")
    return jsonify(ledgerOptions.getList())


@app.route("/tags", methods=["GET"])
def getTags():
    """获取所有标签"""
    logger.info(f"get tags: {request.args}")
    ret = sql.getTags(1)
    return jsonify(ret)


@app.route("/ledger", methods=["POST"])
@verifyToken
def addLedger():
    """记录"""
    logger.info(f"add ledger: {request.json}")
    choice = request.json.get("choice")
    amount = request.json.get("amount")
    tags = request.json.get("tags")
    comment = request.json.get("comment")
    if choice is None or amount is None or tags is None or comment is None:
        return make_response("missing arguments")
    choice = str(choice)
    if len(choice) != DEF_CHOICE_LENGTH or choice == DEF_DEFAULT * DEF_CHOICE_LENGTH\
            or ledgerOptions.getChild(choice.strip(DEF_DEFAULT)) is not None:
        return make_response("invalid choice")
    if amount == '':
        return make_response("invalid amount")

    sql.insertLedger(choice, amount, tags, comment)
    return make_response("success")


@app.route("/get/ledger", methods=["GET"])
def getLedger():
    """获取记录"""
    logger.info(f"get ledger: {request.args}")
    status = request.args.get("status")
    if status is None or not 1 <= int(status) <= 3:
        return make_response("invalid status")
    status = int(status)
    ledgers = sql.getLedger(status)
    ret = []
    for ledger in ledgers:
        ret.append([
            datetime.strftime(ledger[0], "%m%d%H"),
            ledger[1].split(DEF_DEFAULT)[0],  # 去掉占位符
            str(ledger[2]).rstrip('0').rstrip('.'),  # 去掉多余的0和小数点
            ledger[3],
            ledger[4],
        ])
    return jsonify(ret)


@app.route("/login", methods=["POST"])
def login():
    """登录"""
    logger.info(f"login: {request.json}")
    passwd = request.json.get("passwd")

    if passwd == localConfig.LOGIN_PASSWD:
        resp = make_response("success")
    else:
        resp = make_response("failed")
    return resp


app.run(localConfig.APP_HOST, localConfig.APP_PORT, ssl_context=(localConfig.SSL_CRT, localConfig.SSL_KEY))
sql.close()
