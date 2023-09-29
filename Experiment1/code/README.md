# web后端实验1--爬虫

## 实验1.统计亚运会关注人数最多的比赛

### 执行
npm run dev

### 介绍

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
第一步爬取下来liveUlr数据结构为:
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
通过对每个url添加后缀 '/直播间' 即 '%E8%81%8A%E5%A4%A9%E5%AE%A4'



