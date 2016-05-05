Reclaim [ ![CI Releases](https://img.shields.io/github/release/hlaspoor/Reclaim.svg)](https://github.com/hlaspoor/Reclaim/releases)
=============
一个可以帮助你更有效的找到可用 Google IP 的工具

![](https://raw.githubusercontent.com/hlaspoor/DocImages/master/images/Relaim_Screen_Shot.png)

使用方法
-------------
1. 在core文件夹下执行
  ````python start.py````
2. 打开浏览器，访问 http://127.0.0.1:9494

操作说明
-------------
### INPUT（对IP段进行操作）
* 首先你需要导入一些用于搜索的IP段，怎么导入呢？你有两种选择。
  * 通过拷贝IP段的文本到右侧的文本框中，点 **IMPORT** 导入按钮。
  * 通过拷贝IP结果到右侧的文本框中，点 **IMPORT** 导入按钮。
* 导入了IP段之后，表格中就会显示已经导入的IP段，这时你就可以选中要搜索的IP段，点右上角的 **SEARCH** 搜索按钮对选中的IP段进行搜索。
* 在搜索过程中你也可以点右上角的 **CANCEL** 取消按钮取消搜索。
* 在搜索完成之后，IP段的表格中会更新显示IP段搜索到的IP数量。如果IP数量大于0你就可以看下面OUTPUT部分的操作了。

### OUTPUT（对IP搜索结果进行操作）
* 如果在 INPUT 中对IP段的状态进行更新的时候搜索到了IP，那么在 OUTPUT 的表格中就会显示已经搜索到的IP。
* 点右侧的 **EXPORT** 导出按钮可以导出IP到右侧的文本框中。

其他说明
-------------
* 关于 SAVE 保存操作
  * 这个工具会产生一个 range_db.json 的文件，保存表格中所有IP段的搜索结果。
  * **保存操作是不可逆的**，如果你删除了表格中的所有IP段，点了保存的OK项，**range_db.json文件就被清空了**！
* 关于 RELOAD 重新加载操作
  * 重新加载 range_db.json 文件中的数据到表格中，比如你删除了所有的IP段并且没有保存，你点 **RELOAD**  按钮之后 range_db.json 文件中的数据都会被重新加载到表格中。
* 关于 NEVER 列
  * 当一个IP段被添加到表格中之后, NEVER 列默认值为 Y. 表示这个IP段从来没有搜索出可用的IP。如果IP段搜索出来了IP，那么 NEVER 列的值会变为 N.。
  * NEVER 列的作用在于标示这个IP段是否从来没有搜索出过可用的IP。比如一个IP段的 NEVER 列是 N.，但是搜出的IP总数是0，则表示这个IP段曾经搜出过IP，只是现在没有可用IP而已。但是如果 NEVER 列是 Y. 搜索出的IP总数是0，则表示这个IP段从来都没有搜索出过有用的IP。
