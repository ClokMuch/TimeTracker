# 程序配置信息内容格式说明
```json
{
  "track_time": 30,                     // 统计周期 int ，单位为 秒 ，指定时间为间隔，进行一次统计
  "graph_time": 5,                      // 绘图周期 int ，单位为 次 ，指定次数的统计时间后，进行一次数据输出和绘图
  "period": 8,                          // 将指定天数之前的数据视为过期数据，将之压缩并保存在 sub_dir
  "output_dir": "V:\\TimeTracker\\",    // 统计结果输出的主目录
  "sub_dir": "storage\\",               // 过期数据储存目录
  "default_reminder_time": 0,           // 默认提醒器时间 int ，单位为 分钟 ，当不配置提醒器时间时，使用此处的时间
  "app_color": "#999999",               // 程序计时绘图的颜色
  "graph_font": "Sarasa Fixed Slab SC"  // 绘图使用的字体，若未安装此字体或显示异常时，可尝试调整为 "STSong"
}
```
