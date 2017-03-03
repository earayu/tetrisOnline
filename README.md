# readme

这是一个联机版的俄罗斯方块游戏

网络联机方案：
1.  所有客户端把输入传送到服务器，服务器计算后返回模型给客户端，然后客户端渲染
    好处是客户端同步性好，但服务器还得计算一下，而不是简单的转发

2.  P2P方式，客户分别处理自己的输入，然后计算结果。最后将结果发给对方，让对方渲染。
    好处是自己的游戏不会有延迟，但可能会造成2边渲染结果不一致

