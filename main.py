from __future__ import (absolute_import, division, print_function, unicode_literals)

import backtrader

# step1: 布林通道 - 調整標準差大小預估股價的走勢
class BBands(backtrader.Strategy):
   params = (('BBandsperiod', 20),)  # 常用標準差20

   def __log(self, txt, dt=None):

      dt = dt or self.datas[0].datetime.date(0)
      print('%s, %s' % (dt.isoformat(), txt))

   def __init__(self):
      self.data_close = self.datas[0].close

      # To keep track of pending orders and buy price/commission
      self.order = None
      self.bar_executed = None
      self.redline = None
      self.blueline = None
      self.data_close = self.datas[0].close

      # Add a BBand indicator
      self.bband = backtrader.indicators.BBands(self.data_close, period=self.params.BBandsperiod)

   def notify_order(self, order):
      if order.status in [order.Submitted, order.Accepted]:
         return

      if order.status in [order.Completed]:
         if order.isbuy():
            self.__log("Buy Order executed; %s" % order.executed.price)
         elif order.issell():
            self.__log("Sell Order executed; %s" % order.executed.price)

         self.bar_executed = len(self)

      # Write down: no pending order
      self.order = None
      
# 對布林通道有研究的投資者可以自行更改喜愛的買賣依據
# 這裏我是使用突破中線或頂線作為買入點 /跌落中線為退出點
   def next(self):
      # Simply log the closing price of the series from the reference
      self.__log('Close, %.2f' % self.data_close[0])

      if self.order:
         return

      if self.data_close < self.bband.lines.bot and not self.position:
         self.redline = True

      if self.data_close > self.bband.lines.top and self.position:
         self.blueline = True

      if self.data_close > self.bband.lines.mid and not self.position and self.redline:  # 股價突破中線 = 買入點

         self.order = self.buy()
         self.buyPrice = self.data_close[0]

      if self.data_close > self.bband.lines.top and not self.position:  # 股價突破頂線 = 買入點2。0

         self.order = self.buy()
         self.buyPrice = self.data_close[0]

      if self.data_close < self.bband.lines.mid and self.position and self.blueline:  # 股價跌破中線 = 賣出點

         self.blueline = False
         self.redline = False
         self.order = self.sell()

          
 # step2: 和RSI一樣/加入數據、策略就可以進行模擬交易了
def main():
   # 1.資金
   startcash = 100000
   # 2. 股票/虛擬貨幣的歷史數據
   data = backtrader.feeds.YahooFinanceCSVData(dataname = './Data/TSLA.csv')
   # 3. 初始化你的AI
   cerebro = backtrader.Cerebro()
   # 4. 加入歷史數據
   cerebro.adddata(data)
   # 5. 加入寫好的交易策略
   cerebro.addstrategy(RSI)
   # 6. 加入準備號的資金
   cerebro.broker.setcash(startcash)
   # 7.交易量
   cerebro.addsizer(backtrader.sizers.FixedSize, stake=100)
   # 8.手續費
   cerebro.broker.setcommission(commission=0.007)
   # 7. 開始交易
   cerebro.run()





   portvalue = cerebro.broker.getvalue()
   pnl = portvalue - startcash

   print('Final Portfolio Value: ${}'.format(portvalue))
   print('P/L: ${}'.format(pnl))

   cerebro.plot()



if __name__ == '__main__':
   main()


