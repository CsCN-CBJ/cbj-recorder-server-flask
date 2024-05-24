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
    choice = request.args.get("choice")
    choice = "" if choice is None else choice

    # 在分类树中查找
    optionDict = ledgerOptions
    for c in choice:
        value = optionDict.get(c, "")
        if value == "" and c != DEF_OTHER:
            return make_response("invalid choice")
        # 如果是元组则说明有子节点. 否则就是叶子节点, 下一级选项为空
        optionDict = value[1] if isinstance(value, tuple) else {}

    # 从这一级的字典中提取出TEXT与VALUE(抛弃children)
    ret = [
        {OPTIONS_VALUE: k, OPTIONS_TEXT: v[0] if isinstance(v, tuple) else v}
        for k, v in optionDict.items()
    ]

    if len(ret) != 0:
        ret.append({OPTIONS_VALUE: DEF_OTHER, OPTIONS_TEXT: '其他'})
    return jsonify(ret)


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
    if len(choice) != DEF_CHOICE_LENGTH or choice == DEF_DEFAULT * DEF_CHOICE_LENGTH:
        return make_response("invalid choice")
    if amount == '':
        return make_response("invalid amount")

    sql.insertLedger(choice, amount, tags, comment)
    return make_response("success")


@app.route("/get/ledger", methods=["GET"])
def getLedger():
    """获取记录"""
    logger.info(f"get ledger: {request.args}")
    ledgers = sql.getLedger()
    ret = []
    for ledger in ledgers:
        ret.append([
            datetime.strftime(ledger[0], "%y%m%d:%H"),
            ledger[1],
            str(ledger[2]),
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
