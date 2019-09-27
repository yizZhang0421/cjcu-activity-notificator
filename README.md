# 長榮大學 活動通知
長榮大學活動歷程：https://act.cjcu.edu.tw/ActiveSite/ActiveList.aspx</br>
利用網路爬蟲爬取新的活動並透過LINE機器人通知</br>
爬蟲與資料庫架在GCP的App engine和SQL</br>
</br>
[updater.py]</br>
thread每60秒爬一次，更新資料</br>
非截止就檢查是否存在資料庫</br>
不存在就新增並發廣播</br>
存在就更新status</br>
已截止就刪除資料庫中的資料</br>
</br>
[main.py]</br>
接收到數字就回傳數字頁的資料</br>
該頁為空則回傳"空頁"</br>
/db，可以得到資料庫的紀錄(json)</br>
