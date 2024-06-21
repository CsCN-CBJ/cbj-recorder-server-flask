from cbjLibrary.cbjSqlFunc import MysqlConnector
from config import *
from localConfig import USER, PASSWORD, HOST, DATABASE
import logging


class RecorderSql:

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.sql = MysqlConnector(HOST, USER, PASSWORD, DATABASE, logger)

    def close(self):
        self.sql.CloseMysql()

    def insertLedger(self, choice: str, amount: str, tags: str, comment: str):
        """
        插入账单
        """
        self.logger.info(f"Insert ledger: {choice}, {amount}, {tags}, {comment}")
        # 插入账单
        self.sql.Execute(
            f"INSERT INTO `ledger` (`types`, `amount`, `tags`, `comment`, `time`) "
            f"VALUES ('{choice}', {amount}, '{tags}', '{comment}', NOW())"
        )

        # 插入标签
        self.insertTags(tags, 1)

    def getLedger(self, status: int):
        """
        获取账单
        status: 1-3
        1: 限制10条
        2: 一个月
        3: 所有
        """
        self.logger.info(f"Get ledger")
        sql = "SELECT `time`, `types`, `amount`, `tags`, `comment` FROM `ledger` "
        if status == 1:
            sql += "ORDER BY `time` DESC LIMIT 10"
        elif status == 2:
            sql += "WHERE time > DATE_SUB(NOW(), INTERVAL 1 MONTH) ORDER BY `time` DESC"
        elif status == 3:
            sql += "ORDER BY `time` DESC"
        else:
            self.logger.error(f"Invalid status: {status}")
            return None
        return self.sql.Select(sql)

    def insertTags(self, tags: str, tagType: int):
        """
        插入标签
        """

        def getTagId(tagName):
            ret = self.sql.Select(f"SELECT `tid` FROM `tags` WHERE `name`='{tagName}' and `type`='{tagType}'")
            if len(ret) == 0:
                return None

            if len(ret) > 1:
                self.logger.fatal(f"Tag {tagName} has more than one tid: {ret}")
            return ret[0][0]

        # 分割标签并分别进行处理
        if tags is None or tags == "":
            return
        tagList = tags.split(DEF_TAG_SEP)
        for tag in tagList:
            tag = tag.strip()
            tid = getTagId(tag)
            if tid is None:
                # 新标签需要插入
                self.sql.Execute(f"INSERT INTO `tags` (`name`, `type`) VALUES ('{tag}', {tagType})")
                tid = getTagId(tag)

            if tid is None:
                self.logger.error(f"Insert tag {tag} failed")
                return

            # 记录标签使用时间
            self.sql.Execute(f"INSERT INTO `tagTime` (`tid`, `time`) VALUES ({tid}, NOW())")

    def getTags(self, tagType: int):
        ret = self.sql.Select(f"SELECT `name` FROM `tags` where `type`={tagType}")
        self.logger.info(f"Get tags: {ret}")
        return list(map(lambda x: x[0], ret))
