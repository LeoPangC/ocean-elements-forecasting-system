# ocean-forecasting-black-box
可移动轻量级海洋要素预测程序

要素包括：海洋表面温度、海洋表面盐度、风场、流场、浪高

预测区域：
        
        风浪：r1:lat[18.5,22],lon[116.5,120],r2:lat[19.5,23],lon[121.5,125]
        
        温盐流：r1:lat[15,18.5],lon[110.5,114],r2:lat[18,21.5],lon[111.5,115]
        
预测时间：8个时间点预测3小时，执行自回归
