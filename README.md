# readme

这是一个联机版的俄罗斯方块游戏

网络需要用NIO！

网络联机方案：
1.  客户端不进行任何计算，只是渲染。服务端维护board对象，接受客户端的输入，并且实时计算。
    好处是没有同步性问题，2边的画面一样。

2.  客户端维护board对象，服务端接受客户端输入和board对象，计算后返回结果。
    这个方案好像相比于1，并没有什么优点。CPU、内存、网络开销都没有改善，反而更复杂了

3.  客户分别处理自己的输入，然后计算结果。最后将结果发给对方，让对方渲染。
    好处是自己的游戏不会有延迟。如果2个玩家之间没有交互，则这个方案可行，否则的话
    会有数据同步行问题，除非加锁，否则无法实现。

TODO game_id和player_id
TODO 减小服务器和客户端交互频率
TODO 引入匹配机制
TODO 重构代码，使之更加模块化