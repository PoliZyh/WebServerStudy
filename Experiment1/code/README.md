# web后端实验1--爬虫

## 实验1.统计亚运会关注人数最多的比赛

### 安装
npm i

### 执行
npm run dev

### 介绍
使用语言 Node.js 18.17.0
环境 MacOS 11.3.1
测试结果失败 -- 失败原因 -- 忘记考虑异步情况了
 
### 设计思路

``` js
/**
 * * 实现思路：
 * * 再爬去每日赛程界面，每日赛程界面的url变化的只有最后一级，比如2023-09-20或者2023-09-21(需要对date处理)
 * * 再爬去改界面下.wa-olympic-schedule-list-item类下的a标签身上的href属性，因为改属性指向直播间的界面
 * * 在前往直播间界面之前，需要将href的最后一级由数据改为聊天室(这么做之后聊天室标签上才会显示直播间人数)
 * * 最后爬去.text-position-talkroom标签中的Text文本即可爬到直播间人数
 * * 通过fs模块导出数据
 */
```

(1) 第一步使用cheerio爬取下来liveUlr数据结构为:

``` js
{
    2023-09-18: {
        url: [
            '//tiyu.baidu.com/major/matchDetail/Y2U1YzI1OWYyMWQ4MWU3NjI0NWY0ZjMwZGRkZmNjYmI%3D/tab/%E6%95%B0%E6%8D%AE',
            '//tiyu.baidu.com/major/matchDetail/NDg0ZGEwZmZjNWJkZTBhMjJiZDczYTQ3MzY2YmQ0ZDA%3D/tab/%E6%95%B0%E6%8D%AE',
            '//tiyu.baidu.com/major/matchDetail/MDgyMzU4MGQxMzU1MTU0NGMxMDRjYWRiY2E4NmQwMjg%3D/tab/%E6%95%B0%E6%8D%AE',
            '//tiyu.baidu.com/major/matchDetail/5Lqa5rSy6L%2BQ5Yqo5Lya55S35a2Q6Laz55CD6LWbIzIwMjMtMDktMTkj5pyd6bKcVTIzdnPkuK3lm73lj7DljJdVMjM%3D/tab/%E6%95%B0%E6%8D%AE',
            '//tiyu.baidu.com/major/matchDetail/5Lqa5rSy6L%2BQ5Yqo5Lya55S35a2Q6Laz55CD6LWbIzIwMjMtMDktMTkj5Lit5Zu9VTIzdnPljbDluqZVMjM%3D/tab/%E6%95%B0%E6%8D%AE',
            '//tiyu.baidu.com/major/matchDetail/5Lqa5rSy6L%2BQ5Yqo5Lya55S35a2Q6Laz55CD6LWbIzIwMjMtMDktMTkj5rKZ54m56Zisprit5ouJ5LyvVTIzdnPkvIrmnJdVMjM%3D/tab/%E6%95%B0%E6%8D%AE',
            '//tiyu.baidu.com/major/matchDetail/5Lqa5rSy6L%2BQ5Yqo5Lya55S35a2Q6Laz55CD6LWbIzIwMjMtMDktMTkj6Z%2Bp5Zu9VTIzdnPnp5HlqIHniblVMjM%3D/tab/%E6%95%B0%E6%8D%AE'
        ],
        names: ['篮球男子小组赛', '篮球男子足球赛'],
        len: 7
    }
}
```

(2) 第二步通过对每个url添加后缀 '直播间' 即 '%E8%81%8A%E5%A4%A9%E5%AE%A4' 和前缀 'https:' 得到亚运会直播间完整url

(3) 第三步使用puppeteer爬取直播间的人数
    遇到问题以及解决方案：
        a. 使用cheerio进行爬取，但是这个库爬取的是静态界面，导致直播间人数无法爬取到
        b. 使用puppeteer，但太慢了，使用Promise.all进行并发处理，结果导致内存占率99%程序崩溃
        c. 对puppeteer进行优化，包括对launch部分进行优化，但依旧很慢
        d. 使用generic-pool连接池对并发进行优化 --> 完美 参考文章：https://zhuanlan.zhihu.com/p/107800256

(4) 第四步对于爬取的数据继续进行数据修正将peopleCounts数据修正，当前维护的数据结构为
``` js
{
    '2023-09-28': {
    url: [
      'https://tiyu.baidu.com/major/matchDetail/Y2MyYzczN2JhMzNmMjkzZmY4N2U0YmRlMzliMDEwNDQ%3D/tab/%E8%81%8A%E5%A4%A9%E5%AE%A4',
      'https://tiyu.baidu.com/major/matchDetail/MzY5ZWYxM2JmMTc1YjlkNjVjMDVjZGYyOWE2Mzg2ZWI%3D/tab/%E8%81%8A%E5%A4%A9%E5%AE%A4',
      'https://tiyu.baidu.com/major/matchDetail/ZjFiZmVkZGJkZWJiZWRlYzk4OWI2ZmRmYzMyNWU5Mzc%3D/tab/%E8%81%8A%E5%A4%A9%E5%AE%A4',
      'https://tiyu.baidu.com/major/matchDetail/5Lqa5rSy6L%2BQ5Yqo5Lya55S35a2Q56%2Bu55CD6LWbI2Jhc2tldGJhbGwjMjAyMy0wOS0yOCPkuK3lm73lj7DljJd2c%2BS4reWbvQ%3D%3D/tab/%E8%81%8A%E5%A4%A9%E5%AE%A4',
      'https://tiyu.baidu.com/major/matchDetail/YjljZjg1YzdjYmJhNWMzNWY5MDMxMmRiNjdmMjhkNTk%3D/tab/%E8%81%8A%E5%A4%A9%E5%AE%A4',
      'https://tiyu.baidu.com/major/matchDetail/ODJlOTQ2MjllMGUwZmYzNzlhM2RiMTZkM2FkZjdjNGQ%3D/tab/%E8%81%8A%E5%A4%A9%E5%AE%A4',
      'https://tiyu.baidu.com/major/matchDetail/YWE1OWZkNDM0M2QwMDZhZWE1NTVkMjI3ZWM1ZDMxNWI%3D/tab/%E8%81%8A%E5%A4%A9%E5%AE%A4'
    ],
    names: [
      '游泳 女子200米蛙泳决赛',
      '游泳 男子200米蛙泳决赛',
      '街霸5 决赛BO3',
      '篮球 男子小组赛',
      '游泳 男子800米自由泳快组',
      '游泳 男子4×100米自由泳接力决赛',
      '游泳 女子4×200米自由泳接力决赛'
    ],
    len: 7,
    peopleCounts: [ '1.1万人', '1.4万人', '3.0万人', '7.5万人', '2.2万人', '3.6万人', '3.1万人' ]
  },
  ...
}
```

(5) 对每天的数据进行比较得到直播间人数最多的索引
    考虑：
        a. 比较人数 '1.1万人' 和 '7038人' 无法直接进行比较，需要进行一步转换
        b. 如果有相同的人数，那样无法比较出谁是最多的，应当全部保留，设计一个存储人数最多的索引数组如下
```js 
{
    '2023-09-28': {
        ...,
        mostIndexes: [0, 3] 
    }
}
```

(6) 使用fs模块对数据进行导出



