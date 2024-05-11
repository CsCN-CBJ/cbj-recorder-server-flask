create table `tags`
(
    `tid`  int auto_increment primary key,
    `name` varchar(16) not null,
    `type` int         not null
);

create table `tagTime`
(
    `tid`  int      not null,
    `time` datetime not null
);

# 账单
create table `ledger`
(
    `id`      int auto_increment primary key,
    `time`    datetime   not null,
    `types`   varchar(8) not null,
    `tags`    varchar(64),
    `comment` varchar(64)
);

# 时间
create table `time`
(
    `id`      int auto_increment primary key,
    `time`    datetime   not null,
    `types`   varchar(8) not null,
    `tags`    varchar(64),
    `comment` varchar(64),

    `endTime` datetime
);

# 疾病
create table `disease`
(
    `id`       int auto_increment primary key,
    `time`     datetime   not null,
    `types`    varchar(8) not null,
    `tags`     varchar(64),
    `comment`  varchar(64),

    `duration` int,
    `severity` int
);

# 用药
create table `medicine`
(
    `id`      int auto_increment primary key,
    `time`    datetime    not null,
    `types`   varchar(8)  not null, # 用药部位
    `tags`    varchar(64),
    `comment` varchar(64),

    `name`    varchar(64) not null, # 药品不太好分类，所以直接用名字
    `dosage`  int
);


