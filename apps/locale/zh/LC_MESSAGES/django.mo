��    @        Y         �  $   �     �     �     �  L   �  	   E     O     T  F   [  G   �     �     �  9   �     -     :  �   @     �  
   �     �  E   �     #     '     G     Y     j     ~     �     �     �     �     �     �     	     
	     	     4	     J	     \	     d	     ~	     �	     �	     �	     �	     �	     �	     �	      
     
     $
     1
     C
     Y
     m
  	   �
     �
     �
     �
     �
     �
     �
     �
  
     M    ?   a  *   �  B   �  6     c   F     �     �  	   �  6   �  w   �     q     x  >   |     �     �  �   �  	   X  	   b     l  N   s     �     �  0   �  b     *   p  G   �     �     �     	  �        �  F   �  	   )    3  $   8  S   ]  4   �     �     �  L     !   U  0   w     �  1   �  B   �  	   0  g   :  (   �     �     �  �   �  B   �       3     J   F     �  %   �    �  >   �       /   7  ]   g  (   �        
       /   =   (      >   *         )   6   3              <           ,                       @         ?               	          $                   '                  #       2   &       ;                   %   !   1       9                     0   5   -   7      :   .   4      8          "                     +    %(username)s's order items has error %(username)s_amount_invalid %(username)s_not_allowed %(username)s_order_not_found Address: %(address)s, Phone: %(phone)s, Remark: %(remark)s, Total: %(total)s Breakfast Code Driver Hi, %(username)s! Sorry, you are not allowed to run this command here. Hi, %(username)s! You book meal successfully! You can continue to book. Lunch No Order ID: %(orderid)s, Date: %(orderdate)s, Order detail: Order Status Price Recharge successfully! Username: %(username)s, old_balance: %(old_balance)s, current_balance: %(current_balance)s, diff: %(diff)s Remarks: Store Name Supper Transfer successfully! from: %(from)s, to: %(to)s, amount: %(amount)s Yes You can't transfer to yourself! already_discarded an_order_is_open cancel_order_failed cancel_order_success cannot_be_closed cannot_be_discarded cannot_be_refunded cannot_close_order close_order_fail close_order_success closed create_order_success discard_order_failed discard_order_success format_is_invalid invalid jumpserver_notice_success jumpsever_bind_error last_five_orders_info not_supergroup nothing_is_found notice_failed notice_success open open_order_not_found order_is_empty order_item_not_found params_error product_list_hint product_not_available remove_item_success reply_to_sending_photo say_hello store_not_available tele_got_nothing tele_help_message tele_invalid_message too_short_message unkown_error unkown_message uuid_error Project-Id-Version: Jumpserver 0.3.3
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2017-09-28 07:10+0800
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: ibuler <ibuler@qq.com>
Language-Team: Jumpserver team<ibuler@qq.com>
Language: zh_CN
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
 %(username)s的订单存在错误，导致订单无法关闭。 %(username)s，您输入的数量不正确 对不起，%(username)s，您在这里没有权限执行此操作 对不起，%(username)s，没有发现您的订单！ ------------------
地址：%(address)s 
电话：%(phone)s 
备注：%(remark)s
总额：%(total)s 早餐 编号 老司机 您好，%(username)s！您没有权限执行此操作 您好，%(username)s！点餐成功，您还可以继续选择！如果选错了，您可以用/cancelmyorder来取消 午餐 否 订单ID：%(orderid)s 
时间: %(orderdate)s 
订单详情： 订单状态 价格 操作成功！用户名：%(username)s，充值前余额：%(old_balance)s，当前余额： %(current_balance)s，变化额：%(diff)s 备注： 商户名 晚餐 转账成功！转账人：%(from)s，收款人：%(to)s，金额：%(amount)s 是 老铁，你想多了 该订单已经被废弃，不能重复操作。 您有一个订单未关闭，创建新订单前，请使用/closeorder+订单ID命令将其关闭 对不起，订单已关闭，无法取消 订单取消成功，钱已饭还您可以通过/balance来查看余额 订单不能关闭 订单不能废弃 订单不能退款 暂时不能关闭订单，因为有人选错了菜，请检查订单信息重点检查总金额为0的订单它可能多选了或少选了菜品，请与商家定价策略对比 订单关闭失败 订单已关闭，您可以使用命令/lastorder来查看订单信息 已关闭 餐车已启动，各位小伙伴请上车，Dididi...
您可以使用命令/pick+菜ID+数量来点菜, /productlist命令会告诉您哪些菜可选。
当然，如果您不喜欢使用命令，您也可以使用交互式点餐法，直接@我。Just try it! 订单废弃失败，钱暂未退回 该订单废弃成功，钱已返还给用户。使用/balance查看余额信息。 格式不正确, 键入/help命令获取帮助信息 无效 开启telegram通知成功 当前telegram账户已经绑定了一个jumpserver账户,不能重复绑定 最近五个订单信息如下： 当前群组不是超级用户群，请先升级 什么也没找到 通告发送失败！联系管理员@seven_old。 操作成功！已经向所有群组发送了您的通告消息。 开放中 没有开放的订单，所有订单都已经关闭。您可以使用/orderhistory查看订单信息。 订单是空的，暂时没人下单哦~ 没有找到这个小项 参数错误 -----------------------------------------
您可以使用命令: /pick 菜ID 数量 来点菜，
如果你想一下子选择多个菜，你可以这样做：/pick 菜一ID 数量 and 菜二ID 数量 and... 您现在不能选这个菜，请用/productlist查看可选的菜 删除成功！ 感谢您给我发照片，我会好好保管的～ 您好！我是您的订餐助理，请输入/help来查看帮助信息。 餐车尚未启动 Sorry, 我什么也没能为您找到 帮助文档
您可以使用下面这些命令：
    /pick -点菜，必须加上两个参数：菜ID和数量
		例1：/pick 7 1
		例2：/pick 7 1 and 2 1 and 3 1 
    /cancelmyorder-取消订单
    /balance -查看余额
    /productlist -查看可选菜
    /lastorder -显示最新订单
以下命令仅供司机使用:
    /openorder -创建订单
		例：/openorder 7
    /closeorder -关闭订单
    /recharge -充值或扣款
		例： /recharge annwith 1000 
    /orderhistory-查看最近5个历史订单
    /discardorder-翻车，订单作废，退款
		例： /discardorder 7
    /notice-发送消息通知
    /help -显示本条信息
点餐流程介绍：
    1：司机使用/openorder+ID命令创建订单
    2：组员开始点菜
    3：司机/closeorder关闭订单，发车

点餐方法介绍：
    一、图形界面交互式
        1.输入@AnnWithBot
        2.等待几秒...
        3.根据提示选择
    二、命令式
        使用/pick命令
如有疑问，请联系：@seven_old, +63 09451297411 您的输入无效，键入/help命令获取更多帮助信息 消息不能少于10个字符 咦，一不小心出错了~ 请联系管理员 对不起，这类消息我暂时处理不了，不过我会努力变得更聪明的，嘻嘻 您的UUID不正确，请联系管理员 