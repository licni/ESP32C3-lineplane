// 版本流水號: r75 (2026-09-15) 安全審查:油門 0% 脈寬要先勾「螺旋槳已拆除」才能改並加警語;起飛油門超出上下限時時間軸文字提示;
//   新錯誤碼 startbusy/cancelstate,startblock 文字改成「剛取消或剛停止馬達」;拒絕原因 10 電變輸出沒訊號;事件 28/6
// 舊: r74 (2026-09-15) 頁尾 SuperGG 七彩霓虹動畫(GG):字母各一段彩虹漸層,色相輪轉光暈,波浪跳動,兩側星星閃爍;減少動態效果時停止;
//   拉桿/勾選框/進度條 accent-color 改主色(瀏覽器預設藍)
// 舊: r73 (2026-09-15) 暖色系主題(GG:藍色對眼睛不好):主色藍 → 焦橙(深色模式亮橙),底色/文字/框線改米白與咖啡色系,新增 --accentBg;
//   降落狀態列藍 → 棕;角度補償死區,時間軸第二段/換段,監看頁第二段曲線,紀錄頁角度/抖動線條換成暖色,文字說明跟著改;頁尾漸層去掉紫色;
//   連結與文字選取反白也改主色(瀏覽器預設是藍色)
// 舊: r72 (2026-09-15) 備份頁外觀(GG):計時器風格加藍色粗框淺藍底,按鈕加大加粗,說明收進 ⓘ;其他設定改小方塊一行兩個(名稱 + ⓘ 展開說明,WiFi 標 ⚠);
//   取消的項目拿掉刪除線,只變灰打 ✕
// 舊: r71 (2026-09-15) 套用備份碼可取消項目(GG):檢查通過後列出碼裡的風格(顯示碼裡的名稱)與分區,預設全亮,點一下變灰打 ✕ 加刪除線;
//   套用帶 sel/sec,結果寫出已套用與取消沒套用的項目;分區說明分成產生時/套用時的建議
// 舊: r70 (2026-09-15) 備份獨立分頁(GG):產生卡(六組風格 + 起飛降落與安全/安裝/電變/WiFi 各自勾選,每項說明包含什麼,全選/只選測試/全部取消)
//   與套用卡分開,顯示碼裡的內容與 WiFi 已存提示;設定頁移除備份卡;分頁列改兩行(一行 5 個)不橫捲
// 舊: r69 (2026-09-15) 設定備份碼選組(GG):六組風格按鈕點亮要包含的組(預設只選測試,全選/只選測試),產生帶 sel,
//   貼上檢查與套用顯示碼裡包含哪幾組;計時器頁「測試」組改名欄停用(namelocked)
// 舊: r68 (2026-09-15) 角度補償圖:「機頭朝上」移到直軸 +90° 上方,拿掉角落段別文字,圖高回 366(基本油門標籤縮成一排);
//   第一段/第二段按鈕加強(整列等寬,粗框,大字);刪除「編輯「…」· 飛行使用中」文字(GG)
// 舊: r67 (2026-09-15) 角度補償圖:基本油門標籤移到圖框外上方(圖高 366 → 398);紅色「目前」文字跟著紅線與曲線交點移動(GG)
// 舊: r66 (2026-09-15) 系統頁家用 WiFi 欄位寫清楚:標籤「家用 WiFi 名稱(SSID)」「家用 WiFi 密碼」,SSID 說明(大小寫要一樣,只支援 2.4GHz,不支援隱藏名稱)(GG);
//   自身熱點(名稱,密碼)與家用 WiFi(SSID,密碼)各自框成一組並加小標題(GG)
// 舊: r65 (2026-09-15) 時間軸圖分段名稱從 X 軸下方移到圖內下方兩排交錯,不補償標籤第三排;上下限數值改寫在顏色說明;圖高 214 → 194(GG:X 軸文字重疊)
// 舊: r64 (2026-09-15) 時間軸圖每段不同底色(緩啟動/起飛油門/第一段/換段/第二段/降落),不補償改斜線並標秒數,圖下方加顏色說明(GG);拿掉淡綠補償範圍
// 舊: r63 (2026-09-15) 計時器頁起飛區加起飛油門與持續時間(時間軸圖多一段「起飛」,時間軸文字,監看頁「起飛油門」,馬達啟動事件);
//   系統頁 WiFi 卡加熱點密碼欄(可改,顯示/隱藏,儲存後提示新密碼),說明文字改成出廠 12345678 可改
// 舊: r62 (2026-09-15) 曲線朝上點數/朝下點數各自加圓角框(GG:標籤和選單離得遠,看不出是一組)
// 舊: r61 (2026-09-14) 補速/減速起點(死區邊界)的點改成實心小點(半徑 5 空心 → 3 實心),和可拖的空心點區分(GG)
// 舊: r60 (2026-09-14) 曲線點縮小:半徑 9/選取 11 → 6/7.5,框線 3 → 2.2(GG:太肥),觸控範圍維持半徑 20
// 舊: r59 (2026-09-14) 曲線拖曳放開:角度與補償一次送出(setmany),拖曳中與送出中不讓讀回的舊設定覆蓋畫面(GG:放開瞬間點先跳回原位)
// 舊: r58 (2026-09-14) 停用安全開關(GG):設定頁風險說明 + 三項打勾才送出,每一頁上方紅色警告列(狀態 asoff),監看頁開關顯示已停用,事件 28/5
// 舊: r57 (2026-09-14) 手動上傳韌體:選檔後找身分標記,不是這個控制器的韌體就不讓上傳,是的話顯示版本比目前新/相同/舊(允許退回舊版)
// 舊: r56 (2026-09-14) 設定頁「設定備份碼」卡片(產生並複製,貼上即檢查,套用,清空;未儲存時停用);安裝頁「蜂鳴器」電位切換;
//   曲線點拖曳改用總油門 10%~100% 夾(GG:基本油門 70% 時只能拉到 20%),補償值 ±100;未儲存判斷含備份碼套用的飛行風格;
//   出廠值改成 GG 基準設定後的說明文字(校正保持 3 秒,PWM 100Hz,轉速回傳出廠開啟);降落保險時間說明改成從減力走完才算
// 舊: r55 (2026-09-14) 安全開關等待上限(GG):設定頁參數(分鐘),狀態列剩餘時間與逾時取消,事件 28/3,28/4;
//   校正保持秒數說明(出廠 4 秒,電變開機時間);韌體更新只在網站版本比較新時提示(板子 .12 網站 .11 卻說有新版本);
//   參數單位欄最小寬度 18 → 27px(兩個字的單位「分鐘」「公尺」那列輸入框原本往左偏,和上下列沒對齊)
// 舊: r54 (2026-09-14) 安全開關改成「起飛程序照常開始,按下才倒數」(GG):狀態列等待安全開關,事件 28,監看頁開關文字,說明文字
// 舊: r53 (2026-09-14) 韌體更新說明改清楚:開著的網頁自動確認(不用按按鈕),寫上由網頁確認的理由(GG)
// 舊: r52 (2026-09-14) 校正旗標時效 10 秒:按鈕旁醒目注意,步驟與提示文字,倒數秒數(GG)
// 舊: r51 (2026-09-14) 撞擊斷電後推飛機不啟動的文字(原因 9);校正旗標時效顯示,事件 26;WiFi 試用延後事件 27;下限拖曳最低 10%;發射功率與保持被拒時提示
// 舊: r50 (2026-09-14) 安全開關 GPIO21:狀態列與監看頁顯示,拒絕原因 7/8 文字
// 舊: r49 (2026-09-14) 新韌體確認時限說明 5 分鐘 → 1 分鐘,提醒更新時保持網頁開著
// 舊: r48 (2026-09-14) 修正:按「檢查更新」後有時一直停在「檢查中…」(檢查狀態改變就重讀)
// 舊: r47 (2026-09-14) 韌體更新卡(檢查更新,新版說明,按兩下安裝,進度,新韌體自動確認,已退回提示,手動上傳收合);頁首更新中提示;
//   事件 25,拒絕原因 5/6;上電後直接倒數只給拔電再接電的文字(解鎖事件 arg 3)
// 舊: r46 (2026-09-14) 版面重整(GG):置頂列壓扁且八個分頁不用橫捲;卡片說明收進標題 ⓘ;參數列與數值方塊緊湊;ⓘ 說明重寫;
//   計時器三張參數卡併一張(含時間軸圖),角度補償併入風格選擇,安裝/電變移除純說明卡,校正步驟與廠牌說明預設收起,系統頁韌體與裝置資訊併卡. 功能與元素 id 不變
// 舊: r45 (2026-09-14) 參數 +/− 改成兩顆:按一下走一格細調,按住連續加速(約 2 秒後粗調),放開才送出;按鈕連點不再變成雙擊放大(GG)
// 舊: r44 (2026-09-14) WiFi 設定保護:頁首「保持」提示列(功率試用 15 秒 / 設定試用 3 分鐘),系統頁說明保護與開關電救援,事件 24
// 舊: r43 (2026-09-14) 手勢說明改成預設收起,點標題展開(GG)
// 舊: r42 (2026-09-14) 曲線圖雙指手勢全交給瀏覽器(沒放大也能捏合放大,放大後雙指拖動網頁),單指不捲頁只靠 touch-action;圖旁加手勢說明框
// 舊: r41 (2026-09-14) 曲線圖觸控:單指拖曲線不捲頁,雙指縮放(touch-action:pinch-zoom)與雙指移動網頁;第二指放上或瀏覽器接手時取消拖曳不送出
// 舊: r40 (2026-09-14) 油門上下限從計時器頁搬到角度補償頁撞牆檢查下方,預設收起可展開(GG)
// 舊: r39 (2026-09-14) 角度補償圖高度 548 → 366(禁止捲頁後太高,GG)
// 舊: r38 (2026-09-14) 角度補償圖整區不捲動網頁(GG);數值框空白/非數字不送出並顯示回實際值,被拒絕後也換回實際值,Enter 送出
// 舊: r37 (2026-09-14) 狀態列「開始起飛程序」按鈕(待機/結束且手勢開啟時出現,按兩下確認);事件 3 來源 2 = 網頁
// 舊: r36 (2026-09-13) 系統頁熱點名稱:固定開頭 + 可改後綴(即時預覽,位元組上限),熱點密碼標明固定;家用 WiFi 欄位改名清楚
// 舊: r35 (2026-09-13) 頁尾作者:設計開發者 SuperGG(漸層大字)· Line 社群 RotorFlightTW
// 舊: r34 (2026-09-13) 收輪行程說明標出廠預設 1400/1600
// 舊: r33 (2026-09-13) 安裝頁「機輪收腳」卡(開關,收輪秒數,速度,行程,方向,試收輪,提早降落開啟警示);事件 23 收放輪;計時器頁時間軸文字加收輪
// 舊: r32 (2026-09-13) 觸地提早降落關閉時收起抖動門檻/持續秒數/水平容許角度/啟用秒數與即時抖動列(GG)
// 舊: r31 (2026-09-13) 「風格」分頁改名「計時器」(GG),指向該頁的說明文字一併改
// 舊: r30 (2026-09-13) 感測器故障鎖定到重新上電的文字;外力事件改顯示門檻,繼續倒數時顯示外力最大值;事件 22(測試用模擬)
// 舊: r29 (2026-09-13) 倒數中角度超過水平限制取消:狀態列,結束原因 9,事件紀錄第 21 種;r28:
// 舊: r28 (2026-09-13) 起飛前水平限制:設定頁參數,狀態列「等待放平」,拒絕原因與事件紀錄(含角度);r27:
// 舊: r27 (2026-09-13) 暗色模式數值框可讀性(給文字色,底色,框線;宣告 color-scheme 讓原生控制項跟著變暗);r26:
// 舊: r26 (2026-09-13) 未儲存提示併入第一行(取代標題,第一行固定 48px 不換行),出現時不再把下面的欄位往下推;r25:
// 舊: r25 (2026-09-13) 電變頁轉速回傳開關與馬達極數(只在 DShot300 顯示),即時轉速與回傳成功率,收不到回傳警告;監看頁電變輸出加轉速;r24:
// 舊: r24 (2026-09-13) 扭轉機尾取消起飛:設定頁兩項(手勢關閉時隱藏),狀態列顯示扭轉角度與封鎖倒數,事件紀錄;r23:
// 舊: r23 (2026-09-13) 監看頁事件紀錄(通電後秒數,原因與數值,排查方向;觸地提早降落/馬達停止標色);r22:
// 舊: r22 (2026-09-13) 電變頁加「各廠牌校正說明」(19 組,步驟/注意/自動精靈建議秒數/查證程度/官方出處,依查證紀錄檔);r21:協定選項改 PWM / DShot150 / DShot300(拿掉 600);r20:PWM 頻率可調(50~400Hz,DShot 時隱藏);r19:電變頁加輸出協定(PWM/DShot300/600,開機套用中 vs 設定,重新開機套用),DShot 時手動輸出顯示 DShot 值,校正精靈標示不需要
// 舊: r18 (2026-09-13) 新增「電變」分頁:電變脈寬(由安裝頁移來),手動輸出滑桿(螺旋槳確認,解鎖從最低開始,0.2 秒心跳,離頁/切 App 上鎖),電變校正精靈(下次通電校正旗標與狀態)
// 舊: r17 (2026-09-13) 監看頁油門曲線第二段改黃色,曲線說明分兩行移到左上
// 舊: r16 (2026-09-13) 修正後視圖滾轉方向畫反(左翼抬起圖上卻往下);r15 內容見下
// 舊: r15 (2026-09-13) 安裝頁感測器方位加側視/後視圖(跟著感測器即時轉,箭頭標目前選的晶片軸),標出廠預設值與「安裝方位回預設」;角度補償第二段可拖基本油門把手(與風格頁連動),曲線仍不能改
// 舊: r14 (2026-09-13) 刪除第二段曲線設定(第二段只顯示),撞牆檢查(圖上紅線+區間列表);監看頁姿態圖加背景油門曲線與目前角度紅線
// 舊: r13 (2026-09-13) 風格頁時間軸畫成圖(分段寬度有最小值,邊界標實際時間,三種換段線形,上下限與補償範圍,不補償時段,等觸地),文字保留
// 舊: r12 (2026-09-13) 新增「安裝」分頁:感測器安裝方位,飛行速度,電變脈寬(前期設定,設好少變;之後電變協定也放這裡)
// 舊: r11 (2026-09-13) 飛行狀態列加強視覺(狀態徽章,色邊,倒數實心底+大字+進度條+脈動,飛行綠/降落藍/撞擊紅實心);外力門檻與手勢力道即時指示燈(目前值與 3 秒最大)
// 舊: r10 (2026-09-13) 第二段獨立補償曲線+由第一段複製;參數列緊湊化(名稱與按鈕同列,說明收進 ⓘ,換算值放名稱下)
// 舊: r9 (2026-09-13) 角度補償圖形化曲線:實際油門橫軸/角度直軸,上下限灰區與夾限曲線,基本油門標籤,目前角度紅線與飛機圖示,邊框把手(死區/下限/基本/上限)可拖,點可點選拖曳(亮紅光暈),右側選取面板粗細調;第一段/第二段切換;移除輸出掃動測試
// 舊: r7 (2026-09-13) 標題下方飛行狀態列(狀態/倒數/油門/結束原因/拒絕原因/外力),取消倒數,緊急停止連按三下
// 舊: r6 (2026-09-13) 倒飛圖示改為機頭換邊 + 上下顛倒(GG 糾正:r5 只做了上下顛倒)
// 舊: r5 (2026-09-13) 監看頁判斷倒飛/側飛(圖示上下翻轉並標示),啟動手勢開關(關閉時隱藏力道與試推燈)
// 舊: r4 (2026-09-13) 角度補償獨立分頁,紀錄分頁(角度/油門/G 力/短尖峰/手勢推力/Z 抖動圖表),換段三種方式,朝左翼自動顯示,手勢試推燈,提早降落改抖動判斷與即時狀態
// 舊: r3 (2026-09-13) 數字放大,斜坡改稱加力/減力秒數,換段方式(線性/階梯),曲線點分框,觸地提早降落設定,監看頁最近觸地衝擊
// 舊: r2 (2026-09-13) 加風格頁(六組,命名/選用/複製/回預設,時間軸,斜坡,上下限,補償曲線數值)與設定頁(方位,啟動,降落撞擊,速度,電變脈寬);參數一律 +/- 粗細調
// 舊: r1 (2026-09-13) 初版:監看頁(飛機側視姿態圖,感測器與控制迴圈狀態),系統頁(WiFi,韌體更新)
// r91 (2026-09-24) 降落減力方式(逐漸減力/忽高忽低)與低高油門,週期,蜂鳴器提醒;時間軸圖畫出忽高忽低;強制停機卡(搖擺機尾角度);
//   結束原因與事件:長按安全開關,搖擺機尾強制停機;錯誤碼 pulserange,wagdeg;降落中狀態列顯示忽高忽低提醒
// r90 (2026-09-16) 全部 ⓘ 說明重寫得精簡(GG):44 條參數說明,卡片說明,下拉選單說明,備份頁說明;內容與數值不變,只去掉重複與贅字.
// r89 (2026-09-16) 備份碼框字級 13 → 16px(點框時手機不再自動放大),套用框 inputmode=none 不彈鍵盤,提示改「長按這裡 → 貼上」.
// r88 (2026-09-16) 參數名稱「倒數秒數」改「起飛倒數秒數」(GG),延長秒數說明與備份頁項目說明跟著改.
// r87 (2026-09-16) 配色改灰藍銀(GG:琥珀/咖啡色看了討厭):主色鋼藍銀,底色冷灰藍,降落狀態列棕 → 藍,時間軸第二段/降落與紀錄頁抖動線換掉咖啡色;警告黃/紅不變.
// r86 (2026-09-16) WiFi 設定:刪 SSID 說明;發射功率警告移到拉桿下,超過 7 dBm 變紅框紅字;加連續開關電 3 次回出廠的簡短說明.
// r85 (2026-09-15) 三軸格標籤緊貼自己的數字(數字接在標籤後),欄間加細分隔線,避免前一個數字看起來屬於下一個標籤.
// r84 (2026-09-15) 角速度/零點改獨占一整排的三等分固定欄(頭/翼/背各一欄單行靠右),拿掉這兩格的自動縮字與兩行排法,數值變動不再換行或改框高.
// r83 (2026-09-15) 角速度/零點固定兩位小數與負號欄,三軸固定位置,不隨正負/位數自動換行.
// r82 (2026-09-15) 監看數值恢復 17px,僅對實際溢出的欄位自動縮字,維持小格尺寸.
// r81 (2026-09-15) 監看資訊框縮為緊湊等高小格,手機兩欄/桌面三欄,減少留白與框線重量.
// r80 (2026-09-15) 監看資訊框固定標題/數值高度,長資訊加寬,避免數值換行造成版面跳動.
// r79 (2026-09-15) SuperGG 字母彈跳改正向延遲,由左到右依序開始.
// r78 (2026-09-15) 深色頁籤加亮底色/邊框/文字,選中改實心琥珀底與深色粗字.
// r77 (2026-09-15) 移除無用的飛行控制台圖案與識別列,保留科技風格.
// r76 (2026-09-15) 航電控制台:石墨黑/琥珀橙,工程格線,儀表數字與飛機識別.
#pragma once
#include <Arduino.h>

const char WEB_PAGE_HTML[] PROGMEM = R"HTML(<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>線控飛機油門控制器</title>
<style>
*{box-sizing:border-box}
a{color:var(--accent)}
input,progress{accent-color:var(--accent)}
::selection{background:rgba(143,180,220,.35);color:inherit}
/* 頁尾作者(GG):每個分頁最下方,SuperGG 要醒目 */
.credit{display:flex;align-items:baseline;justify-content:center;flex-wrap:wrap;gap:4px 22px;padding:22px 16px 30px;margin-top:8px;border-top:1px solid var(--line);color:var(--mute);font-size:14px}
/* 設計者署名 SuperGG(GG:浮誇一點,七彩霓虹 + 動畫):每個字母一段彩虹漸層接起來,整體色相輪轉(光暈跟著變色),字母波浪跳動,兩側星星閃爍 */
.credit .gg{position:relative;display:inline-flex;font-size:32px;font-weight:900;letter-spacing:.03em;padding:4px 20px;animation:ggHue 4s linear infinite}
.credit .gg i{font-style:normal;display:inline-block;color:transparent;-webkit-background-clip:text;background-clip:text;
 background-image:linear-gradient(90deg,#ff1f5a,#ff8a00,#ffd400,#3ddc4a,#00c2ff,#7a5cff,#e040fb);background-size:700% 100%;
 background-position:calc(var(--i)*100%/6) 0;animation:ggWave 1.6s ease-in-out infinite;animation-delay:calc(var(--i)*.14s)}
.credit .gg::before,.credit .gg::after{content:'✦';position:absolute;font-size:15px;color:#ffd400;animation:ggTwinkle 1.8s ease-in-out infinite}
.credit .gg::before{left:0;top:0}
.credit .gg::after{right:0;bottom:2px;animation-delay:-.9s}
@keyframes ggHue{from{filter:drop-shadow(0 0 6px rgba(255,120,0,.75)) hue-rotate(0deg)}to{filter:drop-shadow(0 0 6px rgba(255,120,0,.75)) hue-rotate(360deg)}}
@keyframes ggWave{0%,100%{transform:translateY(0)}25%{transform:translateY(-5px) scale(1.08)}50%{transform:translateY(0)}}
@keyframes ggTwinkle{0%,100%{opacity:.15;transform:scale(.6) rotate(0deg)}50%{opacity:1;transform:scale(1.2) rotate(90deg)}}
@media (prefers-reduced-motion:reduce){.credit .gg,.credit .gg i,.credit .gg::before,.credit .gg::after{animation:none}}
.credit .line{font-weight:700;color:#06c755}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Noto Sans TC","Microsoft JhengHei",sans-serif}
header{position:sticky;top:0;z-index:5;background:var(--card);border-bottom:1px solid var(--line)}
/* 第一行固定一行高:未儲存提示出現時取代標題,不換行,下面的內容不會被往下推(GG:點欄位時被擠走) */
.bar{display:flex;align-items:center;gap:6px;padding:0 10px;height:42px;flex-wrap:nowrap;overflow:hidden}
.bar h1{font-size:15px;margin:0;flex:1 1 auto;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar .pill{flex:0 0 auto}
.bar.dirty h1,.bar.dirty .pill.ok{display:none}   /* 未儲存時讓出位置:正常(綠色)的感測器/網路狀態先藏起來,異常照樣顯示 */
.savegrp{display:flex;align-items:center;gap:5px;flex:1 1 auto;min-width:0}
.savegrp .pill{flex:0 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis}
.savegrp .b{padding:5px 11px;flex:0 0 auto}
.pill{font-size:13px;padding:2px 10px;border-radius:99px;background:var(--line);white-space:nowrap}
.pill.ok{background:var(--ok);color:#fff}.pill.bad{background:var(--bad);color:#fff}.pill.warn{background:var(--warn);color:#fff}
/* 飛行狀態列:待機也要一眼看得到;一旦進入起飛程序(放穩/倒數/飛行)改成實心色塊,倒數再加脈動 */
.fbar{position:relative;display:flex;gap:4px 10px;align-items:center;flex-wrap:wrap;padding:5px 10px 5px 8px;border-top:1px solid var(--line);border-left:6px solid var(--accent);background:var(--bg);overflow:hidden}
.fbar .ft{flex:1 1 180px;min-width:0;display:flex;align-items:center;flex-wrap:wrap;gap:0 8px}
.fbar .fbadge{flex:0 0 auto;font-size:11.5px;font-weight:700;letter-spacing:.05em;padding:1px 7px;border-radius:6px;background:var(--accent);color:#fff}
.fbar .ft b{font-size:18px;font-weight:800;line-height:1.25}
.fbar .ft .sub{font-size:12.5px;line-height:1.3;flex:1 1 100%}
.fbar .fprog{position:absolute;left:0;right:0;bottom:0;height:5px;background:rgba(255,255,255,.25)}
.fbar .fprog i{display:block;height:100%;width:0;background:#fff;transition:width .25s linear}
.fbar.wait{background:#fde68a;border-left-color:#b45309;animation:fbBreath 1.6s ease-in-out infinite}
.fbar.wait .fbadge{background:#b45309}.fbar.wait,.fbar.wait .sub{color:#422006}
.fbar.count{background:#ea580c;border-left-color:#7c2d12;color:#fff;animation:fbPulse .8s ease-in-out infinite}
.fbar.count .fbadge{background:#7c2d12}.fbar.count .sub{color:#ffedd5}.fbar.count .ft b{font-size:24px}
.fbar.fly{background:#16a34a;border-left-color:#14532d;color:#fff}.fbar.fly .fbadge{background:#14532d}.fbar.fly .sub{color:#dcfce7}
.fbar.land{background:#3d6a99;border-left-color:#1f3a5c;color:#fff}.fbar.land .fbadge{background:#1f3a5c}.fbar.land .sub{color:#dbe7f5}
.fbar.crash{background:#dc2626;border-left-color:#7f1d1d;color:#fff}.fbar.crash .fbadge{background:#7f1d1d}.fbar.crash .sub{color:#fee2e2}
.fbar.done{border-left-color:var(--mute)}.fbar.done .fbadge{background:var(--mute)}
.fbar.reject{background:#fee2e2;border-left-color:#dc2626}.fbar.reject .fbadge{background:#dc2626}
@keyframes fbPulse{0%,100%{filter:brightness(1)}50%{filter:brightness(1.18)}}
@keyframes fbBreath{0%,100%{box-shadow:inset 0 0 0 0 rgba(180,83,9,0)}50%{box-shadow:inset 0 0 0 3px rgba(180,83,9,.55)}}
@media (prefers-reduced-motion:reduce){.fbar.wait,.fbar.count{animation:none}}
/* 忽略安全開關:置頂一直顯示的紅色警告(GG 2026-09-14),設定頁的風險確認框 */
.asoff{display:flex;flex-wrap:wrap;align-items:center;gap:2px 10px;padding:8px 10px;background:#b91c1c;color:#fff;border-top:1px solid #7f1d1d;animation:asPulse 1.6s ease-in-out infinite}
.asoff b{font-size:17px;font-weight:800;letter-spacing:.02em}.asoff span{font-size:13.5px;font-weight:600}
@keyframes asPulse{50%{background:#dc2626}}
.aorow{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px}
.aowarn{margin:8px 0 2px;padding:8px 10px;border:2px solid var(--bad);border-radius:8px;background:rgba(209,36,47,.08);font-size:13.5px;line-height:1.55}
.aowarn .aoh{color:var(--bad);font-weight:800;font-size:15px;margin-bottom:4px}.aowarn .chk{display:flex;gap:6px;align-items:flex-start;margin:6px 0 0;font-weight:600}
.wtrial{display:flex;align-items:center;gap:10px;padding:6px 10px;background:#fef3c7;color:#78350f;border-top:1px solid #f59e0b;font-size:13.5px;font-weight:600}
.wtrial span{flex:1 1 auto}.wtrial .b{flex:0 0 auto;padding:6px 16px}
button.b.start{background:var(--ok);border-color:var(--ok);color:#fff;font-weight:700;padding:8px 14px}
button.b.start.arm{background:#c2410c;border-color:#c2410c}
button.b.estop{background:var(--bad);border-color:var(--bad);color:#fff;font-weight:700;padding:8px 14px}
/* 分頁列:八個分頁在手機寬度一排放得下,不用橫捲才看得到「電變」「系統」;更窄的螢幕才橫捲 */
/* 分頁列兩行堆疊(GG 2026-09-15:九個分頁橫捲要找很久):一行 5 個,不橫捲 */
nav{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:0;padding:0 4px}
nav button{min-width:0;border:0;background:none;color:var(--mute);font:inherit;font-size:14px;padding:6px 2px 5px;border-bottom:3px solid transparent;cursor:pointer;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
nav button.on{color:var(--ink);border-color:var(--accent);font-weight:700}
@media (min-width:900px){nav{max-width:760px;margin:0 auto}nav button{padding:7px 6px 6px}}
/* 備份分頁:勾選項目 */
.bkhd{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 10px;margin:10px 0 4px;font-size:15px}
.bkq{display:flex;gap:12px;font-size:14px}
.bkgt{font-size:14px;font-weight:700;margin:8px 0 1px}
.bkd{font-size:13px;color:var(--mute);line-height:1.45}
/* 計時器風格:醒目的主色粗框(GG);說明收進 ⓘ */
.bkprof{border:2px solid var(--accent);border-radius:12px;background:var(--accentBg);padding:8px 10px 2px;margin:6px 0 10px}
.bkpt{font-size:16px;font-weight:700;color:var(--ink)}
.bkhint{display:none;color:var(--mute);font-size:12.5px;margin:3px 0 4px;padding:5px 8px;border-radius:6px;background:var(--bg);line-height:1.45}
.showhint>.bkhint{display:block}
/* 其他設定:小方塊一行兩個,名稱 + ⓘ(GG:縮小,說明用 ⓘ) */
.bksecs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px;margin:4px 0 6px}
.bks{display:flex;flex-wrap:wrap;align-items:center;min-width:0;border:1.5px solid var(--line);border-radius:8px;background:var(--bg)}
.bks.showhint{grid-column:1/-1}
.bkst{flex:1 1 0;min-width:0;border:0;background:none;color:var(--ink);font:inherit;font-size:14px;text-align:left;padding:6px 2px 6px 8px;cursor:pointer}
.bks .ib{padding:6px 8px}
.bks>.bkhint{flex:1 1 100%;margin:0 6px 6px}
.bks .mk::before{content:'☐ '}
.bks.on{border-color:var(--accent);background:var(--accentBg)}.bks.on .bkst{font-weight:700}.bks.on .mk::before{content:'☑ '}
.bkwm{color:var(--bad);margin-left:3px}
/* 套用時取消的項目:變灰,打 ✕,刪除線 */
.bkpick button:not(.on){opacity:.55;color:var(--mute)}
.bkpick button:not(.on)::before{content:'✕ ';color:var(--bad)}
.bks.pick .mk::before{content:'✓ '}
.bks.pick:not(.on){opacity:.55}
.bks.pick:not(.on) .bkst{color:var(--mute)}
.bks.pick:not(.on) .mk::before{content:'✕ ';color:var(--bad)}
main{max-width:860px;margin:0 auto;padding:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 12px;margin-bottom:8px}
@media (max-width:600px){main{padding:8px}.card{padding:8px 10px}}
.card h2{font-size:15px;margin:0 0 4px;font-weight:700;display:flex;align-items:center;gap:4px;flex-wrap:wrap}
.card h2 .h2r{margin-left:auto;font-weight:400}
.card h3.grp{font-size:13px;color:var(--mute);font-weight:700;margin:8px 0 0;padding-top:6px;border-top:1px dashed var(--line);letter-spacing:.03em}
.card h3.grp:first-of-type{border-top:0;margin-top:2px;padding-top:0}
/* 卡片說明:預設收起,點標題旁的 ⓘ 展開(GG 2026-09-14:說明文字佔太多版面) */
.cnote{display:none;margin:0 0 6px;padding:6px 9px;border-radius:8px;background:var(--bg);color:var(--mute);font-size:13px;line-height:1.5}
.card.shownote .cnote{display:block}
.ib{border:0;background:none;color:var(--accent);font-size:15px;line-height:1;padding:2px 4px;margin-left:1px;cursor:pointer;vertical-align:baseline;font-weight:400}
.att{display:flex;gap:6px 16px;align-items:center;flex-wrap:wrap}
.att svg{flex:1 1 280px;max-width:100%;height:auto;border-radius:10px}
.att .read{flex:1 1 100%;display:flex;align-items:center;gap:4px 12px;flex-wrap:wrap}
.att .read .rd{line-height:1.2}.att .read .rd2{font-size:15px}.att .read .rd2 b{font-size:18px}
.att .read .pill{font-size:15px;padding:2px 14px;margin-left:auto}
@media (min-width:700px){.att .read{flex:0 0 170px;flex-direction:column;align-items:flex-start}.att .read .pill{margin-left:0}}
.big{font-size:40px;font-weight:700;font-variant-numeric:tabular-nums;line-height:1.1}
button.b.sm{padding:3px 10px;font-size:13px}
.sub{color:var(--mute);font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:5px}
.stat{border:1px solid var(--line);border-radius:8px;padding:3px 8px;min-width:0}
.stat .k{font-size:11.5px;color:var(--mute);line-height:1.3}.stat .v{font-size:16px;font-weight:700;font-variant-numeric:tabular-nums;line-height:1.35;overflow-wrap:anywhere}
.grid.g3{grid-template-columns:repeat(3,minmax(0,1fr))}
.row{display:flex;gap:6px 8px;align-items:center;flex-wrap:wrap;margin:6px 0}
.row label{flex:0 0 96px;color:var(--mute);font-size:14px}
.row label.chk{flex:0 0 auto;color:var(--ink)}
.row label .lsub{display:block;font-size:12px;line-height:1.2}
.wgrp{border:1px solid var(--line);border-radius:10px;padding:5px 9px 3px;margin:8px 0}
.wgt{font-size:13px;font-weight:700;color:var(--ink);margin:1px 0 0}
.apfix{font-weight:700;font-size:14px;white-space:nowrap}.sub.bad{color:var(--bad)}
.txphi{color:var(--bad)!important;font-weight:700}#txpWarn.txphi{padding:4px 8px;border:2px solid var(--bad);border-radius:6px;background:rgba(209,36,47,.1)}
input[type=text],input[type=password],input[type=number],select{padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--ink);font:inherit;min-width:0}
.row input[type=text],.row input[type=password],.row input[type=number]{flex:1 1 160px}
.row input[type=range]{flex:1 1 160px;min-width:0}
/* 設定備份碼:英數字長串要能在任何位置斷行. 字級 16px:iPhone 點到小於 16px 的輸入框會自動放大畫面(GG 2026-09-16);
   套用框加 inputmode=none 不叫出鍵盤,長按照樣有「貼上」. 網頁是 http,瀏覽器不准讀剪貼簿,做不出一按就貼上的按鈕. */
.bktext{display:block;width:100%;box-sizing:border-box;margin:4px 0;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--ink);font:16px/1.35 ui-monospace,Consolas,monospace;word-break:break-all;resize:vertical}
.bktext:disabled{opacity:.5}
button,select,input{touch-action:manipulation}   /* 連點按鈕不觸發雙擊放大,雙指縮放照常 */
button.b{flex:0 0 auto;white-space:nowrap;border:1px solid var(--line);background:var(--bg);color:var(--ink);font:inherit;padding:7px 14px;border-radius:8px;cursor:pointer}
button.b.pri{background:var(--accent);border-color:var(--accent);color:#fff}
button.b.danger{border-color:var(--bad);color:var(--bad)}
button.b:disabled{opacity:.45;cursor:default}
.msg{min-height:1.4em;font-size:14px}.msg.ok{color:var(--ok)}.msg.bad{color:var(--bad)}
.seg{display:inline-flex;flex-wrap:wrap;border:1px solid var(--line);border-radius:8px;overflow:hidden}
.seg button{border:0;border-right:1px solid var(--line);background:var(--bg);color:var(--ink);font:inherit;padding:6px 12px;cursor:pointer;white-space:nowrap}
.seg button:last-child{border-right:0}
.seg button.on{background:var(--accent);color:#fff}
.bksel{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 8px}
.bksel button{border:2px solid var(--line);border-radius:999px;background:var(--card);color:var(--ink);font:inherit;font-size:16px;font-weight:600;padding:7px 16px;cursor:pointer}
.bksel button.on{border-color:var(--accent);background:var(--accent);color:#fff;font-weight:700;box-shadow:0 2px 0 rgba(0,0,0,.15)}
.bksel button.on::before{content:'✓ '}
.seg.phseg{display:flex;width:100%;margin:8px 0 6px;border:2px solid var(--accent);border-radius:10px}
.seg.phseg button{flex:1 1 0;padding:9px 12px;font-size:15px;font-weight:700;color:var(--accent);background:var(--card);border-right:2px solid var(--accent)}
.seg.phseg button:last-child{border-right:0}
.seg.phseg button.on{background:var(--accent);color:#fff;box-shadow:inset 0 -3px 0 rgba(0,0,0,.18)}
.prm{display:flex;flex-wrap:wrap;align-items:center;gap:2px 8px;padding:4px 0;border-top:1px solid var(--line)}
.prm:first-of-type,h2+.prm,.cnote+.prm,h3+.prm,h3.grp+.prm{border-top:0}
.prm .lab{flex:1 1 100px;min-width:0;font-size:14px;line-height:1.25}
.prm .hint{display:none;color:var(--mute);font-size:12.5px;margin-top:3px;padding:5px 8px;border-radius:6px;background:var(--bg);line-height:1.45}
.prm.showhint .hint{display:block}
.prm .ctl{display:flex;align-items:center;gap:3px;flex:0 1 auto;margin-left:auto}
.prm .ctl select{max-width:210px}
.prm .ctl .b{padding:6px 0;width:38px;text-align:center;font-size:13px;font-variant-numeric:tabular-nums}
.prm .ctl .b.st{width:42px;padding:5px 0;font-size:20px;line-height:1.1;font-weight:700;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none}
.prm .ctl .b.st.on{background:var(--accent);border-color:var(--accent);color:#fff}
/* 數值框沒有 type 屬性,吃不到上面 input[type=…] 的配色,要自己給文字色與底色(暗色模式原本是黑字配深底) */
.prm .val{width:68px;padding:1px 5px;text-align:right;font-size:20px;font-weight:700;line-height:1.25;font-variant-numeric:tabular-nums;
 color:var(--ink);background:var(--bg);border:1px solid var(--mute);border-radius:6px;font-family:inherit}
.prm .unit{min-width:27px;color:var(--mute);font-size:13px}
.pts{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:10px;margin-top:8px}
.pt{border:1px solid var(--line);border-radius:10px;padding:4px 10px 0;background:var(--bg)}
.pt h4{margin:4px 0 0;font-size:14px}
.pt .prm .val{background:var(--card)}
.prm .extra{color:var(--mute);font-size:12px;font-variant-numeric:tabular-nums}
.prm .extra:empty{display:none}
.profseg button .star{color:#f5b301}
.dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--bad);margin-left:4px;vertical-align:middle}
.side{border:1px dashed var(--line);border-radius:10px;padding:6px 10px;margin:8px 0}
.cvwrap{display:flex;gap:14px;flex-wrap:wrap;align-items:flex-start}
.cvchart{flex:1 1 380px;min-width:0}
.cvchart svg{width:100%;height:auto;display:block;user-select:none;-webkit-user-select:none}
.cvside{flex:1 1 250px;min-width:0}
.gesture{border:1px solid var(--line);border-radius:10px;padding:4px 10px;margin-bottom:6px;background:var(--bg);font-size:14px}
.gesture summary{cursor:pointer}.gesture div{margin:3px 0}.gesture .gk{display:inline-block;min-width:92px;font-weight:700;color:var(--accent)}
.gesture .sub{margin-top:4px}
.cvpanel .selbox{border:2px solid #ef4444;border-radius:10px;padding:4px 10px;background:var(--bg)}
.cvpanel .selbox h3{margin:3px 0;font-size:14.5px;color:#ef4444}
.cvpanel .wl{display:grid;grid-template-columns:76px 1fr;gap:6px;align-items:baseline;font-size:14px;margin:2px 0}
/* 朝上/朝下點數:各自一個框,標籤和選單看得出是同一組(GG:兩者離得遠,中間是說明展開的位置) */
.cnt2{display:flex;gap:6px 10px;flex-wrap:wrap;margin-top:6px}.cnt2 .prm{flex:1 1 150px;border:1px solid var(--line);border-radius:8px;padding:4px 8px;background:var(--bg)}.cnt2 .prm select{background:var(--card)}
.cv-limit{fill:var(--mute);opacity:.18}.cv-dead{fill:var(--accent);opacity:.09}
.cv-grid{stroke:var(--line);stroke-width:1}.cv-zero{stroke:var(--mute);stroke-width:1;stroke-dasharray:4 4}
.cv-lab{fill:var(--mute);font-size:13px;font-family:system-ui,sans-serif}.cv-sm{font-size:10.5px}
.cv-frame{fill:none;stroke:var(--mute);stroke-width:1.2}
.cv-lim{stroke:var(--ink);stroke-width:1.6;stroke-dasharray:7 4}
.cv-base{stroke:var(--accent);stroke-width:1.6;stroke-dasharray:3 3}
.cv-raw{fill:none;stroke:var(--mute);stroke-width:1.6;stroke-dasharray:5 4}
.cv-curve{fill:none;stroke:var(--accent);stroke-width:3.6;stroke-linejoin:round;stroke-linecap:round}
.cv-pt{fill:var(--card);stroke:var(--accent);stroke-width:2.2;cursor:grab}
.cv-pt.sel{fill:#ef4444;stroke:#fff;stroke-width:2;filter:url(#cvGlow)}
.cv-db{fill:var(--accent);stroke:none;pointer-events:none}
.cv-hd{fill:var(--ink);cursor:grab}.cv-hd.base{fill:var(--accent)}.cv-hd.sel{fill:#ef4444;filter:url(#cvGlow)}
.cv-hit{fill:transparent;cursor:grab}
.cv-tag{fill:var(--card);stroke:var(--accent);stroke-width:1.2}.cv-tagt{fill:var(--ink);font-size:13px;font-weight:700;font-family:system-ui,sans-serif}
.cv-now{stroke:#ef4444;stroke-width:2}.cv-nowt{fill:#ef4444;font-size:12.5px;font-weight:700;font-family:system-ui,sans-serif;paint-order:stroke;stroke:var(--card);stroke-width:4px;stroke-linejoin:round}
.cv-plane{fill:var(--plane);opacity:.8}
.tl-lab{fill:var(--mute);font-size:13px;font-family:system-ui,sans-serif}
.tl-seg{fill:var(--ink);font-size:12px;font-weight:600;font-family:system-ui,sans-serif;paint-order:stroke;stroke:var(--card);stroke-width:3.5px;stroke-linejoin:round}
.tl-leg{display:flex;flex-direction:column;gap:3px;font-size:12px;color:var(--mute);margin:0 0 8px}
.tl-leg i{display:inline-block;width:16px;height:11px;border-radius:2px;margin-right:6px;vertical-align:middle;opacity:.75}
.tl-leg i.hatch{background:repeating-linear-gradient(45deg,var(--mute) 0 2px,transparent 2px 5px);opacity:.6}
.tl-leg i.lim{height:0;border-top:2px dashed var(--ink);border-radius:0;opacity:1}
.tl-t{fill:var(--ink);font-size:13px;font-weight:700;font-family:system-ui,sans-serif}
.tl-v{fill:var(--accent);font-size:15px;font-weight:800;font-family:system-ui,sans-serif;paint-order:stroke;stroke:var(--card);stroke-width:4px;stroke-linejoin:round}
.side h3{font-size:14px;margin:4px 0}
.toast{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);max-width:calc(100% - 32px);background:var(--ink);color:var(--card);padding:8px 16px;border-radius:10px;font-size:14px;z-index:20;box-shadow:0 4px 18px rgba(0,0,0,.25)}
.toast.bad{background:var(--bad);color:#fff}
.lamp{display:inline-block;width:22px;height:22px;border-radius:50%;background:#9aa1ad;vertical-align:middle;margin-right:6px;box-shadow:inset 0 -2px 4px rgba(0,0,0,.25)}
.lamp.on{background:#22c55e;box-shadow:0 0 12px 3px rgba(34,197,94,.7),inset 0 -2px 4px rgba(0,0,0,.2)}
.lamp.warnon{background:#f59e0b;box-shadow:0 0 12px 3px rgba(245,158,11,.75),inset 0 -2px 4px rgba(0,0,0,.2)}
.live .lamp{width:16px;height:16px;flex:0 0 auto;margin-right:0}
.live{display:flex;align-items:center;gap:4px 8px;flex-wrap:wrap;padding:4px 8px;margin:3px 0 1px;border-radius:8px;background:var(--bg);font-size:13px;font-variant-numeric:tabular-nums}
.live b{font-weight:600}
.meter{flex:1 1 120px;height:8px;border-radius:4px;background:var(--line);overflow:hidden}
.meter i{display:block;height:100%;background:var(--warn);width:0}
.inst-views{display:flex;flex-wrap:wrap;gap:6px;margin:4px 0}
.inst-views figure{flex:1 1 280px;min-width:0;margin:0;border:1px solid var(--line);border-radius:10px;background:var(--bg);padding:3px 4px 0}
.inst-views figcaption{font-size:13px;font-weight:700;padding:0 4px}
.axrow{display:flex;flex-wrap:wrap;align-items:center;gap:6px 14px;margin:4px 0;font-size:14px}
.axrow label{display:flex;align-items:center;gap:6px}.axrow select{padding:4px 6px}
.inst-views svg{width:100%;height:auto;display:block}
.ins-body{fill:var(--plane);opacity:.28}.ins-hz{stroke:var(--mute);stroke-dasharray:6 5;opacity:.6}
.ins-chip{fill:#1f2937;stroke:#fff;stroke-width:1.2}
.ins-t{font-size:14px;font-weight:700;font-family:system-ui,sans-serif;paint-order:stroke;stroke:var(--bg);stroke-width:4px;stroke-linejoin:round}
.ins-s{fill:var(--mute);font-size:12px;font-family:system-ui,sans-serif}
.ins-v{fill:var(--ink);font-size:15px;font-weight:700;font-family:system-ui,sans-serif}
.axk{font-size:13px;margin-right:2px}.axk.nose{color:#dc2626}.axk.up{color:#16a34a}.axk.left{color:#d97706}
.inst-def{background:var(--bg);border-radius:8px;padding:6px 10px;justify-content:space-between;font-size:14px}
.man-read{display:flex;align-items:center;gap:4px 10px;flex-wrap:wrap;margin:4px 0;font-variant-numeric:tabular-nums}
.man-read b{font-size:26px;font-weight:800}
.chk{display:flex;align-items:center;gap:8px;margin:6px 0;font-size:14px;cursor:pointer}
.chk input{width:20px;height:20px;flex:0 0 auto}
.man-slider{width:100%;height:32px;margin:2px 0}
.man-btns{display:grid;grid-template-columns:repeat(6,1fr);gap:5px;margin:2px 0 2px}
.man-btns .b{padding:7px 0;text-align:center}
.steps{margin:6px 0;padding-left:22px;font-size:14px}.steps li{margin:2px 0}
.subd{border:1px solid var(--line);border-radius:8px;padding:3px 10px;margin:2px 0 4px;background:var(--bg);font-size:14px}
.subd summary{cursor:pointer;font-weight:600}
details.card>summary{cursor:pointer;padding:2px 0}
.fwnotes{white-space:pre-wrap;font-size:13.5px;background:var(--bg);border-radius:8px;padding:6px 9px;margin:2px 0;max-height:220px;overflow-y:auto}
.fwnotes:empty{display:none}
.brand{border:1px solid var(--line);border-radius:10px;margin:8px 0;background:var(--bg)}
.brand summary{cursor:pointer;padding:8px 10px;font-weight:600;font-size:14px;display:flex;flex-wrap:wrap;gap:4px 8px;align-items:center}
.brand summary .tag{font-weight:500;font-size:12px;padding:1px 8px;border-radius:99px;background:var(--line)}
.brand summary .tag.ok{background:#dcfce7;color:#14532d}.brand summary .tag.no{background:#fee2e2;color:#7f1d1d}.brand summary .tag.man{background:#fef3c7;color:#78350f}
.brand .bd{padding:0 12px 10px;font-size:14px}
.brand .bd .kv{margin:4px 0}.brand .bd a{color:var(--accent);word-break:break-all}
.brand .conf{font-size:12px;color:var(--mute)}
.evbox{max-height:230px;overflow-y:auto;margin-top:4px;border:1px solid var(--line);border-radius:8px;background:var(--bg);padding:4px 0;font-size:13.5px;line-height:1.45}
.ev{display:flex;gap:10px;padding:3px 10px;border-bottom:1px dashed var(--line)}.ev:last-child{border-bottom:0}
.ev .et{flex:0 0 auto;min-width:74px;text-align:right;color:var(--mute);font-variant-numeric:tabular-nums;font-family:ui-monospace,Consolas,monospace}
.ev .em{flex:1 1 auto;min-width:0}.ev .eh{display:block;color:var(--mute);font-size:12.5px}
.ev.stop{background:rgba(220,38,38,.10)}.ev.stop .em>b{color:var(--bad)}
.ev.land{background:rgba(245,158,11,.12)}.ev.land .em>b{color:var(--warn)}
.ev.bad .em>b{color:var(--bad)}.ev.good .em>b{color:var(--ok)}.ev.dim{color:var(--mute)}
progress{width:100%;height:10px}
[hidden]{display:none!important}
/* 航電面板:灰藍石墨底,鋼藍銀標記(GG 2026-09-16:琥珀色看了討厭,改回灰藍銀);離線可用,保留控制項排列與警示色. */
:root{color-scheme:dark;--bg:#101419;--card:#1a1f26;--ink:#e8ecf1;--mute:#9aa4b1;--line:#353d48;--accent:#8fb4dc;--accentBg:rgba(143,180,220,.10);--ok:#38804c;--warn:#946014;--bad:#c93636;--plane:#dfe5ec;--sky:#1e2833;--ground:#262b31;--mono:ui-monospace,"Cascadia Code",Consolas,monospace}
body{background-image:linear-gradient(rgba(143,180,220,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(143,180,220,.03) 1px,transparent 1px);background-size:32px 32px}
header{box-shadow:0 6px 24px #0005;border-top:2px solid var(--accent)}
.bar{background:#141920}.bar h1{letter-spacing:.04em}
.bar h1::before{content:'';display:inline-block;width:7px;height:14px;margin-right:8px;background:var(--accent);vertical-align:-2px;transform:skew(-15deg)}
.pill{border-radius:4px;font-size:12px;font-weight:600}
.fbar .fbadge{border-radius:3px;background:#2e4560;color:#dbe9f7}
.fbar.reject,.fbar.reject .sub{color:#7f1d1d}.fbar.done .fbadge{color:#161819}
nav{gap:5px;padding:6px;counter-reset:panel;background:#141920}
nav button{counter-increment:panel;border:1px solid #5f6b78;border-radius:4px;background:#2c343e;color:#e2e8ee;font-weight:600;padding:7px 2px}
nav button::before{content:counter(panel,decimal-leading-zero);font:10px var(--mono);margin-right:5px;opacity:.8}
nav button.on{color:#0f1720;background:var(--accent);border-color:#c9dcf0;font-weight:800;box-shadow:inset 0 -3px #5b7fa6,0 0 0 1px #8fb4dc33}
.card{border-radius:6px;border-top-color:#4a5563;box-shadow:0 3px 12px #0003;padding:12px 14px;margin-bottom:10px}
.card h2{letter-spacing:.035em;margin-bottom:8px}
.card h2::before{content:'';width:3px;height:13px;background:var(--accent);flex:0 0 auto;margin-right:5px}
.card h3.grp{color:var(--accent)}
.stat{background:#141920;border-radius:4px;padding:7px 9px;border-left:2px solid #4f6a88}
.stat .k{margin-bottom:4px}.stat .v{font-family:var(--mono);font-size:17px}
/* 小型儀表格:單行標題 + 固定兩行數值,更新不改尺寸;極長資料仍可在格內捲動查看. */
.sensor-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:4px}
.sensor-grid .stat{padding:5px 7px;border:1px solid #36404b;border-radius:4px;background:#161c23}
.sensor-grid .stat .k{height:15px;line-height:15px;font-size:11.5px;margin-bottom:2px;white-space:nowrap;overflow:auto}
.sensor-grid .stat .v{height:34px;line-height:17px;font-size:17px;font-weight:600;overflow:auto}
/* 三軸格(角速度/零點):獨占一整排,固定三等分欄,每軸單行靠右;數值怎麼變都不換行,不縮字,框高固定 */
.sensor-grid .stat.axes{grid-column:1/-1}
.sensor-grid .stat .v.ax{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));column-gap:7px;height:20px;line-height:20px;overflow:hidden;white-space:nowrap}
.v.ax>span{display:flex;align-items:baseline;gap:5px;min-width:0;overflow:hidden}
.v.ax>span+span{border-left:1px solid var(--line);padding-left:7px}
.v.ax i{font:400 11.5px system-ui,sans-serif;color:var(--mute)}
.v.ax b{font-weight:600}
@media (min-width:600px){.sensor-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
.big{font-family:var(--mono);color:var(--accent);font-size:46px;letter-spacing:-.04em}
.att svg{border:1px solid var(--line);border-radius:4px}
.att .read{padding:10px;background:#141920;border:1px solid var(--line);border-radius:4px}
.att .rd2 b,.man-read b,.prm .val{font-family:var(--mono)}
.prm .val{background:#0f1318;border-color:#56616e;border-radius:4px;color:#dbe9f7}
input[type=text],input[type=password],input[type=number],select,.bktext{border-radius:4px;background:#11161c}
button.b{border-radius:4px;background:#252c35;font-weight:600;box-shadow:inset 0 1px #ffffff08}
button.b.pri,.seg button.on,.bksel button.on,.seg.phseg button.on,.prm .ctl .b.st.on{color:#0f1720;background:var(--accent);border-color:var(--accent)}
button.b.danger{color:#ff9292;border-color:#ac4b4b;background:#361e20}
.seg,.seg.phseg,.bksel button,.bkprof,.bks,.pt,.wgrp,.cnt2 .prm,.gesture,.side,.evbox,.subd,.brand,.inst-views figure{border-radius:4px}
.bkprof{border-width:1px;border-left-width:3px}
.bksel button{font-size:15px}.bksel button.on{box-shadow:none}
.evbox{background:#11161c}.ev{padding-top:6px;padding-bottom:6px}
.msg.ok,.ev.good .em>b{color:#88d39a}.msg.bad,.sub.bad,.ev.bad .em>b,.ev.stop .em>b,.aowarn .aoh{color:#ff9292}
.ev.land .em>b{color:#f0b35b}
.credit{border-top-style:dashed;font-size:12px}
:where(button,input,select,textarea,summary,a):focus-visible{outline:2px solid var(--accent);outline-offset:3px}
@media (hover:hover){button.b:not(:disabled):hover,nav button:hover,.bksel button:hover{filter:brightness(1.16);border-color:var(--accent)}}
@media (max-width:600px){.card{padding:10px}nav button::before{display:none}nav button{min-height:36px}}
@media (prefers-reduced-motion:reduce){.asoff{animation:none}.fbar .fprog i{transition:none}}
</style></head><body>
<header>
 <div class="bar" id="topBar"><h1>線控飛機油門控制器</h1>
  <span class="savegrp" id="saveBar" hidden><span class="pill bad" title="有未儲存的變更,儲存前不能起飛">未儲存,不能起飛</span><button class="b pri" id="btnSave">儲存</button><button class="b" id="btnRevert">放棄</button></span>
  <span id="pillLock" class="pill warn" hidden>設定已鎖定</span><span id="pillImu" class="pill">感測器</span><span id="pillNet" class="pill">網路</span></div>
 <div class="fbar" id="fbar"><div class="ft"><span class="fbadge" id="fBadge">狀態</span><b id="fState">--</b><span class="sub" id="fDetail"></span></div><div class="fprog" id="fProgBox" hidden><i id="fProg"></i></div>
  <button class="b start" id="btnStart" hidden>開始起飛程序</button><button class="b" id="btnCancel" hidden>取消倒數</button><button class="b estop" id="btnEstop" hidden>緊急停止(連按三下)</button></div>
 <div class="asoff" id="asOffBar" hidden><b>⚠ 安全開關已停用</b><span id="asOffText"></span></div>
 <div class="wtrial" id="wifiTrial" hidden><span id="wifiTrialText"></span><button class="b pri" id="btnWifiKeep">保持</button></div>
 <div class="wtrial" id="fwBar" hidden><span id="fwBarText"></span></div>
 <nav><button data-pane="mon" class="on">監看</button><button data-pane="prof">計時器</button><button data-pane="comp">角度補償</button><button data-pane="set">設定</button><button data-pane="log">紀錄</button><button data-pane="inst">安裝</button><button data-pane="esc">電變</button><button data-pane="sys">系統</button><button data-pane="bak">備份</button></nav>
</header>
<main>
<section id="mon">
 <div class="card">
  <h2>機頭角度</h2>
  <div class="att">
   <svg id="attSvg" viewBox="-160 -100 320 200" role="img" aria-label="飛機側視姿態圖">
    <rect x="-160" y="-100" width="320" height="100" fill="var(--sky)"/>
    <rect x="-160" y="0" width="320" height="100" fill="var(--ground)"/>
    <line x1="-160" y1="0" x2="160" y2="0" stroke="var(--mute)" stroke-dasharray="6 5" opacity=".55"/>
    <g id="scale" font-size="10" fill="var(--mute)" text-anchor="end"></g>
    <!-- 背景油門曲線(橫軸油門 0~100%,直軸同機頭角度)與目前角度紅線 -->
    <g id="monCurve"></g>
    <g id="monNow"></g>
    <g id="plane">
     <g id="planeFlip" fill="var(--plane)">
      <path d="M-92,0 Q-90,-9 -72,-10 L58,-5 L96,-3 L96,3 L58,5 L-72,10 Q-90,9 -92,0 Z"/>
      <path d="M-46,-9 Q-30,-23 -8,-8 Z" opacity=".75"/>
      <path d="M68,-4 L90,-30 L100,-30 L97,-3 Z"/>
      <rect x="72" y="-1.5" width="28" height="3" opacity=".8"/>
      <rect x="-50" y="0" width="58" height="4" opacity=".55"/>
      <line x1="-44" y1="9" x2="-54" y2="30" stroke="var(--plane)" stroke-width="3"/>
      <circle cx="-54" cy="32" r="6"/>
      <rect x="-97" y="-28" width="3" height="56" rx="1.5" opacity=".8"/>
     </g>
    </g>
   </svg>
   <div class="read">
    <span class="big" id="pitch">--</span>
    <span class="sub rd">機頭角度<br>朝上為正</span>
    <span class="rd2">滾轉 <b id="roll">--</b></span>
    <span class="pill ok" id="attMode">--</span>
   </div>
  </div>
  <div class="sub" id="compPreview" style="margin-top:4px"></div>
 </div>
 <div class="card">
  <h2>事件紀錄 <span class="sub">(這次通電)</span></h2>
  <div class="cnote">降落,馬達停止,感測器異常等事件與原因,時間是通電後幾秒. 斷電或重新開機才清除;第一行是這次為什麼開機.</div>
  <div class="evbox" id="evBox"><div class="sub">讀取中…</div></div>
 </div>
 <div class="card">
  <h2>感測器與輸出<span class="h2r"><button class="b sm" id="btnTiming">清除迴圈紀錄</button></span></h2>
  <div class="cnote">靜止時自動學習陀螺儀零點. 觸地衝擊只記 80 毫秒內結束的短衝擊,拿飛機輕敲地面看數值,用來訂觸地門檻. 「清除迴圈紀錄」把最長執行與延遲歸零.</div>
  <div class="grid sensor-grid">
   <div class="stat"><div class="k">加速度大小</div><div class="v" id="acc">--</div></div>
   <div class="stat"><div class="k">靜止</div><div class="v" id="still">--</div></div>
   <div class="stat"><div class="k">安全開關(GPIO21)</div><div class="v" id="armSw">--</div></div>
   <div class="stat"><div class="k">電變輸出</div><div class="v" id="esc">--</div></div>
   <div class="stat"><div class="k">迴圈 最長執行 / 延遲</div><div class="v" id="timing">--</div></div>
   <div class="stat"><div class="k">最近觸地衝擊</div><div class="v" id="impact">--</div></div>
   <div class="stat"><div class="k">Z 軸抖動 / 正飛水平</div><div class="v" id="vib">--</div></div>
   <div class="stat axes"><div class="k">角速度 °/秒</div><div class="v ax" id="gyro"><span><i>頭</i><b>--</b></span><span><i>翼</i><b>--</b></span><span><i>背</i><b>--</b></span></div></div>
   <div class="stat axes"><div class="k">陀螺儀零點 °/秒</div><div class="v ax" id="bias"><span><i>頭</i><b>--</b></span><span><i>翼</i><b>--</b></span><span><i>背</i><b>--</b></span></div></div>
  </div>
 </div>
</section>

<section id="prof" hidden>
 <div class="card">
  <h2>風格</h2>
  <div class="cnote">★ = 飛行使用的風格,紅點 = 有未儲存的變更. 點一下切換要編輯哪一組(計時器與角度補償一起換). 複製會把這一組全部蓋到選的那一組.</div>
  <div class="seg profseg" id="profSeg"></div>
  <div class="row">
   <input type="text" id="fName" maxlength="23" style="flex:1 1 90px" placeholder="風格名稱"><button class="b" id="btnName">改名</button>
   <button class="b pri" id="btnSelect">設為飛行使用</button>
  </div>
  <div class="row" style="margin-bottom:0">
   <span class="sub">複製到</span><select id="copyTo"></select><button class="b" id="btnCopy">複製</button>
   <button class="b danger" id="btnProfDef" style="margin-left:auto">這組回預設</button>
  </div>
 </div>
 <div id="profCards"></div>
 <svg id="tlSvg" viewBox="0 0 440 194" role="img" aria-label="飛行時間軸圖" style="width:100%;height:auto;display:block;margin:2px 0 4px"></svg>
 <div id="tlLegend" class="tl-leg"></div>
</section>

<section id="comp" hidden>
 <div class="card">
  <h2>角度補償曲線</h2>
  <div class="cnote">直軸是機頭角度,橫軸是實際輸出油門. 補償值加在當段的基本油門上,兩段共用同一條曲線;切到「第二段」只換基本油門,看加力後哪裡會撞到上限.
   點選或拖曳曲線上的點;邊框的三角形也能拖:左邊是補速/減速起點,下方是油門下限 / 基本油門 / 上限. 改完按上方的儲存.</div>
  <div class="seg profseg" id="profSeg2"></div>
  <div class="seg phseg" id="cvPhase"><button data-ph="1" class="on">第一段</button><button data-ph="2">第二段</button></div>
  <div class="cvwrap">
   <div class="cvchart"><svg id="cvSvg" viewBox="0 0 440 366" role="img" aria-label="角度補償曲線"></svg></div>
   <div class="cvside">
    <details class="gesture"><summary><b>手勢說明</b> <span class="sub">(在曲線圖上)</span></summary>
     <div><span class="gk">單指</span>點選或拖曳點與三角形,網頁不會跟著動</div>
     <div><span class="gk">雙指捏合</span>放大 / 縮小網頁(沒放大時也可以)</div>
     <div><span class="gk">放大後雙指拖</span>移動網頁,看其他地方</div>
     <div class="sub">要單指捲動網頁,手指放在曲線圖以外的地方.</div></details>
    <div class="cvpanel" id="curvePanel"></div>
   </div>
  </div>
 </div>
 <details class="card"><summary><b>全部點的數值</b>(不方便拖曳時用)</summary><div id="curveCard"></div></details>
</section>

<section id="log" hidden>
 <div class="card">
  <h2>G 力與姿態紀錄</h2>
  <div class="cnote">板子一直記錄最近 10 分鐘(每 0.1 秒一筆,重新通電清除),飛完打開來看. 訂門檻的作法:先關閉提早降落,飛幾個特技看「總 G」與「Z 抖動」最高多少,再看地面滑行的抖動,門檻訂在兩者之間. 點或拖圖表看該時刻的數值;下方最大值只算目前畫面範圍.</div>
  <div class="row" style="margin-top:2px"><span class="seg" id="logWin"><button data-s="60">1 分</button><button data-s="180" class="on">3 分</button><button data-s="600">10 分</button></span>
   <button class="b" id="btnLogPause">暫停更新</button><span class="sub" id="logInfo"></span></div>
  <div class="grid g3" id="logStats"></div>
 </div>
 <div class="card" style="padding:6px 6px">
  <div class="sub" id="logCursor" style="min-height:2.8em;padding:0 6px"></div>
  <canvas id="logCanvas" style="width:100%;height:520px;display:block;touch-action:pan-y"></canvas>
 </div>
</section>

<section id="set" hidden>
 <div id="setCards"></div>
 <div class="card"><div class="row" style="margin:0"><button class="b danger sm" id="btnSharedDef">共用設定回預設</button><span class="sub" style="flex:1 1 150px">含安裝,電變頁的設定;按儲存才寫入. 不影響 WiFi.</span></div></div>
</section>

<section id="inst" hidden>
 <div class="card">
  <h2>感測器安裝方位<span class="h2r"><button class="b sm" id="btnOrientDef">方位回預設</button></span></h2>
  <div class="cnote">裝機時設定一次:選晶片的哪一軸朝機頭,哪一軸朝機背(座艙頂). 模組板上印有 X,Y 箭頭;Z 軸垂直板面,朝元件那面為 +Z. 朝左翼由兩軸自動決定(向心力在這個方向).
   裝好後把飛機擺成平飛姿勢,用「角度修正」讓控制使用的角度讀到 0°. 出廠:+X 朝機頭,+Z 朝機背,修正 0°. 改完按上方的儲存.</div>
  <div class="inst-views">
   <figure><figcaption>側視 <span class="sub">站在圓心看,左翼朝你</span></figcaption><svg id="instSide" viewBox="-160 -100 320 200" role="img" aria-label="側視安裝方位圖"></svg></figure>
   <figure><figcaption>後視 <span class="sub">站在機尾往機頭看</span></figcaption><svg id="instRear" viewBox="-160 -100 320 200" role="img" aria-label="後視安裝方位圖"></svg></figure>
  </div>
  <div class="sub" style="margin:0 0 4px">檢查:<b>抬機頭</b>,側視圖機頭也要抬起;<b>抬左翼</b>,後視圖左翼也要抬起. 反了就是軸選錯.</div>
  <div class="axrow">
   <label><span class="axk nose">■</span> 朝機頭<select id="selNose"></select></label>
   <label><span class="axk up">■</span> 朝機背<select id="selUp"></select></label>
   <span><span class="axk left">■</span> 朝左翼 <b id="axisY">--</b> <span class="sub">(自動)</span></span>
  </div>
  <div class="live"><span>控制使用 <b id="setPitch">--</b></span><span class="sub">晶片原始 <b id="setRaw">--</b></span><span id="instDefState" style="margin-left:auto"></span></div>
  <div id="setOrientCards"></div>
  <div class="row" style="margin-bottom:0"><span class="sub">圖示機頭</span><span class="seg" id="noseSeg"><button data-v="0">朝左(逆時針飛)</button><button data-v="1">朝右(順時針飛)</button></span></div>
 </div>
 <div id="instCards"></div>
</section>

<section id="esc" hidden>
 <div id="escCards"></div>
 <div class="card" id="manCard">
  <h2>手動輸出</h2>
  <div class="cnote">用滑桿直接控制電變:測馬達轉向,確認油門大小,也可以手動校正電變. 只在待機或飛行結束時可用.
   安全機制:解鎖後一律從最低油門開始;離開這一頁,切到別的 App 或斷線,0.5 秒內自動回最低並上鎖.</div>
  <div class="man-read"><span class="pill" id="manPill">已上鎖</span><b id="manOut">-- µs</b><span class="sub" id="manPct"></span></div>
  <label class="chk"><input type="checkbox" id="manProp"> 螺旋槳已拆除,解鎖後馬達會照滑桿轉動</label>
  <div class="row"><button class="b pri" id="btnManUnlock" disabled>解鎖手動輸出</button><button class="b danger" id="btnManLock" hidden>上鎖(回最低油門)</button></div>
  <input type="range" id="manSlider" min="1000" max="2000" step="5" value="1000" disabled class="man-slider">
  <div class="man-btns"><button class="b" data-d="min">最低</button><button class="b" data-d="-50">−50</button><button class="b" data-d="-10">−10</button><button class="b" data-d="10">+10</button><button class="b" data-d="50">+50</button><button class="b" data-d="max">最高</button></div>
 </div>
 <div class="card" id="calCard">
  <h2>電變校正精靈(自動)</h2>
  <div class="cnote">讓電變學習油門行程:通電當下輸出最高油門,保持一段時間再切最低,板子自動完成.
   只有「拔電再接電」才會進入校正,軟體重開不算(那時電變可能已解鎖,最高油門等於全速),而且會直接取消校正.
   按下後 <b>10 秒內</b>沒拔電也會自動取消,免得哪天裝著螺旋槳接電池就全速.
   板子用 USB 供電而電變另外接電池時,改用上面的手動輸出:先解鎖推到最高,再接電變電池,聽到提示音拉到最低.</div>
  <details class="subd"><summary>操作步驟</summary>
  <ol class="steps">
   <li>確認「電變脈寬」是你要的範圍,並且已按儲存(校正用存檔裡的值).</li>
   <li>拆下螺旋槳,<b>手先放在電池接頭旁</b>,勾選下方確認,按「下次通電進入校正」.</li>
   <li><b>10 秒內拔掉電池</b>(板子與電變都斷電),再重新接上. 板子一開機就輸出最高油門. 超過 10 秒沒拔會自動取消,要重按.</li>
   <li>保持設定的秒數後自動切到最低油門,電變發出確認音就完成. 各廠牌提示音見下方說明.</li>
   <li>校正完不會自動倒數,要飛請再重新通電一次.</li>
  </ol></details>
  <div id="calParam"></div>
  <div class="live" style="border:1px solid var(--warn)"><span class="pill warn">注意</span><span>按下「下次通電進入校正」後,<b>10 秒內要拔掉電池</b>再接上,沒拔會自動取消. 手先放在電池接頭旁再按.</span></div>
  <div class="man-read"><span class="pill" id="calPill">--</span><span class="sub" id="calText"></span></div>
  <div class="row" style="margin-bottom:0"><label class="chk" style="margin:0"><input type="checkbox" id="calProp"> 螺旋槳已拆除</label>
   <button class="b pri" id="btnCalOn" disabled style="margin-left:auto">下次通電進入校正</button><button class="b" id="btnCalOff" hidden style="margin-left:auto">取消校正</button></div>
 </div>
 <details class="card" id="brandCard">
  <summary><b>各廠牌校正說明</b> <span class="sub">(點開,19 款)</span></summary>
  <div class="sub" style="margin-top:6px">依官方說明書整理(2026-09 查證),點開看步驟與出處. <b>很多電變「最高油門上電」停太久會進入設定模式</b>,聽到確認音就要拉到最低. 保持秒數是依說明書推算的建議值,從板子與電變同時通電起算;不確定時用手動輸出邊聽邊做最保險. 清單沒有的型號以電變說明書為準.</div>
  <div id="brandList"></div>
 </details>
</section>

<section id="sys" hidden>
 <div class="card">
  <h2>網路狀態</h2>
  <div class="grid">
   <div class="stat"><div class="k">模式</div><div class="v" id="netMode">--</div></div>
   <div class="stat"><div class="k">IP 位址</div><div class="v" id="netIp">--</div></div>
   <div class="stat"><div class="k">網址</div><div class="v" id="netHost">--</div></div>
   <div class="stat"><div class="k">訊號強度</div><div class="v" id="netRssi">--</div></div>
  </div>
 </div>
 <div class="card">
  <h2>WiFi 設定</h2>
  <div class="cnote">開機先連家用 WiFi;連不上或名稱留空,就開自身熱點 <b id="apName"></b>(網址 192.168.4.1). 儲存後重新開機生效.
   <br><b>熱點名稱</b>:開頭固定,後面可空白,或接字分辨同場的飛機(例如 3 → HappySuperGG_Plane3),最多 14 個英數字(中文一字算 3 個).
   <br><b>熱點密碼</b>:出廠 12345678,建議改掉,別人才不能連進來改設定. 8~63 個英數字或半形符號,分大小寫. 忘記就用下面的救援回出廠.
   <br><b>發射功率</b>:拖動立即生效,方便比較連線品質;15 秒內要按上方「保持」,沒按會退回.
   <br><b>設定保護</b>:儲存並重新開機後要按上方「保持」;WiFi 就緒後 3 分鐘沒按,自動改回上一次的設定.
   <br><b>完全連不上時救援</b>:電池接上後 5 秒內拔掉,連續 3 次,WiFi 回出廠(熱點 HappySuperGG_Plane,密碼 12345678). 飛行設定不受影響.</div>
  <div class="wgrp"><div class="wgt">自身熱點(AP):手機直接連飛機</div>
   <div class="row"><label for="fApSfx">熱點名稱</label><span class="apfix" id="apPrefix">HappySuperGG_Plane</span><input type="text" id="fApSfx" autocomplete="off" placeholder="(可空白)" style="flex:1 1 70px;min-width:0"></div>
   <div class="sub" id="apHint" style="margin:-2px 0 2px 104px"></div>
   <div class="row"><label for="fApPw">熱點密碼</label><input type="password" id="fApPw" maxlength="63" autocomplete="off"><button class="b sm" id="btnApPwShow">顯示</button></div>
  </div>
  <div class="wgrp"><div class="wgt">家用 WiFi:飛機連到家裡的路由器</div>
   <div class="row"><label for="fSsid">家用 WiFi<span class="lsub">名稱(SSID)</span></label><input type="text" id="fSsid" maxlength="32" autocomplete="off" placeholder="手機 WiFi 清單上的名稱,留空 = 只用熱點"></div>
   <div class="sub" style="margin:-2px 0 4px 104px">只能連 2.4GHz 的 WiFi(不支援 5GHz),也不支援隱藏名稱的 WiFi.</div>
   <div class="row"><label for="fPw">家用 WiFi<span class="lsub">密碼</span></label><input type="password" id="fPw" maxlength="63" autocomplete="off"><button class="b sm" id="btnPwShow">顯示</button></div>
  </div>
  <div class="row"><label for="fHost">裝置名稱</label><input type="text" id="fHost" maxlength="31" autocomplete="off"><span class="sub">.local</span></div>
  <div class="row" title="連不上家用 WiFi 幾秒後改開自身熱點"><label for="fTmo">等待秒數</label><input type="number" id="fTmo" min="10" max="120" style="flex:0 0 64px"><span class="sub">秒後開熱點</span>
   <label class="chk" style="margin:0 0 0 auto"><input type="checkbox" id="fForce"> 一律用熱點</label></div>
  <div class="row"><label for="fTxp">發射功率</label><input type="range" id="fTxp" min="2" max="20" step="1"><b id="txpVal">--</b></div>
  <div class="sub" id="txpWarn" style="margin:-2px 0 6px 104px">⚠ 功率開太高反而會連不上 WiFi,常用 5 dBm.<br>連不上時:電池接上 5 秒內拔掉,連續 3 次,WiFi 設定回出廠.</div>
  <div class="row" style="margin-bottom:0"><button class="b pri" id="btnWifiSave">儲存 WiFi 設定</button><button class="b" id="btnReboot">重新開機</button></div>
  <div class="msg" id="wifiMsg"></div>
 </div>
 <div class="card" id="fwCard">
  <h2>韌體更新</h2>
  <div class="cnote">板子連上家用 WiFi(要能上網)後按「檢查更新」,確認後板子自己下載安裝,完成自動重新開機.
   <br><b>安全保護</b>:只有待機時能更新,更新中不能起飛;檔案大小或檢查碼不對就放棄,目前韌體不變.
   板子重開後,<b>開著的網頁會自動確認</b>(不用按按鈕);1 分鐘內沒有網頁連上(例如新韌體連不上 WiFi)就退回舊版. 確認前不能起飛,斷電或重開也會退回.
   <b>為什麼要確認</b>:板子自己只知道開機了,由網頁確認才能保證更新完你還控制得到它. 所以<b>更新時請保持網頁開著</b>:螢幕關掉或切到別的 App 網頁會暫停,超過 1 分鐘才回來就退回舊版(再更新一次即可).
   <br>更新會重新開機,沒儲存的設定會不見,請先儲存;重開後不會自己倒數. 下方「手動上傳韌體檔」可上傳別人給的 .bin,保護方式相同.</div>
  <div class="live" id="fwPendBox" hidden><span class="pill warn">新韌體待確認</span><span id="fwPendText" class="sub"></span></div>
  <div class="live" id="fwRbBox" hidden><span class="pill bad">已退回舊版</span><span id="fwRbText" class="sub"></span></div>
  <div class="grid g3">
   <div class="stat"><div class="k">韌體版本</div><div class="v" id="fwVer" style="font-size:14px">--</div></div>
   <div class="stat"><div class="k">開機時間</div><div class="v" id="uptime">--</div></div>
   <div class="stat"><div class="k">可用記憶體</div><div class="v" id="heap">--</div></div>
  </div>
  <div class="sub" style="margin:2px 0">編譯 <span id="build">--</span></div>
  <div class="row"><button class="b pri" id="btnFwCheck">檢查更新</button><span class="sub" id="fwCheckText" style="flex:1 1 150px"></span></div>
  <div id="fwRemote" hidden>
   <div class="fwnotes" id="fwNotes"></div>
   <div class="row"><button class="b pri" id="btnFwInstall">更新</button><span class="sub" id="fwInstallText" style="flex:1 1 150px"></span></div>
  </div>
  <progress id="fwDlProg" max="100" value="0" hidden></progress>
  <details class="subd"><summary>手動上傳韌體檔</summary>
   <div class="row"><input type="file" id="fwFile" accept=".bin" style="flex:1 1 160px;min-width:0;font-size:13px"><button class="b" id="btnFw">上傳更新</button></div>
   <progress id="fwProg" max="100" value="0" hidden></progress>
   <div class="msg" id="fwMsg"></div>
  </details>
 </div>
</section>

<section id="bak" hidden>
 <div class="live" id="bkDirty" hidden style="margin:0 0 8px"><span class="pill bad">有未儲存的變更</span><span class="sub">請先按上方的儲存或放棄,才能產生或套用備份碼.</span></div>
 <div class="card" id="bkCard">
  <h2>產生備份碼</h2>
  <div class="cnote">勾選要複製的內容,按「產生並複製」,得到一串 LP 開頭的文字,存在 LINE 或記事本,也可以傳給朋友.
   <br><b>碼裡只有你勾的東西</b>,沒勾的部分對方不會被改到:只想分享飛法就只勾那一組風格,不會蓋掉他的安裝與電變設定.
   <br>六組風格全勾的碼,套用時才會一併切換「飛行使用哪一組」. 勾越少,碼越短.</div>
  <div class="bkhd"><b>① 勾選要複製的內容</b><span class="bkq"><a href="#" id="bkSelAll">全選</a><a href="#" id="bkSelTest">只選測試</a><a href="#" id="bkSelNone">全部取消</a></span></div>
  <div class="bkprof" id="bkProfBox">
   <div class="bkpt">計時器風格<button class="ib" type="button" title="說明">ⓘ</button></div>
   <div class="bkhint">每一組包含計時器頁(油門,時間,起飛油門,換段,降落)與角度補償頁(曲線,油門上下限). 點一下亮起來就是要複製.</div>
   <div class="bksel" id="bkSel"></div>
  </div>
  <div class="bkgt">其他設定</div>
  <div class="bksecs" id="bkSecs"></div>
  <div class="bkhd"><b>② 產生</b></div>
  <div class="row" style="margin-bottom:0"><button class="b pri" id="btnBkMake">產生並複製</button><span class="sub" id="bkMakeText" style="flex:1 1 150px"></span></div>
  <textarea class="bktext" id="bkOut" rows="4" readonly hidden></textarea>
  <div class="msg" id="bkMakeMsg"></div>
 </div>
 <div class="card">
  <h2>套用備份碼</h2>
  <div class="cnote">貼上 LP 開頭的備份碼,板子會先檢查,並告訴你碼裡有哪些內容.
   <br>按「套用」後,碼裡有的部分蓋掉目前設定,沒有的不動. 套用完還沒存:確認後按上方的儲存,不要就按放棄.
   <br><b>WiFi 例外</b>:碼裡有 WiFi 時,套用當下就存起來(按放棄也不會退回),重新開機才生效;重開後 3 分鐘內要按「保持」.
   <br><b>套用後請逐頁檢查</b>,尤其感測器方位,角度修正,電變脈寬與收輪行程:每台飛機的安裝不一樣. 較舊的碼也能用.</div>
  <textarea class="bktext" id="bkIn" rows="4" inputmode="none" placeholder="長按這裡 → 貼上 LP 開頭的備份碼" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false"></textarea>
  <div id="bkPick" hidden>
   <div class="bkhd"><b>要套用的內容</b><span class="sub">點一下取消;灰色打 ✕ 的不會套用,保持你原本的設定</span></div>
   <div class="bkprof" id="bkPickProfBox">
    <div class="bkpt">計時器風格<button class="ib" type="button" title="說明">ⓘ</button></div>
    <div class="bkhint">每一組包含計時器頁(油門,時間,起飛油門,換段,降落)與角度補償頁(曲線,油門上下限). 套用到同一個位置(碼裡的 A 蓋掉你的 A).</div>
    <div class="bksel bkpick" id="bkPickSel"></div>
   </div>
   <div class="bkgt" id="bkPickST">其他設定</div>
   <div class="bksecs" id="bkPickSecs"></div>
   <div class="bkd" id="bkPickNote" style="margin:2px 0 4px"></div>
  </div>
  <div class="row" style="margin-bottom:0"><button class="b pri" id="btnBkApply" disabled>套用</button><button class="b" id="btnBkClear">清空</button></div>
  <div class="msg" id="bkMsg"></div>
 </div>
</section>
</main>
<footer class="credit"><span><span class="ck">設計開發者：</span><span class="gg" aria-label="SuperGG"><i style="--i:0">S</i><i style="--i:1">u</i><i style="--i:2">p</i><i style="--i:3">e</i><i style="--i:4">r</i><i style="--i:5">G</i><i style="--i:6">G</i></span></span><span><span class="ck">Line社群：</span><span class="line">RotorFlightTW</span></span></footer>
<div class="toast" id="toast" hidden></div>
<script>
const $=id=>document.getElementById(id);
let pane='mon',META=null,VALS=null,editP=0,STATUS=null;
const CODES={startauto:'目前是「上電後直接倒數」模式:要飛請拔掉電池再接上(每次通電倒數一次).',startstate:'只有待機或飛行結束時可以開始.',
 startblock:'剛取消起飛或剛停止馬達,稍等幾秒再開始.',startbusy:'手動輸出或電變校正進行中,先上鎖或等校正完成再開始.',cancelstate:'只有等待放穩或倒數中可以取消;馬達運轉中請用緊急停止.',start:'已開始.',saved:'已儲存.',pwshort:'密碼至少 8 碼(開放網路請留空).',apsfxlong:'熱點名稱後面接的字太長:最多 14 個英數字(中文一字算 3 個).',
 apsfxspace:'熱點名稱後面接的字,頭尾不能是空白(手機上看不出來,容易連錯).',apsfxbad:'熱點名稱後面接的字含有不能用的字元.',ssidlong:'WiFi 名稱太長.',
 pwlong:'密碼太長.',hostbad:'裝置名稱只能用英文,數字與連字號,且不可頭尾為連字號.',tmo:'等待秒數要在 10~120.',
 txp:'發射功率超出範圍.',savefail:'寫入失敗,請再試一次.',badform:'欄位不齊.',busy:'飛行中不能執行.',
 updated:'更新完成,重新開機中…',updatefail:'更新失敗,檔案可能不對.',reboot:'重新開機中…',
 fwnotours:'這個檔案不是線控飛機控制器的韌體(找不到身分標記),已放棄,目前韌體不變. 2026.09.14.16 和更早的版本沒有標記,不能用上傳的方式安裝.',
 fwchecking:'檢查中…',fwinstalling:'開始下載安裝,請勿斷電.',fwconfirmed:'新韌體已確認.',fwconfirmfail:'確認失敗,請重新整理網頁.',
 fwbusy:'更新作業進行中,請稍候.',fwpending:'目前的韌體還沒確認,請重新整理網頁後再試.',fwdirty:'有未儲存的設定,請先儲存或放棄(更新會重新開機).',
 fwstale:'版本資訊已經變了,請重新檢查更新.',fwnotnewer:'網站上的版本沒有比目前的新,不需要更新.',nosta:'要連上家用 WiFi(能上網)才能檢查更新,自身熱點模式沒有網路.',nomem:'記憶體不足,請重新開機後再試.',
 net:'連不上更新伺服器,請確認家用 WiFi 能上網.',http:'更新伺服器回應錯誤,請稍後再試.',nomanifest:'更新頁上還沒有韌體.',manifest:'更新資訊格式不對,請回報開發者.',
 toolarge:'韌體檔太大,裝不下.',url:'更新網址錯誤.',nofile:'找不到韌體檔(可能剛發布,幾分鐘後再試).',size:'下載的檔案大小不對,請稍後再試.',
 flashbegin:'無法開始寫入,請重新開機後再試.',flashwrite:'寫入失敗,目前韌體沒有改變.',flashend:'寫入檢查失敗,目前韌體沒有改變.',
 short:'下載中斷,目前韌體沒有改變,請再試一次.',timeout:'下載逾時,目前韌體沒有改變,請再試一次.',sha:'下載的檔案檢查碼不對,已放棄,目前韌體沒有改變.',
 locked:'起飛流程進行中,設定已鎖定.',range:'超出可調範圍.',order:'曲線的角度必須由水平往外依序排列,不可越過相鄰的點或死區.',
 minmax:'油門下限必須小於上限.',phasetime:'第一段時間必須比總飛行時間短.',takeofftime:'緩啟動加力秒數 + 起飛油門持續時間 + 1 秒過渡,要在第一段持續時間內結束.',
 appwshort:'熱點密碼至少 8 個字.',appwlong:'熱點密碼最多 63 個字.',appwspace:'熱點密碼頭尾不能是空白(看不出來,容易打錯).',appwbad:'熱點密碼只能用英文,數字與鍵盤上的半形符號(不能有中文或全形字).',axis:'朝機頭與朝機背不能是同一軸.',
 escrange:'100% 的脈寬至少要比 0% 大 100 µs.',pwmhz:'PWM 週期要比 100% 脈寬多 300 µs:頻率調低一點,或把 100% 脈寬調小.',twistdeg:'扭轉取消角度設 0(關閉)或至少 15 度.',wagdeg:'搖擺機尾停機角度設 0(關閉)或至少 15 度.',pulserange:'忽高忽低的高油門要比低油門至少高 10%.',gearrange:'舵機行程上限至少要比下限大 100 µs.',geartest:'已送出.',name:'名稱不能空白,也不能有換行等特殊字元.',key:'未知的參數.',value:'數值格式不對.',scope:'風格編號不對.',
 selected:'已設為飛行使用.',copied:'已複製,記得儲存.',defaults:'已回預設,按儲存才會寫入;按放棄變更可以救回.',reverted:'已放棄變更.',
 manualstate:'只有待機或飛行結束時可以手動輸出(倒數中請先取消倒數).',manuallow:'手動輸出要從最低油門開始.',
 calibdirty:'有未儲存的變更,請先儲存(校正用存檔裡的脈寬).',calibproto:'DShot 是數位油門,不需要校正行程.',
 calibon:'已設定:10 秒內拔掉電池再接上就開始校正,沒拔會自動取消.',caliboff:'已取消電變校正.',
 bkdirty:'有未儲存的變更,請先按上方的儲存或放棄.',bkprefix:'這不是備份碼(要 LP 開頭),已清空,請重新貼上.',
 bkcrc:'備份碼不完整或有錯字(可能少複製了一段),已清空,請重新複製整串再貼上.',bkver:'這個備份碼的格式比這台飛機的韌體新,請先到系統頁更新韌體.',
 bkfail:'產生備份碼失敗,請再試一次.',bksel:'要包含的內容至少選一項.',bknone:'全部都取消了,沒有東西可以套用.',namelocked:'「測試」這組名稱固定,不能改.'};
const PROFILE_TEST_INDEX=5;   // 「測試」組(與韌體 settings.h PROFILE_TEST_INDEX 一致):名稱鎖定,備份碼預設只選這組
const AXES=['晶片 +X','晶片 −X','晶片 +Y','晶片 −Y','晶片 +Z','晶片 −Z'];
const UNIT={pct:'%',cpct:'%',sec:'秒',min:'分鐘',deg:'°',g:'g',us:'µs',m:'公尺',num:'',hz:'Hz'};
// 參數標籤:[名稱, 單位種類, 說明]
const L={
 phase1Pct:['第一段基本油門','pct','第一段的油門,角度補償加在這上面.'],
 phase1Sec:['第一段持續時間','sec','馬達啟動後多久換到第二段. 要比總飛行時間短.'],
 phase2Pct:['第二段基本油門','pct','後段電池變弱,用較高的油門補回推力.'],
 flightSec:['總飛行時間','sec','馬達啟動後多久開始降落.'],
 takeoffRamp:['緩啟動加力秒數','sec','馬達從停止加到起飛油門的秒數,起飛不會猛衝. 起飛油門持續時間 0 時,是加到第一段油門.'],
 takeoffPct:['起飛油門','pct','緩啟動加到這個油門,維持設定的秒數後用 1 秒換到第一段. 持續時間 0 = 不使用.'],
 takeoffHold:['起飛油門持續時間','sec','維持起飛油門的秒數. 0 = 不使用(直接加到第一段油門). 緩啟動 + 這個秒數 + 1 秒要在第一段時間內.'],
 phaseRamp:['換段加力秒數','sec','換段選「有過渡」時,第一段加到第二段的秒數.'],
 noCompSec:['起飛後不補償','sec','起飛滑跑這段不補償. 後三點飛機停著就機頭朝上,免得被當成爬升而加油門.'],
 minPct:['飛行中油門下限','pct','補償後的油門不會低於這個值,兩段共用. 最低 10%.'],
 maxPct:['飛行中油門上限','pct','補償後的油門不會超過這個值,兩段共用.'],
 landingRamp:['降落減力秒數','sec','開始降落後,油門減到降落油門的秒數. 選忽高忽低時是忽高忽低持續的秒數,走完換降落油門. 0 = 直接換降落油門.'],
 landingPct:['降落油門','pct','降落時維持的油門,判定觸地才關馬達.'],
 pulseLow:['忽高忽低:低油門','pct','忽高忽低時的低油門. 至少比高油門低 10%.'],
 pulseHigh:['忽高忽低:高油門','pct','忽高忽低時的高油門. 先高後低.'],
 pulsePeriod:['忽高忽低週期','sec','一高一低合起來的秒數. 1 秒 = 高半秒,低半秒.'],
 wagStop:['搖擺機尾停機角度','deg','馬達運轉中抓著機尾左右搖擺,每次從一邊擺到另一邊超過這個角度,連續 3 個來回就關馬達. 0 = 關閉.'],
 upDb:['補速開始角度','deg','機頭朝上超過這個角度才開始補速.'],
 dnDb:['減速開始角度','deg','機頭朝下超過這個角度才開始減速.'],
 pitchTrim:['角度修正','deg','加到量到的角度上. 平飛姿勢讀到 +2° 就設 −2. 出廠 0.'],
 gestureG:['啟動手勢力道','g','機身水平時往機頭推超過這個力道才算啟動. 推一下看下方試推燈調整.'],
 armWait:['安全開關等待上限','min','起飛程序開始後這麼久沒按安全開關就取消,回到待機(飛機被碰到誤觸發時不會一直鎖著設定). 上電直接倒數模式取消後,要飛請拔電再接電.'],
 countdownSec:['起飛倒數秒數','sec','倒數完馬達啟動,也就是你走到手柄的時間. 從按過安全開關而且飛機放穩那一刻算起.'],
 disturbG:['外力門檻','g','倒數中晃動超過這個值,算有人碰到飛機. 碰一下看下方橘燈調整,有風時調大.'],
 startLevel:['起飛前水平限制','deg','機頭或滾轉超過這個角度就不起飛:手勢被拒絕,上電倒數暫停,等待放穩或倒數中則取消. 後三點飛機要設得比停放角度大. 原因看監看頁事件紀錄.'],
 twistCancel:['扭轉機尾取消起飛','deg','手勢起飛後抓機尾把飛機轉超過這個角度就取消. 0 = 關閉;放飛機容易誤觸就調大.'],
 twistBlock:['取消後暫停手勢','sec','扭轉取消後這段時間不接受手勢,放下飛機的撞擊才不會又觸發.'],
 disturbMode:['外力介入時','num',''],
 extendSec:['延長秒數','sec','外力介入後重新放穩,倒數加上這個秒數. 最多加到「起飛倒數秒數 +10 秒」.'],
 touchdownG:['降落觸地衝擊門檻','g','降落中觸地衝擊超過這個值就關馬達. 在監看頁輕敲飛機,看「最近觸地衝擊」決定.'],
 touchdownStill:['觸地靜止判定','sec','降落中靜止這麼久也算觸地(輕輕著陸時).'],
 earlyLandVib:['Z 軸抖動門檻','g','機背方向的抖動. 到紀錄頁看:要高於特技時,低於地面滑行時.'],
 earlyLandHold:['抖動持續秒數','sec','抖動持續這麼久才觸發. 特技急轉的抖動很短,撐不過去.'],
 earlyLandTilt:['正飛水平容許角度','deg','機頭與滾轉都在這個角度內才算正飛水平,倒飛或爬升不會觸發.'],
 earlyLandArm:['起飛後幾秒才啟用','sec','起飛後這段時間不偵測,避開滑跑的顛簸.'],
 landingTimeout:['降落保險時間','sec','減力走完後再過這麼久沒判定觸地,一樣關馬達. 降落最長 = 減力秒數 + 這個秒數.'],
 crashEnable:['撞擊斷電','num',''],
 crashG:['撞擊門檻','g','飛行中衝擊連續 10 毫秒超過這個值就關馬達. 特技直角彎可達 8~10g,不要設太低.'],
 lineLength:['線長','m','扣除繞圈向心力用,大概的值即可.'],
 lapSec:['單圈秒數','sec','飛一圈大約幾秒,和線長換算飛行速度.'],
 calibHold:['最高油門保持秒數','sec','通電後輸出最高油門多久才切到最低. 出廠 3 秒(電變自己開機要約 1 秒,太短來不及記住,太長有些會進入設定模式). 各廠牌建議見下方. 沒聽到「已記住」提示音就調長,聽到設定模式音就調短.'],
 motorPoles:['馬達極數','num','馬達的磁鐵數(不是線圈槽數),只用來顯示轉速. 常見外轉子 14 極.'],
 escPwmHz:['PWM 頻率','hz','每秒送幾個油門脈衝. 出廠 100Hz;電變抖動或不解鎖就改 50Hz(所有電變都支援). 電變有標明支援才調高. 頻率越高,100% 脈寬能設的上限越低.'],
 gearRetractSec:['起飛後幾秒收輪','sec','馬達啟動後多久收輪. 要比離地時間長一點.'],
 gearTravelSec:['舵機速度','sec','輪子放下到收起的秒數,慢一點比較不傷收腳機構. 0 = 舵機最快.'],
 gearMinUs:['舵機行程下限','us','舵機一端的位置. 出廠 1400:先按「試收輪」確認方向,再慢慢加大到剛好收到底,不要頂死.'],
 gearMaxUs:['舵機行程上限','us','舵機另一端的位置. 出廠 1600. 至少要比下限大 100 µs.'],
 escMinUs:['油門 0% 脈寬','us','油門 0% 送出的脈寬,標準電變 1000. ⚠ 待機時就輸出這個值,調高馬達會立刻轉,要先勾「螺旋槳已拆除」.'],
 escMaxUs:['油門 100% 脈寬','us','油門 100% 送出的脈寬,標準電變 2000. 改過建議重新校正電變.']
};
// 計時器頁三組參數放同一張卡,用小標題分組(r46:原本三張卡,卡片邊框與標題佔版面)
const PROF_LAYOUT=[
 {t:'起飛',k:['takeoffRamp','takeoffPct','takeoffHold','noCompSec']},
 {t:'飛行時間軸(從馬達開始轉算起)',k:['phase1Pct','phase1Sec','phaseMode','phaseRamp','phase2Pct','flightSec']},
 {t:'降落',k:['landingMode','landingRamp','pulseHigh','pulseLow','pulsePeriod','landingPct','landingBuzz']}
];
const PROF_NOTE='時間都從馬達開始轉算起. 總飛行時間到了,或觸地提早降落(設定頁),就開始降落;降落期間不補償. 油門上下限在角度補償頁.';
const SET_LAYOUT=[
 {t:'啟動與倒數',k:['gestureEnable','startLevel','gestureG','twistCancel','twistBlock','armSwitchOff','armWait','countdownSec','disturbG','disturbMode','extendSec'],
  n:'推一下飛機或按上方「開始起飛程序」→ 飛機放穩 → 按安全開關 → 倒數 → 馬達啟動. 開關放穩前後按都可以,超過等待上限沒按就取消. 倒數中可按「取消倒數」或扭轉機尾取消.'},
 {t:'觸地提早降落',k:['earlyLand','earlyLandVib','earlyLandHold','earlyLandTilt','earlyLandArm'],n:'想提早結束時,讓飛機正飛水平貼地滑行,機輪彈跳的抖動持續一段時間就開始降落. 門檻參考「紀錄」頁的實際數值.',id:'earlyCard'},
 {t:'降落與撞擊',k:['touchdownG','touchdownStill','landingTimeout','crashEnable','crashG'],n:'降落中任一成立就關馬達:觸地衝擊超過門檻,完全靜止,或滑行抖動持續達標(用提早降落的抖動設定,不管有沒有開啟). 減力走完才開始判斷,都沒成立就等保險時間到.'},
 {t:'強制停機',k:['wagStop'],n:'馬達運轉中(起飛後到降落)人在飛機旁要關馬達:長按安全開關 2 秒,或抓著機尾左右搖擺 3 個來回. 長按開關一定有效(馬達啟動後開關要先放開過,短路跳線的開關不會誤關). 飛行中機尾只會往同一邊轉,不會誤觸搖擺停機.'},
 ];
const INST_LAYOUT=[
 {t:'飛行速度',k:['lineLength','lapSec'],n:'姿態計算要扣掉繞圈的向心力,用線長與單圈秒數換算速度. 大概填對即可.',id:'speedCard'},
 {t:'機輪收腳',k:['gearEnable','gearRetractSec','gearTravelSec','gearMinUs','gearMaxUs','gearReverse'],id:'gearCard',
  n:'舵機訊號線接 GPIO3. 馬達啟動後到設定秒數收輪,開始降落減力時放輪;馬達一停(緊急停止,撞擊斷電)立即放輪. 開機,待機,倒數中一律放下. 所有計時器共用.'},
 {t:'蜂鳴器',k:['buzzerLow'],id:'buzzCard',
  n:'蜂鳴器訊號接 GPIO7,與控制器共地. 開機就緒響「滴滴」;等按安全開關時每 2.5 秒一聲長音;倒數時短音越來越急,最後 3 秒連續響到馬達啟動. 切換立即生效.'}
];
const ESC_LAYOUT=[
 {t:'輸出協定',k:['escProtocol','escPwmHz','escRpm','motorPoles'],id:'protoCard',n:'一般電變用 PWM(出廠 100Hz). 開源韌體電變(BLHeli_S,Bluejay,BLHeli_32,AM32)可選 DShot:數位油門,不用校正,也不看下面的脈寬. 換協定或頻率要<b>儲存後重新開機</b>,電變也要重新通電.'},
 {t:'電變脈寬',k:['escMinUs','escMaxUs'],n:'油門 0% 與 100% 對應的脈寬,出廠 1000 / 2000 µs. 改過建議重新校正電變.'}
];

async function poll(url,opt){
 const c=new AbortController(),t=setTimeout(()=>c.abort(),4000);
 try{const r=await fetch(url,Object.assign({signal:c.signal},opt||{}));return await r.json()}
 finally{clearTimeout(t)}
}
function post(url,data){
 return poll(url,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(data||{})});
}
let toastTimer=0;
function toast(text,bad){const e=$('toast');e.textContent=text;e.className='toast'+(bad?' bad':'');e.hidden=false;
 clearTimeout(toastTimer);toastTimer=setTimeout(()=>e.hidden=true,bad?4500:2200)}
function msg(id,ok,code){const e=$(id);e.className='msg '+(ok?'ok':'bad');e.textContent=CODES[code]||code}
function pill(id,cls,text){const e=$(id);e.className='pill '+cls;e.textContent=text}
function fmtStep(v){return v>=1?String(Math.round(v)):String(v)}
function decOf(fine){return fine>=1?0:(fine>=0.1?1:2)}
function pctToUs(p){const s=VALS.shared;return Math.round(s.escMinUs+(s.escMaxUs-s.escMinUs)*Math.min(100,Math.max(0,p))/100)}
function fmtDur(s){s=Math.round(s);return s>=60?`${Math.floor(s/60)} 分 ${s%60} 秒`:''}

// --- 參數元件:[−] 數值 [+] ---
// 按一下走一格細調;按住 0.4 秒後開始連續走,越按越快,約 2 秒後改用粗調步進(GG 2026-09-14:原本大小四顆鈕連按會變成畫面放大).
// 按住期間框內每格更新,板子每 0.4 秒送一次(不是每格都送),放開再送最後的值.
// 板子拒絕(例如第一段時間加到超過總飛行時間)就停在最後一個被接受的值並顯示原因,不會整段退回起點.
// 手指按下後滑動(捲頁)瀏覽器會送 pointercancel:還沒開始連續走就當作沒按;已經在連續走就送出目前顯示的值.
const HOLD_DELAY_MS=400,HOLD_COARSE_AFTER=15,HOLD_SEND_MS=400;
function holdInterval(n){return n>=HOLD_COARSE_AFTER?120:Math.max(60,200-n*12)}
const WIDGETS=[];
function metaOf(scope,key){return META[scope==='s'?'shared':'profile'][key]}
function valOf(scope,key){return VALS[scope==='s'?'shared':'profile'][key]}
function extraText(scope,key,v){
 const kind=(L[key]||[])[1];
 if(kind==='pct')return pctToUs(v)+' µs';
 if(kind==='sec')return fmtDur(v);
 return '';
}
function labHtml(label,hint,withExtra){
 return `<div class="lab"><span class="nm">${label}</span>${hint?'<button class="ib" type="button" title="說明">ⓘ</button>':''}`+
  (withExtra?'<div class="extra"></div>':'')+(hint?`<div class="hint">${hint}</div>`:'')+'</div>';
}
function wireHint(el){const b=el.querySelector('.ib');if(b)b.onclick=()=>el.classList.toggle('showhint')}
function makeParam(scope,key,label,hint,kind){
 const m=metaOf(scope,key),el=document.createElement('div');
 const def=L[key]||[key,'num',''];label=label||def[0];hint=hint===undefined?def[2]:hint;kind=kind||def[1];
 el.className='prm';
 // 緊湊版面:名稱(說明收進 ⓘ,換算值放名稱下方)與按鈕排同一列
 el.innerHTML=labHtml(label,hint,true)+`<div class="ctl">`+
  `<button class="b st" type="button" data-d="-1" title="按一下 −${fmtStep(m[2])},按住連續減">−</button>`+
  `<input class="val" inputmode="decimal"><span class="unit">${UNIT[kind]||''}</span>`+
  `<button class="b st" type="button" data-d="1" title="按一下 +${fmtStep(m[2])},按住連續加">+</button></div>`;
 wireHint(el);
 const inp=el.querySelector('.val'),w={scope,key,el,inp,kind,m,hold:null};
 const dec=decOf(m[2]);
 const stepFrom=(cur,d,n)=>{const st=(n>=HOLD_COARSE_AFTER&&m[3]>m[2])?m[3]:m[2];
  let v=Math.round((cur+d*st)/m[2])*m[2];v=Math.min(m[1],Math.max(m[0],v));return Number(v.toFixed(dec))};
 const showPend=v=>{inp.value=v.toFixed(dec);el.querySelector('.extra').textContent=extraText(scope,key,v)};
 // 快速連點時上一格可能還沒送到板子:以「最後送出的值」為基準,不然第二下會讀到舊值而少走一格
 const base=()=>w.pend!=null?w.pend:Number(valOf(scope,key));
 const commit=(v,d)=>{const cur=base();
  if(v===cur){toast(d>0?'已到上限.':'已到下限.');renderWidgets();return}
  w.pend=v;showPend(v);
  setParam(scope,key,v).then(()=>{if(w.pend===v)w.pend=null;renderWidgets()})};
 const pid=()=>scope==='s'?'s':editP;
 // 按住中送出目前值(排在 setParam 同一條佇列,順序不會亂). 被拒絕 → 停在最後接受的值;連線失敗先不管,放開時會再送.
 const holdSend=h=>{h.busy=true;h.sent=Date.now();const v=h.v;
  chain=chain.then(async()=>{let r=null;try{r=await post('/api/set',{p:pid(),k:key,v:v})}catch(e){}
   h.busy=false;if(!r)return;
   if(r.ok){h.ok=v;return}
   if(!h.rej){h.rej=true;toast(CODES[r.code]||r.code,true)}
   clearTimeout(h.tm);h.v=h.ok;if(w.hold===h)showPend(h.ok)})};
 const endHold=send=>{const h=w.hold;if(!h)return;w.hold=null;clearTimeout(h.tm);h.btn.classList.remove('on');
  if(!send){renderWidgets();return}
  if(h.n===0){commit(stepFrom(h.v,h.d,0),h.d);return}   // 沒有連續走 = 按一下
  if(h.v===h.start&&!h.busy){toast(h.d>0?'已到上限.':'已到下限.');renderWidgets();return}
  w.pend=h.v;
  chain=chain.then(async()=>{const v=h.rej?h.ok:h.v;   // 送最後的值(期間被拒絕就不再送)
   if(v!==h.ok){try{const r=await post('/api/set',{p:pid(),k:key,v:v});if(!r.ok)toast(CODES[r.code]||r.code,true)}catch(e){toast('連線失敗,請再試一次.',true)}}
   w.pend=null;await loadVals()})};
 el.querySelectorAll('.ctl .st').forEach(b=>{
  const d=Number(b.dataset.d);
  b.onpointerdown=e=>{if(e.button>0)return;endHold(false);
   const v0=base(),h={btn:b,d,n:0,v:v0,start:v0,ok:v0,sent:0,busy:false,rej:false,tm:0};w.hold=h;b.classList.add('on');
   const tick=()=>{if(w.hold!==h||h.rej)return;const nv=stepFrom(h.v,d,h.n);h.n++;
    if(nv===h.v){h.tm=setTimeout(tick,200);return}   // 到頂就停在那裡
    h.v=nv;showPend(nv);
    if(!h.busy&&Date.now()-h.sent>=HOLD_SEND_MS)holdSend(h);
    h.tm=setTimeout(tick,holdInterval(h.n))};
   h.tm=setTimeout(tick,HOLD_DELAY_MS)};
  b.onpointerup=()=>endHold(true);
  b.onpointerleave=()=>{if(w.hold&&w.hold.btn===b)endHold(w.hold.n>0)};
  b.onpointercancel=()=>{if(w.hold&&w.hold.btn===b)endHold(w.hold.n>0)};
  b.oncontextmenu=e=>e.preventDefault();   // 長按不要跳出選單
  // 鍵盤 Enter/空白鍵或程式呼叫 click() 沒有 pointer 事件(detail = 0):走一格
  b.onclick=e=>{if(e.detail===0)commit(stepFrom(base(),d,0),d)};
 });
 // 輸入框:空白或不是數字 → 不送,顯示回目前的值(r37 以前空白會被 Number('') 當成 0 送出);
 // 送出後不管成功或被拒絕,都把框內顯示換回板子上的實際值(按 Enter 時焦點還在框內,renderWidgets 不會更新它)
 const showCur=()=>{inp.value=Number(valOf(scope,key)).toFixed(decOf(m[2]))};
 inp.onchange=()=>{const t=inp.value.trim(),v=Number(t);
  if(t===''||!isFinite(v)){toast('請輸入數字.',true);showCur();return}
  setParam(scope,key,v).then(showCur)};
 inp.onkeydown=e=>{if(e.key==='Enter')inp.blur()};
 WIDGETS.push(w);
 return el;
}
function makeSelect(scope,key,label,options,hint){
 const el=document.createElement('div');el.className='prm';
 el.innerHTML=labHtml(label,hint,false)+`<div class="ctl"><select>${options.map((o,i)=>`<option value="${i}">${o}</option>`).join('')}</select></div>`;
 wireHint(el);
 const sel=el.querySelector('select');sel.onchange=()=>setParam(scope,key,sel.value);
 WIDGETS.push({scope,key,el,sel});
 return el;
}
// 忽略安全開關(GG 2026-09-14):停用要展開風險說明,三項全部打勾才送出;恢復使用一鍵. 都要按儲存才生效.
function makeArmOff(){
 const el=document.createElement('div');el.className='prm';el.id='armOffBox';
 el.innerHTML=`<div class="aorow"><span>安全開關</span><b id="armOffState">--</b>
   <button class="b danger sm" id="btnArmOffOpen" style="margin-left:auto">停用安全開關…</button><button class="b pri sm" id="btnArmOn" hidden style="margin-left:auto">恢復使用安全開關</button></div>
  <div class="aowarn" id="armOffWarn" hidden>
   <div class="aoh">⚠ 停用後,不按安全開關也會倒數,倒數完馬達就啟動</div>
   <div>「上電後直接倒數」:<b>接上電池,飛機放平就開始倒數</b>. 「推一下才倒數」:推一下飛機或按網頁開始,飛機放穩就開始倒數.</div>
   <div>安全開關是接錯電池,搬運時誤觸,手還在螺旋槳旁邊時,防止馬達啟動的最後一道保護. 停用後網頁每一頁上方會一直顯示紅色警告,直到恢復使用;事件紀錄也會記下這趟沒有經過安全開關.</div>
   <label class="chk"><input type="checkbox" class="aock"><span>我了解停用後,接上電池或推一下飛機就會倒數,倒數完馬達會啟動.</span></label>
   <label class="chk"><input type="checkbox" class="aock"><span>接電池與倒數時,我會確認螺旋槳旋轉範圍內沒有人,手不靠近螺旋槳.</span></label>
   <label class="chk"><input type="checkbox" class="aock"><span>我自行承擔停用安全開關的風險.</span></label>
   <div class="row" style="margin:8px 0 0"><button class="b danger" id="btnArmOffGo" disabled>確認停用安全開關</button><button class="b" id="btnArmOffCancel">取消</button></div>
  </div>`;
 const q=s=>el.querySelector(s),cks=[...el.querySelectorAll('.aock')];
 const send=async v=>{try{const r=await post('/api/set',{p:'s',k:'armSwitchOff',v});
   toast(r.ok?(v?'已停用安全開關,按上方的儲存才生效.':'已恢復使用安全開關,按上方的儲存才生效.'):(CODES[r.code]||r.code),!r.ok||!!v)}catch(e){toast('連線失敗.',true)}
  q('#armOffWarn').hidden=true;loadVals()};
 q('#btnArmOffOpen').onclick=()=>{cks.forEach(c=>c.checked=false);q('#btnArmOffGo').disabled=true;q('#armOffWarn').hidden=false};
 cks.forEach(c=>c.onchange=()=>{q('#btnArmOffGo').disabled=!cks.every(x=>x.checked)});
 q('#btnArmOffCancel').onclick=()=>{q('#armOffWarn').hidden=true};
 q('#btnArmOffGo').onclick=()=>{if(cks.every(x=>x.checked))send(1)};
 q('#btnArmOn').onclick=()=>send(0);
 return el;
}
function armOffRender(){
 const box=$('armOffBox');if(!box||!VALS)return;
 const off=!!VALS.shared.armSwitchOff,st=$('armOffState');
 st.textContent=off?'⚠ 已停用(不按開關也會倒數)':'使用中(按下才倒數)';st.style.color=off?'var(--bad)':'var(--ok)';
 $('btnArmOffOpen').hidden=off;$('btnArmOn').hidden=!off;
 if(off)$('armOffWarn').hidden=true;
 for(const w of WIDGETS)if(w.key==='armWait')w.el.hidden=off;   // 不等開關,等待上限用不到
}
function renderWidgets(){
 for(let i=WIDGETS.length-1;i>=0;i--)if(!WIDGETS[i].el.isConnected)WIDGETS.splice(i,1);   // 曲線卡重建後丟掉舊元件
 for(const w of WIDGETS){
  const v=valOf(w.scope,w.key);
  if(w.sel){if(document.activeElement!==w.sel)w.sel.value=v;continue}
  if(w.hold||w.pend!=null)continue;   // 按住 +/− 中或還有沒送完的值:框內顯示的是那個值
  if(document.activeElement!==w.inp)w.inp.value=Number(v).toFixed(decOf(w.m[2]));
  w.el.querySelector('.extra').textContent=extraText(w.scope,w.key,v);
 }
}
let chain=Promise.resolve();
function setParam(scope,key,v){
 // 油門 0% 脈寬待機時立即輸出(安全審查 2-A):PWM 電變已解鎖的話馬達會直接照新脈寬轉. 要先勾「螺旋槳已拆除」才讓改.
 if(scope==='s'&&key==='escMinUs'&&!$('manProp').checked){toast('改「油門 0% 脈寬」時待機中的馬達會立刻照新脈寬轉動. 請先在下方手動輸出卡勾「螺旋槳已拆除」再調.',true);loadVals();return chain}
 chain=chain.then(async()=>{
  try{const r=await post('/api/set',{p:scope==='s'?'s':editP,k:key,v:v});if(!r.ok)toast(CODES[r.code]||r.code,true)}
  catch(e){toast('連線失敗,請再試一次.',true)}
  await loadVals();
 });
 return chain;
}
function card(title,note,id){const c=document.createElement('div');c.className='card';if(id)c.id=id;
 c.innerHTML=`<h2>${title}</h2>${note?`<div class="cnote">${note}</div>`:''}`;wireNotes(c);return c}
// 卡片說明(.cnote)預設收起:在標題加 ⓘ,點了展開/收起. 靜態卡片開機時掃一次,動態卡片建立時呼叫.
function wireNotes(root){
 const cards=root.classList&&root.classList.contains('card')?[root]:[...root.querySelectorAll('.card')];
 for(const c of cards){if(!c.querySelector('.cnote'))continue;const h=c.querySelector('h2');if(!h||h.querySelector(':scope>.ib'))continue;
  const b=document.createElement('button');b.className='ib';b.type='button';b.title='說明';b.textContent='ⓘ';b.onclick=()=>c.classList.toggle('shownote');
  const r=h.querySelector('.h2r');r?h.insertBefore(b,r):h.appendChild(b)}
}

function buildProfile(){
 const box=$('profCards');box.innerHTML='';
 const c=card('時間軸',`<div id="timeline" style="color:var(--ink);margin-bottom:4px"></div>${PROF_NOTE}`,'profParams');
 c.appendChild($('tlSvg'));c.appendChild($('tlLegend'));   // 時間軸圖與顏色說明放在參數上方,同一張卡
 for(const g of PROF_LAYOUT){c.insertAdjacentHTML('beforeend',`<h3 class="grp">${g.t}</h3>`);
  g.k.forEach(k=>c.appendChild(k==='phaseMode'?makeSelect('p',k,'換段方式',PHASE_NAMES,'直接跳:時間到立刻變成第二段油門. 有過渡:時間到後用「換段加力秒數」加上去. 平均分攤:起飛後就把兩段的油門差平均加在第一段時間內,第一段結束剛好到第二段油門.')
   :k==='landingMode'?makeSelect('p',k,'減力方式',['逐漸減力','忽高忽低'],'逐漸減力:在減力秒數內慢慢降到降落油門. 忽高忽低:減力秒數內油門在高低之間規律切換,讓飛手知道動力快停了,走完換降落油門.')
   :k==='landingBuzz'?makeSelect('p',k,'蜂鳴器提醒',['不響','減力期間響'],'減力期間蜂鳴器響:忽高忽低時跟著高油門響,逐漸減力時響半秒停半秒. 蜂鳴器類型在安裝頁設定.')
   :makeParam('p',k)))}
 box.appendChild(c);
}
// --- 風格頁時間軸圖 ---
// 橫軸時間,直軸基本油門. 緩啟動與降落只有幾秒,照真實比例在 5 分鐘的軸上只有兩三個像素看不到,
// 所以每一段依長短分配寬度但有最小寬度(圖上註明不按比例),分段邊界標真實時間.
function drawTimeline(p,sh){
 const svg=$('tlSvg');if(!svg)return;
 const W=440,L=40,R=12,T=20,B=150,pw=W-L-R;
 const p1=p.phase1Pct,p2=p.phase2Pct,T1=p.phase1Sec,F=p.flightSec,tr=Math.min(p.takeoffRamp,T1),pm=p.phaseMode;
 const rampEnd=pm===1?Math.min(F,T1+p.phaseRamp):T1;
 const WAIT=Math.max(3,Math.min(sh.landingTimeout,10));   // 等觸地段只示意
 // 分段:[開始秒,結束秒,名稱]
 // 短段的長度直接寫在名稱裡,刻度只標主要時間點,手機上才不會擠成一團
 // 起飛油門(持續時間 > 0 才有):緩啟動走完維持 hold 秒,再 1 秒過渡到第一段(與韌體 TAKEOFF_BLEND_S 相同)
 const hold=p.takeoffHold>0?p.takeoffHold:0,toEnd=hold?Math.min(T1,tr+hold+1):tr;
 // 第 4 格是底色種類(TL_KIND),圖下方的顏色說明也用同一張表
 const segs=[[0,tr,`緩啟動 ${tr}s`,'ramp']];
 if(hold)segs.push([tr,toEnd,`起飛 ${hold}s`,'takeoff']);
 segs.push([toEnd,T1,'第一段','p1']);
 if(pm===1&&rampEnd>T1)segs.push([T1,rampEnd,`換段 ${p.phaseRamp}s`,'change']);
 segs.push([rampEnd,F,'第二段','p2'],[F,F+p.landingRamp,`${p.landingMode===1?'忽高忽低':'減力'} ${p.landingRamp}s`,'land'],[F+p.landingRamp,F+p.landingRamp+WAIT,'等觸地','land']);
 const MINW=62,dur=segs.map(s=>Math.max(0,s[1]-s[0]));
 const total=dur.reduce((a,b)=>a+b,0)||1;
 let widths=dur.map(d=>Math.max(MINW,pw*d/total));
 const k=pw/widths.reduce((a,b)=>a+b,0);widths=widths.map(w=>w*k);   // 加了最小寬度後整體再縮回總寬
 const x0s=[];let acc=L;for(const w of widths){x0s.push(acc);acc+=w}
 const xOf=t=>{for(let i=0;i<segs.length;i++){const [a,b]=segs[i];if(t<=b||i===segs.length-1){const f=b>a?Math.min(1,Math.max(0,(t-a)/(b-a))):1;return x0s[i]+widths[i]*f}}return L+pw};
 const yOf=v=>B-(B-T)*Math.min(100,Math.max(0,v))/100;
 const base=t=>{   // 與韌體 baseThrottle 同一套(緩啟動期間乘上爬升比例)
  let b=t<T1?(pm===2?p1+(p2-p1)*t/T1:p1):(pm===1&&p.phaseRamp>0?p1+(p2-p1)*Math.min(1,(t-T1)/p.phaseRamp):p2);
  if(hold&&t<tr+hold+1){const he=tr+hold;b=t<he?p.takeoffPct:p.takeoffPct+(b-p.takeoffPct)*(t-he)}
  return t<tr&&tr>0?b*t/tr:b};
 let h=`<defs><pattern id="tlHatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="7" stroke="var(--mute)" stroke-width="2.2" opacity=".45"/></pattern></defs>`;
 // 每一段一種淡底色(GG 2026-09-15):一眼看出緩啟動,起飛油門,第一段,換段,第二段,降落各佔哪裡
 segs.forEach((s,i)=>{h+=`<rect x="${x0s[i]}" y="${T}" width="${widths[i]}" height="${B-T}" fill="${TL_KIND[s[3]].c}" opacity=".18"/>`});
 // 不補償:從馬達起轉(0 秒)算起 noCompSec 秒,用斜線疊在底色上(和階段無關,可能跨過緩啟動,起飛油門,第一段)
 const xFlyA=xOf(Math.min(p.noCompSec,F)),xFlyB=xOf(F);
 if(p.noCompSec>0)h+=`<rect x="${L}" y="${T}" width="${Math.max(0,xFlyA-L)}" height="${B-T}" fill="url(#tlHatch)"/>`;
 for(const v of [0,50,100]){const y=yOf(v);h+=`<line x1="${L}" y1="${y}" x2="${W-R}" y2="${y}" class="cv-grid"/><text x="${L-6}" y="${y+4}" text-anchor="end" class="tl-lab">${v}%</text>`}
 // 上下限數值寫在圖下方說明(r65:原本下限標籤在線下 16px,下限低時掉到 X 軸文字上)
 h+=`<line x1="${L}" y1="${yOf(p.maxPct)}" x2="${xFlyB}" y2="${yOf(p.maxPct)}" class="cv-lim"/><line x1="${L}" y1="${yOf(p.minPct)}" x2="${xFlyB}" y2="${yOf(p.minPct)}" class="cv-lim"/>`;
 // 分段分隔線
 segs.forEach((s,i)=>{if(i)h+=`<line x1="${x0s[i]}" y1="${T}" x2="${x0s[i]}" y2="${B}" stroke="var(--line)" stroke-dasharray="3 3"/>`});
 // X 軸下方只標起飛,換段,降落三個主要時間點(分段名稱改放圖內,見下方)
 for(const [tt,anchor] of [[0,'start'],[T1,'middle'],[F,'middle']])h+=`<text x="${xOf(tt)}" y="${B+17}" text-anchor="${anchor}" class="tl-t">${mmss(Math.round(tt))}</text>`;
 // 基本油門線:依分段逐秒取樣(短段也有足夠點數)
 let pts='';
 segs.forEach(([a,b],i)=>{if(i>=segs.length-2)return;const n=Math.max(2,Math.ceil(widths[i]/4));for(let j=0;j<=n;j++){const t=a+(b-a)*j/n;pts+=`${xOf(t).toFixed(1)},${yOf(base(t)).toFixed(1)} `}});
 // 直接跳:第一段結束瞬間跳到第二段(同一個 x 上的垂直線)
 const segFlyEnd=segs.length-2;
 const xL0=x0s[segFlyEnd],xL1=xL0+widths[segFlyEnd],xW1=xL1+widths[segFlyEnd+1];
 if(p.landingMode===1&&p.landingRamp>0){   // 忽高忽低:先高後低的方波(週期太多只畫 8 個示意),走完換降落油門
  const n=Math.min(8,Math.max(1,Math.round(p.landingRamp/p.pulsePeriod))),dx=(xL1-xL0)/n,yH=yOf(p.pulseHigh).toFixed(1),yLo=yOf(p.pulseLow).toFixed(1);
  for(let j=0;j<n;j++){const a=(xL0+dx*j).toFixed(1),m=(xL0+dx*(j+.5)).toFixed(1),e=(xL0+dx*(j+1)).toFixed(1);pts+=`${a},${yH} ${m},${yH} ${m},${yLo} ${e},${yLo} `}
  pts+=`${xL1.toFixed(1)},${yOf(p.landingPct).toFixed(1)}`}
 else pts+=`${xL0.toFixed(1)},${yOf(p2).toFixed(1)} ${xL1.toFixed(1)},${yOf(p.landingPct).toFixed(1)}`;
 h+=`<polyline points="${pts}" fill="none" stroke="var(--accent)" stroke-width="3" stroke-linejoin="round"/>`;
 h+=`<line x1="${xL1}" y1="${yOf(p.landingPct)}" x2="${xW1}" y2="${yOf(p.landingPct)}" stroke="var(--accent)" stroke-width="3" stroke-dasharray="6 5"/>`;
 // 關鍵油門值
 const tag=(x,v,anchor,dy)=>`<text x="${x}" y="${yOf(v)+(dy||-8)}" text-anchor="${anchor||'middle'}" class="tl-v">${Math.round(v)}%</text>`;
 h+=tag(x0s[1]+4,base(tr),'start')+tag(xOf(T1)-4,base(Math.max(toEnd,T1-0.01)),'end')+tag(xL0-4,p2,'end')+tag(xL1+4,p.landingPct,'start');
 if(hold)h+=tag(x0s[2]+4,base(toEnd),'start');   // 起飛油門之後的第一段油門
 // 分段名稱放在圖內下方,上下兩排交錯(GG 2026-09-15:短段名稱在 X 軸下方擠在一起重疊);相鄰兩段一定不同排.
 // 大略估字寬(中文 12px,英數 6.5px),頭尾的名稱往內推,不超出圖框. 最後畫,文字外框蓋在油門線上仍看得清楚.
 const txtW=s=>[...s].reduce((a,ch)=>a+(ch.charCodeAt(0)>255?12:6.5),0);
 segs.forEach((s,i)=>{const hw=txtW(s[2])/2,cx=Math.min(W-R-hw,Math.max(L+hw,x0s[i]+widths[i]/2));
  h+=`<text x="${cx.toFixed(1)}" y="${i%2?B-24:B-7}" text-anchor="middle" class="tl-seg">${s[2]}</text>`});
 // 不補償標籤放在第三排(斜線區塊中間)
 if(p.noCompSec>0){const s=`不補償 ${p.noCompSec}s`,hw=txtW(s)/2;
  h+=`<text x="${Math.max(L+hw,(L+xFlyA)/2).toFixed(1)}" y="${B-41}" text-anchor="middle" class="tl-seg">${s}</text>`}
 h+=`<text x="${L}" y="${B+37}" class="cv-lab cv-sm">※ 寬度不按比例(短的階段放大),刻度是實際時間(從馬達起轉算起)</text>`;
 svg.innerHTML=h;
 // 顏色說明:只列這組設定圖上有出現的
 const kinds=[...new Set(segs.map(s=>s[3]))];
 let lg=kinds.map(k=>`<span><i style="background:${TL_KIND[k].c}"></i>${TL_KIND[k].t}</span>`).join('');
 if(p.noCompSec>0)lg+=`<span><i class="hatch"></i>斜線:不補償,馬達起轉後 ${p.noCompSec} 秒內不做角度補償</span>`;
 lg+=`<span><i class="lim"></i>虛線:飛行中油門上限 ${p.maxPct}% / 下限 ${p.minPct}%,角度補償加減後不會超出</span><span><i style="background:var(--accent);height:3px"></i>橘線:基本油門(未含角度補償)</span>`;
 $('tlLegend').innerHTML=lg;
}
// 時間軸圖各階段的底色與說明
const TL_KIND={
 ramp:{c:'#f59e0b',t:'緩啟動:馬達從停止慢慢加油門'},
 takeoff:{c:'#ef4444',t:'起飛油門:維持起飛油門,最後 1 秒換到第一段'},
 p1:{c:'#65a30d',t:'第一段'},
 change:{c:'#db2777',t:'換段:從第一段油門加到第二段'},
 p2:{c:'#60a5fa',t:'第二段'},
 land:{c:'#94a3b8',t:'降落:減力後維持降落油門,等觸地關馬達'}
};

// --- 角度補償:只有一條曲線,兩段飛行共用. 「第二段」頁籤只換基本油門顯示,讓人看出加力後哪裡會撞到上限 ---
// (曾經做過第二段獨立曲線,GG 認為不好設定且易混淆,已刪除.)
let cvPhase=1;
const ck=name=>name;   // 曲線參數鍵名(保留這層,日後若再分段只要改這裡)
// 撞牆檢查:掃 -90~+90 度,找出「基本油門 + 補償」超過上限或低於下限的角度區間
function cvWalls(p,base){
 const out=[];let cur=null;
 for(let d=-90;d<=90;d++){
  const want=base+cvComp(p,d),kind=want>p.maxPct?'max':(want<p.minPct?'min':null);
  if(kind&&cur&&cur.kind===kind){cur.to=d;cur.worst=Math.max(cur.worst,Math.abs(want-(kind==='max'?p.maxPct:p.minPct)))}
  else{if(cur)out.push(cur);cur=kind?{kind,from:d,to:d,worst:Math.abs(want-(kind==='max'?p.maxPct:p.minPct))}:null}
 }
 if(cur)out.push(cur);
 return out;
}
function cvWallText(p,base){
 const w=cvWalls(p,base);
 if(!w.length)return '<span style="color:var(--ok)">不會撞到上下限</span>';
 const deg=d=>(d>0?'+':'')+d+'°';
 return w.map(r=>`<div>${deg(r.from)}~${deg(r.to)} ${r.kind==='max'?`<b style="color:var(--bad)">撞上限 ${p.maxPct}%</b>`:`<b style="color:var(--warn)">觸底 ${p.minPct}%</b>`},差 ${r.worst.toFixed(0)}%</div>`).join('');
}
let curveSig='';
function buildCurve(){
 const p=VALS.profile,sig=cvPhase+'/'+p[ck('upN')]+'/'+p[ck('dnN')];
 if(sig===curveSig&&$('curveCard').childElementCount)return;
 curveSig=sig;
 const c=$('curveCard');c.innerHTML=`<div class="sub" style="margin:6px 0">補償曲線(兩段飛行共用). 補償值加在當段基本油門上,點與點之間直線相連,超過最後一點維持最後一點的值.</div>`;
 for(const [side,title] of [['up','機頭朝上:補速'],['dn','機頭朝下:減速']]){
  const s=document.createElement('div');s.className='side';s.innerHTML=`<h3>${title}</h3>`;
  s.appendChild(makeParam('p',ck(side+'Db'),L[side+'Db'][0],L[side+'Db'][2],'deg'));
  s.appendChild(makeCountSelect(side,'可調點數量'));
  const n=p[ck(side+'N')],grid=document.createElement('div');grid.className='pts';
  for(let i=1;i<=n;i++){
   // 同一點的角度與補償放在同一個框裡,點與點各自分開
   const box=document.createElement('div');box.className='pt';box.innerHTML=`<h4>點 ${i}</h4>`;
   box.appendChild(makeParam('p',ck(`${side}${i}a`),'角度','','deg'));
   box.appendChild(makeParam('p',ck(`${side}${i}p`),'補償','','cpct'));
   grid.appendChild(box);
  }
  s.appendChild(grid);
  c.appendChild(s);
 }
}
// --- 角度補償曲線圖(規格第 4 節圖形化介面) ---
// 座標:直軸機頭角度 +90(上)~-90(下),橫軸實際輸出油門 0~100% 等距. 繪圖區以外是把手與刻度.
// 高度 548 → 366(GG 2026-09-14):整張圖禁止捲頁後太高,手機上能按著捲頁的區域被壓縮. 角度區 442 → 260 單位,
// 15° 格線間距約 22 單位,點的觸控範圍(半徑 20)仍夠用. 改高度要同時改下面 cvSvg 的 viewBox.
// 圖框上方那一排放基本油門標籤(r67 從框中間搬出來)與直軸上方的「機頭朝上」;r68 拿掉角落段別文字,高度回到 366
const CV={W:440,H:366,L:62,R:26,T:22,B:84};
const CV_X0=CV.L,CV_X1=CV.W-CV.R,CV_Y0=CV.T,CV_Y1=CV.H-CV.B;
let cvSel={t:'pt',side:'up',i:1},cvDrag=null,cvPanelSig='',cvLimOpen=false;
const cvX=p=>CV_X0+(CV_X1-CV_X0)*p/100, cvY=d=>CV_Y0+(CV_Y1-CV_Y0)*(90-d)/180;
const cvPct=x=>(x-CV_X0)/(CV_X1-CV_X0)*100, cvDeg=y=>90-(y-CV_Y0)/(CV_Y1-CV_Y0)*180;
const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
function cvBaseKey(){return cvPhase===1?'phase1Pct':'phase2Pct'}
function cvUs(p){return pctToUs(p)}
// 與韌體 curveCompPct() 同一套:朝下用「離水平越遠越大」的距離算,超過最後一點維持最後一點
function cvComp(p,deg){
 const s=deg>=0?'up':'dn',sign=deg>=0?1:-1,x=deg*sign;
 let pa=p[ck(s+'Db')]*sign,pp=0;if(x<=pa)return 0;
 for(let i=1;i<=p[ck(s+'N')];i++){const a=p[ck(`${s}${i}a`)]*sign,c=p[ck(`${s}${i}p`)];if(x<=a)return a>pa?pp+(c-pp)*(x-pa)/(a-pa):c;pa=a;pp=c}
 return pp;
}
function cvSelKey(){return cvSel.t==='pt'?`${cvSel.side}${cvSel.i}`:cvSel.t==='db'?cvSel.side+'Db':cvSel.t}
function drawCurve(){
 if(!VALS||!META)return;
 const p=VALS.profile,base=p[cvBaseKey()],mn=p.minPct,mx=p.maxPct,right=VALS.shared.noseRight===1;
 const upDb=p[ck('upDb')],dnDb=p[ck('dnDb')];
 const X0=CV_X0,X1=CV_X1,Y0=CV_Y0,Y1=CV_Y1;
 let h='<defs><filter id="cvGlow" x="-2" y="-2" width="5" height="5"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>';
 // 油門上下限以外塗灰,死區淡主色
 h+=`<rect x="${X0}" y="${Y0}" width="${cvX(mn)-X0}" height="${Y1-Y0}" class="cv-limit"/><rect x="${cvX(mx)}" y="${Y0}" width="${X1-cvX(mx)}" height="${Y1-Y0}" class="cv-limit"/>`;
 h+=`<rect x="${X0}" y="${cvY(upDb)}" width="${X1-X0}" height="${Math.max(0,cvY(dnDb)-cvY(upDb))}" class="cv-dead"/>`;
 for(let d=-90;d<=90;d+=15){const y=cvY(d);h+=`<line x1="${X0}" y1="${y}" x2="${X1}" y2="${y}" class="${d?'cv-grid':'cv-zero'}"/>`;
  if(d%30===0)h+=`<text x="${X0-9}" y="${y+4.5}" text-anchor="end" class="cv-lab">${d>0?'+':''}${d}°</text>`}
 for(let v=0;v<=100;v+=10){const x=cvX(v);h+=`<line x1="${x}" y1="${Y0}" x2="${x}" y2="${Y1}" class="cv-grid"/>`;
  if(v%20===0)h+=`<text x="${x}" y="${Y1+50}" text-anchor="middle" class="cv-lab">${v}%</text><text x="${x}" y="${Y1+64}" text-anchor="middle" class="cv-lab cv-sm">${cvUs(v)}µs</text>`}
 // 「機頭朝上」放在直軸 +90° 刻度上方(框外左上角);段別文字已拿掉,看上方第一段/第二段按鈕(GG 2026-09-15)
 h+=`<text x="${X0-9}" y="${Y0-8}" text-anchor="end" class="cv-lab cv-sm">機頭朝上</text><text x="${X0}" y="${Y1+80}" class="cv-lab cv-sm">橫軸:實際輸出油門(灰色 = 超出上下限,不會輸出)</text>`;
 h+=`<rect x="${X0}" y="${Y0}" width="${X1-X0}" height="${Y1-Y0}" class="cv-frame"/>`;
 h+=`<line x1="${cvX(mn)}" y1="${Y0}" x2="${cvX(mn)}" y2="${Y1}" class="cv-lim"/><line x1="${cvX(mx)}" y1="${Y0}" x2="${cvX(mx)}" y2="${Y1}" class="cv-lim"/>`;
 h+=`<line x1="${cvX(base)}" y1="${Y0}" x2="${cvX(base)}" y2="${Y1}" class="cv-base"/>`;
 // 曲線:原始(虛線)與夾在上下限後的實際輸出(粗線)
 let raw='',clip='';
 for(let d=-90;d<=90;d++){const c=base+cvComp(p,d),y=cvY(d).toFixed(1);raw+=`${cvX(clamp(c,0,100)).toFixed(1)},${y} `;clip+=`${cvX(clamp(c,mn,mx)).toFixed(1)},${y} `}
 h+=`<polyline points="${raw}" class="cv-raw"/><polyline points="${clip}" class="cv-curve"/>`;
 // 撞牆:補償後被上下限卡住的角度區間,沿限制線畫紅色粗線並標示
 for(const w of cvWalls(p,base)){
  const x=cvX(w.kind==='max'?mx:mn),ya=cvY(w.to),yb=cvY(w.from),ym=(ya+yb)/2;
  h+=`<line x1="${x}" y1="${ya}" x2="${x}" y2="${yb}" stroke="#ef4444" stroke-width="6" stroke-linecap="round" opacity=".85"/>`+
   `<text x="${w.kind==='max'?x-8:x+8}" y="${ym+4}" text-anchor="${w.kind==='max'?'end':'start'}" class="cv-nowt">${w.kind==='max'?'撞上限':'觸底'}</text>`;
 }
 // 目前角度紅線的群組放在標籤與點的底下,紅線才不會穿過文字(每次狀態輪詢只更新這個群組)
 h+='<g id="cvNow"></g>';
 // 基本油門標籤放在圖框外上方(GG 2026-09-15:原本在框中間 0° 的位置,遮住曲線與死區),短線接到框頂的基本油門線
 const bx=cvX(base),bt=`基本油門 ${base}%(${cvUs(base)}µs)`,bw=bt.length*9.5+14,tx=clamp(bx,X0+bw/2+2,X1-bw/2-2);
 h+=`<rect x="${tx-bw/2}" y="${Y0-21}" width="${bw}" height="19" rx="5" class="cv-tag"/><text x="${tx}" y="${Y0-7}" text-anchor="middle" class="cv-tagt" style="font-size:12.5px">${bt}</text>`;
 // 飛機圖示(左上角,跟著目前角度轉)
 h+=`<g transform="translate(${X0+44},${Y0+36})"><g id="cvPlane"><g id="cvPlaneFlip" transform="scale(${right?-1:1},1)" class="cv-plane"><g transform="scale(.36)">`+
  `<path d="M-92,0 Q-90,-9 -72,-10 L58,-5 L96,-3 L96,3 L58,5 L-72,10 Q-90,9 -92,0 Z"/><path d="M68,-4 L90,-30 L100,-30 L97,-3 Z"/><rect x="-97" y="-28" width="4" height="56"/><circle cx="-54" cy="30" r="7"/></g></g></g></g>`;
 // 死區邊界(曲線從這裡開始補償):不能拖,畫成實心小點,和空心可拖的點區分(GG)
 h+=`<circle cx="${bx}" cy="${cvY(upDb)}" r="3" class="cv-db"/><circle cx="${bx}" cy="${cvY(dnDb)}" r="3" class="cv-db"/>`;
 // 可調點
 for(const side of ['up','dn'])for(let i=1;i<=p[ck(side+'N')];i++){
  const a=p[ck(`${side}${i}a`)],c=p[ck(`${side}${i}p`)],x=cvX(clamp(base+c,0,100)),y=cvY(a);
  const sel=cvPhase===1&&cvSel.t==='pt'&&cvSel.side===side&&cvSel.i===i;
  // 看得到的點縮小(GG:太肥),手指觸控範圍維持半徑 20 才好按
  h+=`<circle cx="${x}" cy="${y}" r="${sel?7.5:6}" class="cv-pt${sel?' sel':''}"/><circle cx="${x}" cy="${y}" r="20" class="cv-hit" data-h="pt" data-side="${side}" data-i="${i}"/>`;
  if(sel){const out=clamp(base+c,mn,mx),lx=x>X1-150?x-16:x+16,ly=y-14<Y0+14?y+26:y-14;   // 太靠近頂端時文字放到點下方,不壓到圖角標籤
   h+=`<text x="${lx}" y="${ly}" text-anchor="${x>X1-150?'end':'start'}" class="cv-nowt">${a>0?'+':''}${a}° ${c>=0?'+':''}${c}% → ${out}%</text>`}
 }
 // 邊框把手:直軸左側 = 死區上下緣;橫軸下方 = 下限 / 基本 / 上限
 const hdY=(side,deg,label)=>{const y=cvY(deg),sel=cvSel.t==='db'&&cvSel.side===side;
  return `<path d="M${X0-2},${y} l-13,-9 v18 z" class="cv-hd${sel?' sel':''}"/><text x="${X0-17}" y="${y+(side==='up'?-8:17)}" text-anchor="end" class="cv-lab cv-sm">${label}</text>`+
   `<rect x="${X0-40}" y="${y-14}" width="52" height="28" class="cv-hit" data-h="db" data-side="${side}"/>`};
 const hdX=(key,v,label,cls)=>{const x=cvX(v),sel=cvSel.t===key;
  return `<path d="M${x},${Y1+2} l-9,14 h18 z" class="cv-hd ${cls}${sel?' sel':''}"/><text x="${x}" y="${Y1+30}" text-anchor="middle" class="cv-lab cv-sm">${label}</text>`+
   `<rect x="${x-16}" y="${Y1}" width="32" height="36" class="cv-hit" data-h="${key}"/>`};
 // 第二段:曲線不能改,只留基本油門把手(就是風格頁的第二段基本油門,兩邊連動)
 if(cvPhase===2){h+=hdX('base',base,'基本','base');$('cvSvg').innerHTML=h;if(STATUS)updateCurveNow(STATUS);buildCurvePanel();return}
 h+=hdY('up',upDb,'補速起點')+hdY('dn',dnDb,'減速起點');
 h+=hdX('min',mn,'下限','')+hdX('max',mx,'上限','')+hdX('base',base,'基本','base');
 $('cvSvg').innerHTML=h;
 if(STATUS)updateCurveNow(STATUS);
 buildCurvePanel();   // 撞牆檢查跟著曲線即時更新(拖曳中也是)
}
let cvInverted=false;
function updateCurveNow(s){
 const g=$('cvNow');if(!g||!VALS)return;
 const p=VALS.profile,base=p[cvBaseKey()],d=clamp(s.p,-90,90),y=cvY(d),out=clamp(base+cvComp(p,d),p.minPct,p.maxPct);
 // 「目前」文字跟著紅線與曲線的交點走(GG 2026-09-15). 曲線越往上(朝上角度大或朝下角度小)油門越大,
 // 交點的左上方與右下方不會壓到曲線:優先放左上;左邊放不下或太靠頂端放右下;右下超出底部再回左上.
 const px=cvX(out),nt=`目前 ${d>0?'+':''}${d.toFixed(0)}° → ${out.toFixed(0)}%`,nw=[...nt].reduce((a,ch)=>a+(ch.charCodeAt(0)>255?12.5:7.2),0);
 let ul=px-10-nw>=CV_X0+2&&y-8>=CV_Y0+12;
 if(!ul&&y+18>CV_Y1-4)ul=true;
 const tx=ul?Math.max(CV_X0+2+nw,px-10):Math.min(CV_X1-2-nw,px+10);
 g.innerHTML=`<line x1="${CV_X0}" y1="${y}" x2="${CV_X1}" y2="${y}" class="cv-now"/><circle cx="${px}" cy="${y}" r="5" fill="#ef4444"/>`+
  `<text x="${tx.toFixed(1)}" y="${(ul?Math.max(CV_Y0+12,y-8):y+18).toFixed(1)}" text-anchor="${ul?'end':'start'}" class="cv-nowt">${nt}</text>`;
 // 飛機圖示:與監看頁同一套倒飛判斷(倒飛時機頭換邊且上下顛倒)
 if(Math.abs(s.p)<70){if(Math.abs(s.r)>100)cvInverted=true;else if(Math.abs(s.r)<80)cvInverted=false}
 const nr=(VALS.shared.noseRight===1)!==cvInverted,pl=$('cvPlane'),pf=$('cvPlaneFlip');
 if(pl)pl.setAttribute('transform',`rotate(${nr?-d:d})`);
 if(pf)pf.setAttribute('transform',`scale(${nr?-1:1},${cvInverted?-1:1})`);
}
function cvSvgPoint(e){const svg=$('cvSvg'),pt=svg.createSVGPoint();pt.x=e.clientX;pt.y=e.clientY;return pt.matrixTransform(svg.getScreenCTM().inverse())}
// 拖曳時只改畫面上的值,放開才送出;相鄰限制在前端先夾好,送出去一定合法
function cvApplyDrag(e){
 const p=VALS.profile,q=cvSvgPoint(e),base=p[cvBaseKey()],d=Math.round(cvDeg(q.y)),v=Math.round(cvPct(q.x));
 const s=cvDrag,A=(side,i)=>p[ck(`${side}${i}a`)];
 if(s.t==='pt'){
  const side=s.side,i=s.i,n=p[ck(side+'N')];
  if(side==='up'){const lo=(i===1?p[ck('upDb')]:A('up',i-1))+1,hi=i===n?90:A('up',i+1)-1;p[ck(`up${i}a`)]=clamp(d,lo,hi)}
  else{const hi=(i===1?p[ck('dnDb')]:A('dn',i-1))-1,lo=i===n?-90:A('dn',i+1)+1;p[ck(`dn${i}a`)]=clamp(d,lo,hi)}
  // 用總油門夾(GG:不管基本油門在哪,都能拉到總油門 10%~100%),補償值本身 ±100
  p[ck(`${side}${i}p`)]=clamp(clamp(v,META.profile.minPct[0],100)-base,-100,100);
 }else if(s.t==='db'){
  if(s.side==='up')p[ck('upDb')]=clamp(d,0,Math.min(89,A('up',1)-1));else p[ck('dnDb')]=clamp(d,Math.max(-89,A('dn',1)+1),0);
 }else if(s.t==='min')p.minPct=clamp(v,META.profile.minPct[0],p.maxPct-1);   // 下限最低 10%(參數表範圍)
 else if(s.t==='max')p.maxPct=clamp(v,p.minPct+1,100);
 else if(s.t==='base')p[cvBaseKey()]=clamp(v,0,100);
 drawCurve();renderWidgets();
}
// 取消拖曳:畫面上改到一半的值放回拖曳前,不送出
function cvCancelDrag(){
 if(!cvDrag)return;const s=cvDrag;cvDrag=null;
 if(s.moved&&VALS){s.keys.forEach((k,i)=>{VALS.profile[k]=s.before[i]});drawCurve();renderWidgets()}
}
function cvDragKeys(s){
 if(s.t==='pt')return [ck(`${s.side}${s.i}a`),ck(`${s.side}${s.i}p`)];
 if(s.t==='db')return [ck(s.side+'Db')];
 return [s.t==='min'?'minPct':s.t==='max'?'maxPct':cvBaseKey()];
}
(function(){
 const svg=$('cvSvg');
 const hitOf=e=>e.target&&e.target.closest?e.target.closest('[data-h]'):null;
 // 觸控手勢(GG 2026-09-14,說明文字在圖旁的「手勢」框):
 //  單指:只拖曲線的點與把手,不捲動網頁.
 //  雙指捏合:放大/縮小網頁(網頁沒放大時也可以). 放大後雙指拖動:移動網頁.
 // 做法:touch-action:pinch-zoom 讓瀏覽器在這區只做雙指縮放(放大後雙指縮放手勢會一起平移),單指不捲頁;
 // 觸控事件完全不呼叫 preventDefault —— r41 在單指移動時擋預設,又自己處理雙指拖動,手指一前一後放上去時
 // 瀏覽器常常不開始縮放,網頁沒放大時捏不動(GG 回報).
 svg.style.touchAction='pinch-zoom';
 svg.addEventListener('touchstart',e=>{if(e.touches.length>=2)cvCancelDrag()},{passive:true});
 const pointers=new Set();
 svg.addEventListener('pointerdown',e=>{
  if(e.isPrimary)pointers.clear();   // 一次手勢的第一指:清掉上次手指在圖外放開沒收到 pointerup 留下的殘留
  pointers.add(e.pointerId);
  if(pointers.size>1){cvCancelDrag();return}   // 第二隻手指放上來:不是在拖曲線
  const hit=hitOf(e);if(!hit||!VALS)return;
  if(STATUS&&STATUS.lock){toast(CODES.locked,true);return}
  const t=hit.dataset.h;
  if(cvPhase===2&&t!=='base'){toast('第二段只能拖基本油門. 曲線與上下限請切回「第一段」調整.');return}
  cvSel=t==='pt'?{t,side:hit.dataset.side,i:Number(hit.dataset.i)}:t==='db'?{t,side:hit.dataset.side}:{t};
  const keys=cvDragKeys(cvSel),before=keys.map(k=>VALS.profile[k]);
  cvDrag=Object.assign({},cvSel,{keys,before,x:e.clientX,y:e.clientY,moved:false});
  svg.setPointerCapture(e.pointerId);buildCurvePanel();drawCurve();
 });
 svg.addEventListener('pointermove',e=>{
  if(!cvDrag||pointers.size>1)return;
  if(!cvDrag.moved&&Math.hypot(e.clientX-cvDrag.x,e.clientY-cvDrag.y)<4)return;   // 點一下只選取,不移動
  cvDrag.moved=true;cvApplyDrag(e);
 });
 const end=async()=>{
  if(!cvDrag)return;const s=cvDrag;cvDrag=null;
  if(!s.moved)return;
  // 角度與補償一次送出(setmany 全部寫完才驗證),送完只重新讀一次. r58 以前分兩次送,每次都重新讀,
  // 送完角度讀回來補償還是舊值,畫面上的點先跳回原位再跳到新位置. 被韌體拒絕時重新讀回來就回到原值.
  const body=s.keys.map((k,i)=>[k,VALS.profile[k],s.before[i]]).filter(x=>x[1]!==x[2]).map(x=>`${x[0]}=${x[1]}`).join('\n');
  if(!body){render();return}
  cvSaving=true;valsGen++;
  chain=chain.then(async()=>{
   try{const r=await poll('/api/setmany?p='+editP,{method:'POST',headers:{'Content-Type':'text/plain'},body});
    if(!r.ok)toast(CODES[r.code]||r.code,true)}
   catch(e){toast('連線失敗,請再試一次.',true)}
   cvSaving=false;valsGen++;
   await loadVals();
  });
 };
 svg.addEventListener('pointerup',e=>{pointers.delete(e.pointerId);end()});
 // 瀏覽器接手手勢(雙指縮放)時會送 pointercancel:拖到一半的點回原位,不送出
 svg.addEventListener('pointercancel',e=>{pointers.delete(e.pointerId);cvCancelDrag()});
 document.querySelectorAll('#cvPhase button').forEach(b=>b.onclick=()=>{cvPhase=Number(b.dataset.ph);
  document.querySelectorAll('#cvPhase button').forEach(x=>x.classList.toggle('on',x===b));
  cvPanelSig='';buildCurvePanel();drawCurve()});
})();
function makeCountSelect(side,label){
 const row=makeSelect('p',ck(side+'N'),label,[],'改變點數時,各點會重新平均分布,曲線形狀大致不變.');
 const sel=row.querySelector('select');
 for(let n=META.curveMin;n<=META.curveMax;n++)sel.insertAdjacentHTML('beforeend',`<option value="${n}">${n} 點</option>`);
 return row;
}
function buildCurvePanel(){
 if(!VALS||!META)return;
 const p=VALS.profile;
 if(cvSel.t==='pt'&&cvSel.i>p[ck(cvSel.side+'N')])cvSel.i=p[ck(cvSel.side+'N')];
 // 撞牆檢查每次都更新(拖曳中也會變),不受下面的面板重建節流影響
 const wallBox=()=>{let wb=$('cvWall');if(!wb){wb=document.createElement('div');wb.id='cvWall';wb.className='selbox';wb.style.cssText='margin-top:6px;border-color:var(--line)'}
  wb.innerHTML=`<h3 style="color:var(--ink)">撞牆檢查 <span class="sub" style="font-weight:400">補償後被上下限卡住的角度</span></h3>`+
   `<div class="wl"><span class="sub">第一段 ${p.phase1Pct}%</span><div>${cvWallText(p,p.phase1Pct)}</div></div><div class="wl"><span class="sub">第二段 ${p.phase2Pct}%</span><div>${cvWallText(p,p.phase2Pct)}</div></div>`;
  return wb};
 // 油門上下限(GG 2026-09-14 從計時器頁搬來):放在撞牆檢查下面,預設收起,點標題展開. 面板重建時保留展開狀態.
 const limBox=()=>{let d=$('cvLim');
  if(!d){d=document.createElement('details');d.id='cvLim';d.className='selbox';d.style.cssText='margin-top:6px;border-color:var(--line)';d.open=cvLimOpen;
   d.ontoggle=()=>{cvLimOpen=d.open};
   d.innerHTML='<summary style="cursor:pointer;padding:2px 0"><b>油門上下限</b> <span class="sub">(兩段共用,也可拖圖下方三角形)</span></summary>';
   d.appendChild(makeParam('p','minPct'));d.appendChild(makeParam('p','maxPct'))}
  return d};
 // 已在正確位置就不搬(搬動元素會讓正在輸入的上下限框失去焦點)
 const tail=()=>{const pn=$('curvePanel'),wb=wallBox(),lb=limBox();
  if(pn.lastChild!==lb||lb.previousSibling!==wb){pn.appendChild(wb);pn.appendChild(lb)}};
 const sig=cvSelKey()+'|'+cvPhase+'|'+p[ck('upN')]+'|'+p[ck('dnN')]+'|'+editP;
 if(sig===cvPanelSig&&$('curvePanel').childElementCount){tail();return}
 cvPanelSig=sig;
 const box=$('curvePanel');box.innerHTML='';
 if(cvPhase===2){
  // 第二段:曲線不能改,只能調第二段基本油門(與風格頁同一個參數),看加力後哪裡會撞到上限
  const sb2=document.createElement('div');sb2.className='selbox';
  sb2.innerHTML=`<h3>第二段基本油門(與計時器頁連動)</h3>`;sb2.appendChild(makeParam('p','phase2Pct'));
  sb2.insertAdjacentHTML('beforeend',`<div class="sub" style="margin:2px 0 4px">拖圖下方「基本」三角形或按 +/−. 曲線兩段共用,要改曲線請切回第一段. 圖上紅色粗線 = 撞到上限,油門被卡住的角度.</div>`);
  box.appendChild(sb2);
  tail();
  renderWidgets();
  return;
 }
 const sb=document.createElement('div');sb.className='selbox';
 const ph='';
 let title='',rows=[];
 if(cvSel.t==='pt'){const s=cvSel.side;title=`選取:${s==='up'?'朝上':'朝下'} 點 ${cvSel.i}`;
  rows=[makeParam('p',ck(`${s}${cvSel.i}a`),'角度','','deg'),makeParam('p',ck(`${s}${cvSel.i}p`),'補償','加在基本油門上','cpct')]}
 else if(cvSel.t==='db'){const s=cvSel.side;title=`選取:${s==='up'?'補速起點(死區上緣)':'減速起點(死區下緣)'}`;
  rows=[makeParam('p',ck(s+'Db'),L[s+'Db'][0],L[s+'Db'][2],'deg')]}
 else if(cvSel.t==='min'){title='選取:飛行中油門下限(兩段共用)';rows=[makeParam('p','minPct')]}
 else if(cvSel.t==='max'){title='選取:飛行中油門上限(兩段共用)';rows=[makeParam('p','maxPct')]}
 else {title='選取:第一段基本油門';rows=[makeParam('p',cvBaseKey())]}
 sb.innerHTML=`<h3>${title}</h3>`;rows.forEach(r=>sb.appendChild(r));
 box.appendChild(sb);
 // 朝上/朝下點數兩個選單排同一列
 const cnt=document.createElement('div');cnt.className='cnt2';
 cnt.appendChild(makeCountSelect('up','朝上點數'));cnt.appendChild(makeCountSelect('dn','朝下點數'));
 box.appendChild(cnt);
 tail();
 renderWidgets();
}
function buildShared(){
 const oc=$('setOrientCards');oc.innerHTML='';oc.appendChild(makeParam('s','pitchTrim'));
 $('setCards').innerHTML='';$('instCards').innerHTML='';$('escCards').innerHTML='';
 $('calParam').innerHTML='';$('calParam').appendChild(makeParam('s','calibHold'));
 for(const [layout,boxId] of [[SET_LAYOUT,'setCards'],[INST_LAYOUT,'instCards'],[ESC_LAYOUT,'escCards']])for(const g of layout){const box=$(boxId);
  const c=card(g.t,g.n,g.id);
  for(const k of g.k){
   if(k==='gestureEnable')c.appendChild(makeSelect('s',k,'啟動方式',['上電後直接倒數','推一下才倒數(手勢)'],'推一下才倒數:推一下飛機或按上方「開始起飛程序」,放穩後按安全開關開始倒數. 上電後直接倒數:接上電池,飛機放平按下安全開關就倒數,每次通電只一次(軟體重開不算,要飛請拔電再接電). 想按開關後一定準時啟動,把「外力介入時」設成不理會外力.'));
   else if(k==='disturbMode')c.appendChild(makeSelect('s',k,'外力介入時',['延長秒數','從頭倒數','不理會外力'],'倒數中有人碰到飛機(晃動超過外力門檻)時怎麼處理.'));
   else if(k==='earlyLand')c.appendChild(makeSelect('s',k,'觸地提早降落',['關閉','開啟'],'建議先關閉,到紀錄頁比對特技與地面滑行的 Z 軸抖動,確定不會誤觸再開啟. 開啟時收輪不作用.'));
   else if(k==='gearEnable')c.appendChild(makeSelect('s',k,'收輪功能',['關閉','開啟'],'沒有收腳的飛機保持關閉. 觸地提早降落開啟時不收輪:隨時可能貼地降落,輪子要一直放著.'));
   else if(k==='gearReverse')c.appendChild(makeSelect('s',k,'舵機方向',['正轉(收起在上限)','反轉(收起在下限)'],'正轉:放下在下限,收起在上限;反轉相反. 按「試收輪」看方向,反了就切換.'));
   else if(k==='armSwitchOff')c.appendChild(makeArmOff());
   else if(k==='buzzerLow')c.appendChild(makeSelect('s',k,'蜂鳴器類型',['有源:高電位觸發','有源:低電位觸發','無源蜂鳴器(2 kHz)'],'通電就會響的有源模組,依標示選高或低電位;要方波才響的選無源(輸出 2 kHz). GPIO7 是 3.3V 小電流訊號,大電流蜂鳴器請接驅動模組. 改完按上方的儲存.'));
   else if(k==='crashEnable')c.appendChild(makeSelect('s',k,'撞擊斷電',['關閉','開啟'],'開啟時,飛行中衝擊超過撞擊門檻立即關馬達.'));
   else if(k==='escRpm')c.appendChild(makeSelect('s',k,'轉速回傳(雙向 DShot)',['關閉','開啟'],'電變把馬達轉速送回來顯示. 只有 DShot300 可用,電變韌體要支援雙向 DShot(Bluejay,AM32,BLHeli_32 32.7 以上). <b>不支援的電變開了可能不解鎖</b>:改用 DShot300 後先用手動輸出確認馬達會轉,不轉就關閉. 儲存並重新開機生效;收不到回傳只顯示警告,不擋起飛.'));
   else if(k==='escProtocol')c.appendChild(makeSelect('s',k,'電變訊號',['PWM(一般電變)','DShot150','DShot300'],'一般電變用 PWM;Bluejay 只能用 DShot. BLHeli_S 的 L 型(24MHz)官方建議 DShot150,其他開源電變用 DShot300. 詳見下方廠牌說明.'));
   else c.appendChild(makeParam('s',k));
  }
  if(g.id==='earlyCard')c.insertAdjacentHTML('beforeend','<div class="live" id="elLive"><span>目前</span><b id="elVib">--</b><span id="elLvl">--</span><span class="meter"><i id="elMeter"></i></span><span id="elHold">--</span></div>');
  if(g.id==='speedCard')c.insertAdjacentHTML('beforeend','<div class="sub" id="speedText"></div>');
  if(g.id==='gearCard'){c.insertAdjacentHTML('beforeend','<div class="live" id="gearEarlyWarn" hidden><span class="pill warn">收輪不作用</span><span class="sub">設定頁的「觸地提早降落」開啟中,輪子會一直放著. 要收輪請先關閉提早降落.</span></div>'+
   '<div class="live" id="gearLive"><span>目前</span><b id="gearState">--</b><span id="gearUs" class="sub"></span><button class="b" id="btnGearTest" style="margin-left:auto">試收輪</button></div>');
   c.querySelector('#btnGearTest').onclick=()=>{const on=!(STATUS&&STATUS.gear&&STATUS.gear[2]);
    post('/api/geartest',{on:on?1:0}).then(r=>{if(!r.ok)toast(CODES[r.code]||r.code,true);else if(on)toast('試收輪:10 秒後自動放下.');tick()}).catch(()=>toast('連線失敗.',true))}}
  if(g.id==='protoCard')c.insertAdjacentHTML('beforeend','<div class="man-read"><span class="pill" id="protoPill">--</span><span class="sub" id="protoText"></span><button class="b" id="btnProtoReboot" hidden>重新開機套用</button></div>'+
   '<div class="live" id="rpmLive" hidden><span class="pill" id="rpmPill">--</span><b id="rpmVal">--</b><span class="sub" id="rpmText"></span></div>');
  box.appendChild(c);
 }
 const sn=$('selNose'),su=$('selUp');
 sn.innerHTML=AXES.map((a,i)=>`<option value="${i}">${a}${i===0?'(預設)':''}</option>`).join('');
 su.innerHTML=AXES.map((a,i)=>`<option value="${i}">${a}${i===4?'(預設)':''}</option>`).join('');
 sn.onchange=()=>setParam('s','noseAxis',sn.value);su.onchange=()=>setParam('s','upAxis',su.value);
 // 回預設:兩軸與角度修正一次送出(逐項送會卡在「兩軸同軸」的中間狀態被拒)
 $('btnOrientDef').onclick=()=>{chain=chain.then(async()=>{
  try{const r=await poll('/api/setmany?p=s',{method:'POST',headers:{'Content-Type':'text/plain'},body:'noseAxis=0\nupAxis=4\npitchTrim=0'});
   if(!r.ok)toast(CODES[r.code]||r.code,true);else toast('安裝方位已回預設,確認沒問題再按上方的儲存.')}
  catch(e){toast('連線失敗,請再試一次.',true)}
  await loadVals()})};
 // 啟動手勢試推燈:掛在手勢力道那一列
 const gw=WIDGETS.find(w=>w.key==='gestureG');
 if(gw)gw.el.insertAdjacentHTML('beforeend','<div class="live" style="flex:1 1 100%" title="機身水平往機頭推,達到力道亮綠燈"><span class="lamp" id="gLamp"></span><span class="sub">試推亮綠燈</span><b id="gPush" style="margin-left:auto">--</b></div>');
 // 外力門檻指示燈:與倒數中判斷外力是同一個數值(加速度相對放穩時的變化),超過門檻亮橘燈
 const dw=WIDGETS.find(w=>w.key==='disturbG');
 if(dw)dw.el.insertAdjacentHTML('beforeend','<div class="live" style="flex:1 1 100%" title="晃動或碰一下飛機,超過門檻亮橘燈"><span class="lamp" id="dLamp"></span><span class="sub">碰飛機亮橘燈</span><b id="dVal" style="margin-left:auto">--</b></div>');
 document.querySelectorAll('#noseSeg button').forEach(b=>b.onclick=()=>setParam('s','noseRight',b.dataset.v));
}

function render(){
 if(!VALS)return;
 const p=VALS.profile,s=VALS.shared;
 // 風格選擇列
 for(const id of ['profSeg','profSeg2']){
  $(id).innerHTML=VALS.names.map((n,i)=>`<button data-i="${i}" class="${i===editP?'on':''}">${i===VALS.active?'<span class="star">★</span>':''}${esc(n)}${VALS.dirtyProfiles[i]?'<span class="dot"></span>':''}</button>`).join('');
  $(id).querySelectorAll('button').forEach(b=>b.onclick=()=>{editP=Number(b.dataset.i);loadVals()});
 }
 $('btnSelect').disabled=editP===VALS.active;
 $('btnSelect').textContent=editP===VALS.active?'★ 飛行使用中':'設為飛行使用';
 if(document.activeElement!==$('fName'))$('fName').value=VALS.names[editP];
 // 「測試」組名稱固定(GG 2026-09-15):改名欄與按鈕停用
 const nameLocked=editP===PROFILE_TEST_INDEX;
 $('fName').disabled=nameLocked;$('btnName').disabled=nameLocked;
 $('fName').title=nameLocked?'「測試」這組名稱固定,不能改.':'';
 $('copyTo').innerHTML=VALS.names.map((n,i)=>i===editP?'':`<option value="${i}">${esc(n)}</option>`).join('');
 const pm=p.phaseMode,phaseText=pm===0?`直接跳到 ${p.phase2Pct}%`:pm===1?`${p.phaseRamp} 秒加到 ${p.phase2Pct}%`:`已平均加到 ${p.phase2Pct}%`;
 drawTimeline(p,VALS.shared);
 const toClamp=p.takeoffHold>0?(p.takeoffPct>p.maxPct?`⚠ 起飛油門 ${p.takeoffPct}% 超過上限,實際 ${p.maxPct}%. `:p.takeoffPct<p.minPct?`⚠ 起飛油門 ${p.takeoffPct}% 低於下限,實際 ${p.minPct}%. `:''):'';
 $('timeline').textContent=toClamp+(p.takeoffHold>0?`時間軸:0:00 緩啟動(${p.takeoffRamp} 秒加到起飛油門 ${p.takeoffPct}%) → 維持 ${p.takeoffHold} 秒 → 1 秒換到第一段 ${p.phase1Pct}%`
  :`時間軸:0:00 緩啟動(${p.takeoffRamp} 秒加到 ${p.phase1Pct}%)`)+(pm===2?` → 第一段期間平均加油門`:'')+
  ` → ${mmss(p.phase1Sec)} 換段(${phaseText}) → ${mmss(p.flightSec)} 降落(`+
  (p.landingMode===1?`${p.pulseHigh}% / ${p.pulseLow}% 忽高忽低 ${p.landingRamp} 秒,再換 ${p.landingPct}%`:`${p.landingRamp} 秒減到 ${p.landingPct}%`)+
  (p.landingBuzz?',蜂鳴器提醒':'')+')'+
  (VALS.shared.gearEnable?(VALS.shared.earlyLand?'. 收輪:觸地提早降落開啟中,輪子不收':`. 收輪:${mmss(VALS.shared.gearRetractSec)} 收起,降落開始時放下`):'');
 for(const w of WIDGETS)if(w.key==='phaseRamp')w.el.hidden=pm!==1;   // 只有「有過渡」用得到加力秒數
 for(const w of WIDGETS)if(['pulseLow','pulseHigh','pulsePeriod'].includes(w.key)&&w.scope==='p')w.el.hidden=p.landingMode!==1;   // 忽高忽低才用得到
 buildCurve();
 buildCurvePanel();drawCurve();
 // 共用設定
 $('selNose').value=s.noseAxis;$('selUp').value=s.upAxis;
 for(const w of WIDGETS)if(w.key==='gestureG'||w.key==='twistCancel'||w.key==='twistBlock')w.el.hidden=!s.gestureEnable;   // 手勢關閉時力道,試推燈,扭轉取消都用不到
 for(const w of WIDGETS)if(['earlyLandVib','earlyLandHold','earlyLandTilt','earlyLandArm'].includes(w.key))w.el.hidden=!s.earlyLand;   // 觸地提早降落關閉時收起它的設定(GG)
 if($('elLive'))$('elLive').hidden=!s.earlyLand;
 for(const w of WIDGETS)if(['gearRetractSec','gearTravelSec','gearMinUs','gearMaxUs','gearReverse'].includes(w.key))w.el.hidden=!s.gearEnable;   // 收輪關閉時收起它的設定
 if($('gearEarlyWarn'))$('gearEarlyWarn').hidden=!(s.gearEnable&&s.earlyLand);
 $('axisY').textContent=axisName(cross(axisVec(s.upAxis),axisVec(s.noseAxis)));
 instDraw(STATUS);
 document.querySelectorAll('#noseSeg button').forEach(b=>b.classList.toggle('on',Number(b.dataset.v)===s.noseRight));
 const st=$('speedText');if(st){const v=2*Math.PI*s.lineLength/s.lapSec;st.textContent=`換算飛行速度約 ${v.toFixed(1)} m/s(${(v*3.6).toFixed(0)} km/h)`}
 renderWidgets();
 armOffRender();
 const dirty=valsDirty();
 $('saveBar').hidden=!dirty;$('topBar').classList.toggle('dirty',dirty);
 bkRender();
}
// dirtyActive:備份碼套用了不同的飛行風格,也要按儲存
function valsDirty(){return !!VALS&&(VALS.dirtyShared||!!VALS.dirtyActive||VALS.dirtyProfiles.some(x=>x))}
function esc(t){return String(t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function mmss(s){return `${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}`}

// 曲線拖曳中或放開後還在送出時,讀回來的設定是舊值:不覆蓋畫面(GG:放開瞬間點先跳回原位再跳到新位置).
// valsGen:送出開始就加一,送出前就發出的讀取回來時丟掉.
let cvSaving=false,valsGen=0;
async function loadVals(){
 try{const g=valsGen,v=await poll('/api/settings?p='+editP);
  if(cvDrag||cvSaving||g!==valsGen)return;
  VALS=v;editP=VALS.edit;
  if(VALS.edit===VALS.active){ACTP=VALS.profile;ACTP_IDX=VALS.active}   // 監看頁背景曲線跟著最新的飛行風格
  render()}catch(e){}
}

// --- 姿態圖 ---
(function(){const g=$('scale');for(let d=-60;d<=60;d+=30){if(!d)continue;const y=-d*100/90;
 g.insertAdjacentHTML('beforeend',`<text x="-128" y="${y+3}">${d>0?'+':''}${d}°</text><line x1="-124" y1="${y}" x2="-116" y2="${y}" stroke="var(--mute)"/>`)}})();
function fmtUp(s){const h=Math.floor(s/3600),m=Math.floor(s%3600/60);return h?`${h} 時 ${m} 分`:`${m} 分 ${s%60} 秒`}
function sgn(v,d){return (v>0?'+':'')+v.toFixed(d)}

// --- 監看頁:背景油門曲線與目前角度紅線(與角度補償頁同一套座標概念) ---
// 圖的直軸本來就是機頭角度(-90 上緣 ~ +90... 以 y=-角度×100/90),橫軸拿來放油門 0~100%.
let ACTP=null,ACTP_IDX=-1,actFetching=false;
async function ensureActiveProfile(idx){
 if((ACTP&&ACTP_IDX===idx)||actFetching)return;
 actFetching=true;
 try{const v=await poll('/api/settings?p='+idx);ACTP=v.profile;ACTP_IDX=idx}catch(e){}finally{actFetching=false}
}
function drawMonitorCurve(s){
 const g=$('monCurve'),gn=$('monNow');if(!g||!ACTP||ACTP_IDX!==s.act)return;
 const p=ACTP,f=s.f,flying=f.s>=4&&f.s<=6,ph=flying&&f.ph===2?2:1;
 const X=v=>-160+3.2*clamp(v,0,100),Y=d=>-clamp(d,-90,90)*100/90;
 const curve=base=>{let pts='';for(let d=-90;d<=90;d+=2)pts+=`${X(clamp(base+cvComp(p,d),p.minPct,p.maxPct)).toFixed(1)},${Y(d).toFixed(1)} `;return pts};
 const baseNow=ph===1?p.phase1Pct:p.phase2Pct,baseOther=ph===1?p.phase2Pct:p.phase1Pct;
 // 顏色跟著段別固定:第一段主色(橘),第二段綠;目前這段實線,另一段虛線
 const colOf=n=>n===1?'var(--accent)':'#65a30d',other=ph===1?2:1;
 let h=`<line x1="${X(p.minPct)}" y1="-100" x2="${X(p.minPct)}" y2="100" stroke="var(--mute)" stroke-dasharray="4 4" opacity=".6"/>`+
  `<line x1="${X(p.maxPct)}" y1="-100" x2="${X(p.maxPct)}" y2="100" stroke="var(--mute)" stroke-dasharray="4 4" opacity=".6"/>`+
  `<polyline points="${curve(baseOther)}" fill="none" stroke="${colOf(other)}" stroke-width="2" stroke-dasharray="5 4" opacity=".8"/>`+
  `<polyline points="${curve(baseNow)}" fill="none" stroke="${colOf(ph)}" stroke-width="3" opacity=".8" stroke-linejoin="round"/>`;
 for(const w of cvWalls(p,baseNow)){const x=X(w.kind==='max'?p.maxPct:p.minPct);h+=`<line x1="${x}" y1="${Y(w.to)}" x2="${x}" y2="${Y(w.from)}" stroke="#ef4444" stroke-width="4" opacity=".8"/>`}
 for(const v of [0,50,100])h+=`<text x="${X(v)+(v===0?2:v===100?-2:0)}" y="96" font-size="9" fill="var(--mute)" text-anchor="${v===0?'start':v===100?'end':'middle'}">${v}%</text>`;
 // 說明放左上角分兩行:右上是加油門的曲線,放右邊會被蓋住
 const tx=`font-size="9.5" font-weight="700" style="paint-order:stroke;stroke:var(--sky);stroke-width:3px"`;
 h+=`<text x="-155" y="-89" ${tx} fill="${colOf(ph)}">油門曲線 第${ph===1?'一':'二'}段(實線,目前)</text>`+
  `<text x="-155" y="-77" ${tx} fill="${colOf(other)}">第${other===1?'一':'二'}段(虛線)</text>`;
 g.innerHTML=h;
 // 目前角度紅線與實際輸出點
 const d=clamp(s.p,-90,90),out=flying?f.out:clamp(baseNow+cvComp(p,d),p.minPct,p.maxPct),y=Y(d),x=X(out);
 gn.innerHTML=`<line x1="-160" y1="${y}" x2="160" y2="${y}" stroke="#ef4444" stroke-width="2"/>`+
  `<circle cx="${x}" cy="${y}" r="5" fill="#ef4444" stroke="#fff" stroke-width="1.5"/>`+
  `<text x="${x>100?x-8:x+8}" y="${y>-80?y-6:y+14}" font-size="11" font-weight="700" fill="#ef4444" text-anchor="${x>100?'end':'start'}" style="paint-order:stroke;stroke:var(--card);stroke-width:3px">${Math.round(out)}%</text>`;
}

// WiFi 設定保護(GG 2026-09-14):試用中的發射功率或剛儲存的 WiFi 設定,連線正常要按「保持」,沒按自動退回
function renderWifiTrial(s){
 const w=s.wt;if(!w)return;
 const box=$('wifiTrial');let t='';
 if(w[0]>0)t=`發射功率 ${w[3]} dBm 試用中:連線正常請按「保持」,${Math.ceil(w[0])} 秒後自動退回`;
 else if(w[1])t=w[2]<0?'WiFi 設定剛變更,等待 WiFi 就緒…':`WiFi 設定剛變更:連線正常請按「保持」,${mmss(Math.ceil(w[2]))} 後自動改回上一次的設定`;
 box.hidden=!t;if(t)$('wifiTrialText').textContent=t;
}
$('btnWifiKeep').onclick=()=>post('/api/wifi/keep').then(r=>{if(r.ok)toast('已保持目前的 WiFi 設定.');else toast((CODES[r.code]||r.code)+' 試用計時暫停中,落地後再按保持.',true);tick()}).catch(()=>toast('連線失敗.',true));

// --- 韌體更新(GG 2026-09-14):板子自己下載,新韌體由開著的網頁自動確認 ---
// 狀態 fw:[更新中,待確認,確認剩餘秒數,檢查狀態(0 未檢查/1 檢查中/2 已讀到/3 下載中/4 完成/5 失敗),進度,已退回]
let FW=null,fwConfirmAt=0,fwArm=0;
async function fwLoad(){try{FW=await poll('/api/fw');fwRender()}catch(e){}}
function fwRender(){
 const f=FW;if(!f)return;
 $('fwVer').textContent=f.ver;
 $('fwPendBox').hidden=!f.pending;
 $('fwPendText').textContent=f.remain>=0?`網頁連上就會自動確認(不用按按鈕);${Math.ceil(f.remain)} 秒內沒有網頁連上會退回舊版. 確認前不能起飛.`:'等待 WiFi 就緒後開始計時. 確認前不能起飛.';
 $('fwRbBox').hidden=!f.rb;
 $('fwRbText').textContent=`上次更新${f.rbver?'到 '+f.rbver+' ':''}沒有完成確認,已自動退回,目前是 ${f.ver}. 請回報給提供韌體的人.`;
 // 板子逐段比版本數字(newer:1 網站比較新 / 0 相同 / -1 網站比較舊). 原本只比字串相不相同,板子 .12 網站 .11 也說有新版本.
 const c=f.check,newer=f.newer>0;
 $('btnFwCheck').disabled=c===1||c===3||c===4||!!f.busy;
 const t=c===1?'檢查中…(約需數秒)':c===2?(newer?`有新版本 ${f.rver}`:f.newer===0?`已是最新版 ${f.ver}`:`目前的 ${f.ver} 比網站上的 ${f.rver} 新,不需要更新`)
  :c===3?'下載安裝中,請勿斷電…':c===4?'安裝完成,重新開機中…':c===5?(CODES[f.err]||'失敗:'+f.err):'';
 $('fwCheckText').textContent=t;$('fwCheckText').className='sub'+(c===5?' bad':'');
 const show=!!f.rver&&((c===2&&f.newer>=0)||c===3||c===4);   // 網站版本比較舊時不顯示它的說明
 $('fwRemote').hidden=!show;
 if(show){
  $('fwNotes').textContent=`版本 ${f.rver}(${(f.rsize/1048576).toFixed(2)} MB)`+(f.notes?'\n'+f.notes:'');
  const b=$('btnFwInstall');b.hidden=c!==2||!newer;if(!fwArm)b.textContent=`更新到 ${f.rver}`;
  $('fwInstallText').textContent=c===3?`${f.prog}%,請勿斷電`:(c===2&&newer?'按兩下確認. 會重新開機,沒儲存的設定會不見.':'');
 }
 $('fwDlProg').hidden=c!==3;$('fwDlProg').value=f.prog;
}
function renderFw(s){
 const fw=s.fw;if(!fw)return;
 // 新韌體待確認:能跑到這裡代表新韌體的 WiFi,網頁伺服器與網頁程式都正常 → 自動確認
 if(fw[1]&&Date.now()-fwConfirmAt>5000){fwConfirmAt=Date.now();
  post('/api/fw/confirm').then(r=>{if(r.ok){toast('新韌體已確認採用.');fwLoad();tick()}}).catch(()=>{})}
 const bt=fw[0]?(fw[3]===3?`韌體下載安裝中 ${fw[4]}%,請勿斷電`:fw[3]===4?'韌體安裝完成,重新開機中…':'韌體更新中,請勿斷電'):(fw[1]?'正在確認新韌體…':'');
 $('fwBar').hidden=!bt;if(bt)$('fwBarText').textContent=bt;
 // 板子上的檢查狀態和畫面上的不同就重讀:原本只在「檢查中」時重讀,剛好在兩次讀取之間檢查完成,畫面會一直停在「檢查中…」
 if(pane==='sys'&&(fw[0]||fw[3]===1||fw[3]===3||fw[1]||!FW||FW.check!==fw[3]||FW.rb!==fw[5]))fwLoad();
}
$('btnFwCheck').onclick=async()=>{
 try{const r=await post('/api/fw/check');if(!r.ok)toast(CODES[r.code]||r.code,true)}catch(e){toast('連線失敗.',true)}
 fwLoad()};
$('btnFwInstall').onclick=async()=>{
 const b=$('btnFwInstall');if(!FW)return;
 if(!fwArm){fwArm=setTimeout(()=>{fwArm=0;fwRender()},3000);b.textContent='確定更新?再按一下';return}
 clearTimeout(fwArm);fwArm=0;
 try{const r=await post('/api/fw/install',{ver:FW.rver});toast(CODES[r.code]||r.code,!r.ok)}catch(e){toast('連線失敗.',true)}
 fwLoad()};
let inverted=false;
// 三軸格只換 <b> 裡的數字;格式最多 6 字元(角速度 ±999.9,超過 1000 改整數 ±2000;零點兩位小數),欄寬固定不會換行
function setAxes(id,values,dec){
 const b=document.getElementById(id).querySelectorAll('b');
 values.forEach((v,i)=>{b[i].textContent=v.toFixed(Math.abs(v)>=999.95?0:dec)});
}
// 只縮放真正超出兩行的數值;寬度/內容相同時不重算,文字變短會回到原始字級. 三軸格固定版面,不參與縮字
function fitSensorValues(){
 document.querySelectorAll('.sensor-grid .v:not(.ax)').forEach(e=>{
  const w=e.clientWidth;if(!w)return;
  const key=w+'|'+e.textContent;if(e._fitKey===key)return;
  e.style.fontSize='17px';
  const over=()=>e.scrollHeight>e.clientHeight||e.scrollWidth>e.clientWidth;
  for(let size=16.5;size>=11&&over();size-=.5)e.style.fontSize=size+'px';
  e._fitKey=e.clientWidth+'|'+e.textContent;
 });
}
window.addEventListener('resize',()=>requestAnimationFrame(fitSensorValues));
function renderStatus(s){
 ensureActiveProfile(s.act);
 drawMonitorCurve(s);
 STATUS=s;
 renderWifiTrial(s);
 renderFw(s);
 const right=VALS&&VALS.shared.noseRight===1;
 $('pitch').textContent=sgn(s.p,1)+'°';
 $('roll').textContent=sgn(s.r,0)+'°';
 // 倒飛判斷:滾轉超過 100° 算倒飛,回到 80° 內才算正飛(中間保持,不來回跳).
 // 機頭接近垂直時滾轉角沒有意義(數學上的奇異點),保持前一刻的判斷.
 if(Math.abs(s.p)<70){if(Math.abs(s.r)>100)inverted=true;else if(Math.abs(s.r)<80)inverted=false}
 const knife=Math.abs(s.p)<70&&Math.abs(s.r)>=60&&Math.abs(s.r)<=120;
 // 倒飛時機頭換到另一邊並且上下顛倒(GG 指定,符合飛友看飛機翻過去的直覺).
 // 機頭朝哪邊決定機頭角度的轉動方向:機頭朝右時,機頭抬起是逆時針.
 const noseRightNow=right!==inverted;
 $('planeFlip').setAttribute('transform',`scale(${noseRightNow?-1:1},${inverted?-1:1})`);
 const am=$('attMode');am.textContent=knife?'側飛':(inverted?'倒飛':'正飛');am.className='pill '+(knife?'warn':(inverted?'bad':'ok'));
 $('plane').setAttribute('transform',`rotate(${noseRightNow?-s.p:s.p})`);
 $('acc').textContent=s.a.toFixed(2)+' g';
 $('still').textContent=s.st?`是(${s.sts.toFixed(1)} 秒)`:'否';
 {const e=$('armSw');e.textContent=(s.f.arm?'已按下':'沒按下')+(s.asoff?'(已停用)':'');e.style.color=s.asoff?'var(--bad)':s.f.arm?'var(--ok)':'var(--mute)'}
 {const t=rpmText(s);$('esc').textContent=(s.proto?`DShot ${s.dsh}`:s.esc+' µs')+(t?(t.ok?` · ${t.rpm} RPM`:' · 轉速收不到'):'')}
 setAxes('gyro',s.g,1);
 setAxes('bias',s.b,2);
 $('timing').textContent=`${(s.ex/1000).toFixed(1)} ms / ${s.late} ms`;
 $('vib').textContent=s.vib.toFixed(2)+' g / '+(s.lvl?'是':'否');
 // 設定頁:手勢試推燈與提早降落即時狀態
 if($('gLamp')){$('gLamp').classList.toggle('on',!!s.glamp);
  $('gPush').textContent=`${Math.max(0,s.push).toFixed(2)} g · 3秒最大 ${Math.max(0,s.push3).toFixed(2)} g`}
 if($('dLamp')){const over=s.dist[2]>=0&&s.dist[2]<15;   // 1.5 秒內超過門檻
  $('dLamp').classList.toggle('warnon',over);
  $('dVal').textContent=`${s.dist[0].toFixed(2)} g · 3秒最大 ${s.dist[1].toFixed(2)} g`}
 if($('elVib')&&VALS){const sh=VALS.shared;
  $('elVib').textContent=`抖動 ${s.vib.toFixed(2)} g`;$('elLvl').textContent=s.lvl?'正飛水平':'非水平';
  $('elMeter').style.width=Math.min(100,s.hold/sh.earlyLandHold*100)+'%';
  $('elHold').textContent=`已持續 ${s.hold.toFixed(1)} / ${sh.earlyLandHold} 秒`}
 if($('gearState')&&s.gear){const p=s.gear[0],idle=s.f.s===1||s.f.s===7;
  $('gearState').textContent=p<=0?'放下':p>=100?'收起':`移動中 ${p}%`;$('gearUs').textContent=`${s.gear[1]} µs`+(s.gear[2]?' · 試收輪中':'');
  $('btnGearTest').textContent=s.gear[2]?'放下':'試收輪';$('btnGearTest').disabled=!idle&&!s.gear[2]}
 $('impact').textContent=s.imp[2]<0?'尚未發生':`${s.imp[0].toFixed(2)} g / ${s.imp[1]} ms(${s.imp[2]} 秒前)`;
 $('setPitch').textContent=sgn(s.p,1)+'°';
 $('setRaw').textContent=sgn(s.rp,1)+'°';
 instDraw(s);
 escRender(s);
 if(VALS){
  const name=VALS.names[s.act],act=VALS.edit===s.act?VALS.profile:null;
  $('compPreview').textContent=act?`飛行風格「${name}」在這個角度補償 ${sgn(s.cmp,1)}%:第一段實際 ${Math.min(act.maxPct,Math.max(act.minPct,act.phase1Pct+s.cmp)).toFixed(0)}%,第二段實際 ${Math.min(act.maxPct,Math.max(act.minPct,act.phase2Pct+s.cmp)).toFixed(0)}%`
   :`飛行風格「${name}」在這個角度補償 ${sgn(s.cmp,1)}%`;
 }
 if(s.imu===0)pill('pillImu','bad','感測器未連接');else if(s.imu===2)pill('pillImu','bad','感測器故障,請重新上電');else pill('pillImu','ok','感測器正常');
 const modes=['連線中','家用 WiFi','自身熱點'];
 pill('pillNet',s.ws===0?'warn':'ok',modes[s.ws]||'?');
 $('pillLock').hidden=!s.lock;
 // 忽略安全開關:每一頁上方都一直顯示(含還沒儲存的值,寧可多警告)
 $('asOffBar').hidden=!s.asoff;
 if(s.asoff)$('asOffText').textContent=s.f.ge?'推一下飛機或按開始,放穩後就倒數,不必按開關. 倒數完馬達啟動.':'接上電池,飛機放平就開始倒數,倒數完馬達啟動. 接電池前確認螺旋槳旁沒有人.';
 $('netMode').textContent=modes[s.ws]+(s.ws===0?`(剩 ${s.cd} 秒)`:'');
 $('netIp').textContent=s.ip||'--';
 $('netRssi').textContent=s.ws===1?s.rssi+' dBm':'--';
 $('uptime').textContent=fmtUp(s.up);
 $('heap').textContent=Math.round(s.heap/1024)+' KB';
 renderFlight(s.f);
 evSync(s);
 if(pane==='comp')updateCurveNow(s);
 // 別的裝置或序列埠存檔後,這裡的未儲存提示要跟著消失
 if(VALS){if(valsDirty()!==!!s.dirty)loadVals()}
 if(pane==='bak')bkRender();   // 起飛程序鎖定時不能套用
 if(pane==='mon')fitSensorValues();
}

let busy=false;
async function tick(){
 if(busy||document.hidden)return;busy=true;
 try{renderStatus(await poll('/api/status'))}catch(e){pill('pillNet','bad','連線中斷')}
 finally{busy=false}
}
setInterval(()=>{if(pane==='mon'||pane==='set'||pane==='comp'||pane==='inst'||pane==='esc')tick()},250);
setInterval(()=>{if(pane==='prof'||pane==='sys'||pane==='log')tick()},1000);

// --- 事件紀錄 ---
// 韌體只存數字(種類,參數,a,b),文字與排查方向在這裡組. 格式見 src/event_log.h.
let evKnown=0,evLines=[],evFetching=false,evMotorMs=-1,evDropped=0;
const BOOT_TEXT={1:['上電開機',''],3:['軟體重新開機','網頁重新開機,韌體更新後會這樣.'],4:['程式當機後重新開機','請記下前後發生的事回報開發者.'],
 5:['看門狗重新開機(中斷)','請回報開發者.'],6:['看門狗重新開機(工作)','請回報開發者.'],7:['看門狗重新開機','請回報開發者.'],
 9:['電壓不足重新開機','板子供電掉太低:檢查 BEC 或降壓板,電池接頭,馬達加速時電壓是否被拉低. 如果這行出現在飛行中,馬達停轉就是這個原因.'],
 11:['USB 重置','燒錄或序列埠連線造成.'],14:['電源干擾重新開機','檢查供電與接地.']};
const REJ_TEXT=['','有未儲存的變更,請先按儲存','感測器異常','機身角度超過起飛前水平限制','上電自動倒數暫停:機身角度超過起飛前水平限制','韌體更新中','新韌體還沒確認(網頁連上會自動確認)',
 '安全開關沒有按下','上電自動倒數暫停:等安全開關按下','撞擊斷電後推飛機不會啟動','電變輸出腳位沒有訊號(開機掛載失敗,請重新開機或回報)'];
function evText(e){
 const [seq,ms,ty,arg,a,b]=e,s1=v=>v.toFixed(1),s2=v=>v.toFixed(2),fl=()=>evMotorMs>=0?`(飛行 ${mmss(Math.max(0,Math.round((ms-evMotorMs)/1000)))})`:'';
 switch(ty){
  case 1:{const t=BOOT_TEXT[Math.round(a)]||[`重新開機(原因代碼 ${Math.round(a)})`,''];return {c:[1,3,11].includes(Math.round(a))?'dim':'bad',m:t[0],h:t[1]}}   // 上電,軟體重開,USB 是正常操作
  case 2:return {c:'dim',m:['電變解鎖完成,開始上電自動倒數','電變解鎖完成,等待啟動手勢','電變解鎖完成(手勢關閉且自動倒數已用過,要飛請重新上電)','電變解鎖完成,不自動倒數(這次不是拔電再接電)'][arg]||'電變解鎖完成',
   h:arg===3?'安全設計:更新韌體,網頁重新開機,當機重開後都不會自己倒數. 要飛請拔掉電池再接上.':''};
  case 3:return {c:'',m:arg===2?'網頁按「開始起飛程序」':arg?'序列埠模擬啟動手勢':`啟動手勢成立(推力 ${s2(a)} g)`,h:''};
  case 4:{const lim=VALS?VALS.shared.startLevel:'?';
   if(arg===3)return {c:'bad',m:`拒絕啟動:${REJ_TEXT[3]}(機頭 ${s1(a)}°,滾轉 ${s1(b)}°,限制 ±${lim}°)`,h:'把飛機放平再推啟動手勢. 停放時機頭本來就朝上的話,到設定頁把「起飛前水平限制」調大.'};
   if(arg===4)return {c:'bad',m:`${REJ_TEXT[4]}(機頭 ${s1(a)}°,滾轉 ${s1(b)}°,限制 ±${lim}°)`,h:'飛機放平並維持 1 秒就會開始倒數.'};
   if(arg===7)return {c:'bad',m:'拒絕啟動:安全開關沒有按下',h:'GPIO21 的微動開關要接地(按下)才能開始起飛程序. 沒接開關或線斷掉都算沒按下.'};
   if(arg===8)return {c:'bad',m:REJ_TEXT[8],h:'按下安全開關並維持 1 秒就會開始倒數.'};
   if(arg===9)return {c:'bad',m:`拒絕啟動:撞擊斷電後推飛機不會啟動(推力 ${s2(a)} g)`,h:'撞機後撿飛機,扶正時很容易推到. 要再飛請按網頁「開始起飛程序」,或拔電再接電.'};
   return {c:'bad',m:'拒絕啟動:'+(REJ_TEXT[arg]||arg),h:''}}
  case 5:{const mx=b>0?`(剛才外力最大 ${s2(b)} g)`:'';return {c:'',m:arg===1?`放穩,延長後繼續倒數,剩 ${s1(a)} 秒${mx}`:arg===2?`放穩,重新倒數 ${s1(a)} 秒${mx}`:`開始倒數 ${s1(a)} 秒`,h:''}}
  case 6:return {c:'',m:`倒數中外力超過門檻 ${s2(b)} g,等飛機放穩`,h:''};
  case 7:return {c:'',m:'網頁取消倒數',h:''};
  case 8:{evMotorMs=ms;const n=VALS&&VALS.names[arg]?`「${VALS.names[arg]}」`:`#${arg}`;return {c:'good',m:`馬達啟動(風格${n},`+(b>0?`起飛油門 ${Math.round(b)}%,`:'')+`第一段 ${Math.round(a)}%)`,h:''}}
  case 9:return {c:'',m:`換到第二段${fl()}`,h:''};
  case 10:return arg===2?{c:'land',m:`觸地提早降落觸發:正飛水平且 Z 軸抖動持續 ${s1(b)} 秒${fl()}`,h:'如果當時沒有碰地:到紀錄頁看 Z 軸抖動數值,調高「Z 軸抖動門檻」或「抖動持續秒數」,或在設定頁關閉觸地提早降落.'}
   :{c:'land',m:`總飛行時間到,開始降落${fl()}`,h:''};
  case 11:{let r;switch(arg){
   case 1:r={m:`觸地衝擊 ${s2(a)} g(門檻 ${s2(b)} g),關馬達`,h:''};break;
   case 2:r={m:`完全靜止 ${s1(a)} 秒(門檻 ${s1(b)} 秒),判定已觸地,關馬達`,h:'如果當時還在空中:調長「觸地靜止判定」秒數.'};break;
   case 3:r={m:`地面滑行抖動持續 ${s1(a)} 秒,判定已觸地,關馬達`,h:''};break;
   case 4:r={m:`降落 ${s1(a)} 秒都沒判定觸地,保險時間到關馬達`,h:'如果飛機早就落地:觸地衝擊門檻可能太高,到監看頁輕敲飛機看「最近觸地衝擊」數值.'};break;
   case 5:r={m:`撞擊斷電:衝擊 ${s2(a)} g ≥ 門檻 ${s2(b)} g`,h:'如果是飛行中做特技誤觸:到紀錄頁看總 G 力最高值,調高撞擊門檻.'};break;
   case 6:r={m:'網頁緊急停止',h:''};break;
   case 11:r={m:`長按安全開關 ${s1(a)} 秒,強制停機`,h:''};break;
   case 12:r={m:`搖擺機尾 3 個來回(每次超過 ${Math.round(b)}°),強制停機`,h:'如果沒有人搖機尾:到設定頁把「搖擺機尾停機角度」調大,或設 0 關閉.'};break;
   default:r={m:`馬達停止(原因代碼 ${arg})`,h:''};}
   const out={c:'stop',m:r.m+fl(),h:r.h};evMotorMs=-1;return out}
  case 12:return {c:'bad',m:arg===2?'開機時找不到感測器':arg===1?'飛行中感測器讀取失敗:角度補償停止,撞擊與觸地判斷失效':'感測器讀取失敗',h:'這次通電不再使用感測器,就算之後恢復也一樣,要重新上電. 檢查感測器接線與焊點(震動容易鬆脫),以及供電.'};
  case 13:return arg?{c:'bad',m:'感測器又有回應,但這次通電不採用(故障過的感測器資料不可信)',h:'時好時壞通常是接觸不良. 檢查接線後重新上電.'}:{c:'good',m:'感測器恢復',h:''};
  case 14:return {c:'',m:'網頁手動輸出開始',h:''};
  case 15:return {c:'',m:arg?'網頁手動輸出結束(心跳逾時,回最低油門)':'網頁手動輸出結束',h:''};
  case 16:return {c:'',m:`電變校正開始:輸出最高 ${Math.round(a)} µs,保持 ${s1(b)} 秒`,h:''};
  case 17:return {c:'good',m:`電變校正:切到最低 ${Math.round(a)} µs`,h:'聽電變確認音判斷是否成功,要飛請重新通電.'};
  case 18:return {c:'bad',m:`控制迴圈延遲 ${Math.round(a)} ms`,h:'偶爾一次通常是 WiFi 連線瞬間;頻繁出現請回報.'};
  case 19:return {c:'bad',m:'感測器量程飽和(超過 16 g 或 2000°/秒)'+(arg?',馬達運轉中':''),h:'劇烈撞擊或震動;常出現時檢查感測器固定方式與螺旋槳平衡.'};
  case 21:return {c:'land',m:`起飛程序中角度超過水平限制,取消(機頭 ${s1(a)}°,滾轉 ${s1(b)}°,限制 ±${arg}°)`,h:'倒數或等待放穩時飛機被拿起或傾斜. 如果飛機其實停在地上沒動:停放角度可能太大,到設定頁把「起飛前水平限制」調大.'};
  case 24:return arg===1?{c:'bad',m:'連續開關電 3 次:WiFi 設定已回出廠(自身熱點 HappySuperGG_Plane)',h:'手機連熱點 HappySuperGG_Plane(密碼 12345678),開 192.168.4.1 重新設定家用 WiFi.'}
   :arg===2?{c:'bad',m:'WiFi 設定沒有在 3 分鐘內按「保持」,已改回上一次的設定',h:'如果新設定其實連得上:重新儲存後記得按保持.'}
   :arg===4?{c:'bad',m:`家用 WiFi 斷線超過 ${Math.round(a)} 秒連不回來,已改開自身熱點`,h:'手機連自身熱點(密碼是系統頁設定的熱點密碼,出廠 12345678),開 192.168.4.1. 家用 WiFi 恢復後重新開機就會再連回去.'}
   :{c:'bad',m:`發射功率沒有在 15 秒內按「保持」,已退回 ${Math.round(a)} dBm`,h:''};
  case 26:return arg===2?{c:'land',m:'電變校正已取消:這次開機不是拔電再接電',h:'校正只給「按下後馬上拔電再接電」用. 網頁重新開機,韌體更新,當機重開都會取消,要校正請重新設定.'}
   :{c:'land',m:'電變校正已自動取消:設定後 10 秒內沒有拔電',h:'免得忘記後哪天裝著螺旋槳接電池就是全速. 要校正請手先放在電池接頭旁,重新按下後 10 秒內拔電再接上.'};
  case 27:return {c:'dim',m:arg===1?'起飛程序或飛行中,發射功率試用的退回延後到落地':'起飛程序或飛行中,WiFi 設定試用的退回延後到落地',h:'飛行中不改 WiFi,落地後試用時間繼續算,可以按「保持」.'};
  case 25:{const src=['網頁上傳','無線燒錄','板子下載'][Math.round(a)]||'';
   return [{c:'good',m:'新韌體已確認採用',h:''},
    {c:'land',m:'新韌體第一次開機,等待確認',h:'網頁連上就會自動確認,不用按按鈕;連上 WiFi 後 1 分鐘內沒有網頁連上,自動退回舊版. 由網頁確認,才能保證更新完之後還控制得到板子. 確認前不能起飛.'},
    {c:'bad',m:'上次更新的新韌體沒有完成確認,已自動退回舊版',h:'可能是新韌體連不上 WiFi 或網頁. 請回報給提供韌體的人.'},
    {c:'',m:`開始更新韌體(${src})`,h:''},
    {c:'',m:'韌體寫入完成,重新開機',h:''},
    {c:'bad',m:'韌體更新失敗,繼續使用目前的版本',h:'下載中斷或檔案不對時會這樣,目前韌體沒有改變,可以再試一次.'},
    {c:'bad',m:'新韌體沒有在時限內確認,退回舊版',h:''}][arg]||{c:'dim',m:`韌體更新(${arg})`,h:''}}
  case 23:return {c:'dim',m:arg?`收輪(飛行 ${mmss(Math.round(a))})`:(a>0?`放輪(飛行 ${mmss(Math.round(a))})`:'放輪'),h:''};
  case 28:{const sec=Math.round(a),dur=sec>=60&&sec%60===0?`${sec/60} 分鐘`:`${sec} 秒`;
   if(arg===3)return {c:'land',m:`等安全開關超過 ${dur},自動取消起飛程序`,h:'要飛再推一下飛機或按「開始起飛程序」. 等待時間在設定頁「安全開關等待上限」調整.'};
   if(arg===4)return {c:'land',m:`上電自動倒數:等安全開關超過 ${dur},這次通電不再自動倒數`,h:'要飛請拔掉電池再接上. 等待時間在設定頁「安全開關等待上限」調整.'};
   if(arg===5)return {c:'bad',m:'安全開關已停用:這趟起飛程序不等開關',h:'設定頁「啟動與倒數」停用了安全開關. 要恢復,按「恢復使用安全開關」再儲存.'};
   if(arg===6)return {c:'land',m:'上電自動倒數等待中改成手勢啟動,這次通電不再自動倒數',h:'改回「上電後直接倒數」也要拔電再接電才會自動倒數.'};
   return arg===2?{c:'good',m:'安全開關按下',h:''}
   :{c:'',m:arg===1?'上電自動倒數:等安全開關按下':'飛機已放穩,等安全開關按下才開始倒數',h:arg===1?'按下安全開關(飛機放平)就開始倒數.':'按下安全開關就開始倒數.'}}
  case 22:return {c:'bad',m:arg?'測試用感測器模擬開啟(USB 序列指令)':'測試用感測器模擬關閉',h:arg?'只有開發測試會出現. 模擬中角度與 G 力都是假的,重新開機即清除.':''};
  case 20:return {c:'land',m:(a>0?`扭轉機尾 ${Math.round(a)}°(門檻 ${Math.round(b)}°),取消起飛`:'序列埠模擬扭轉,取消起飛')+`,${arg} 秒內不接受手勢`,h:'如果不是故意扭轉:放飛機時轉動太多也會取消,可以在設定頁把角度調大.'};
 }
 return {c:'dim',m:`事件 ${ty}(${arg},${s2(a)},${s2(b)})`,h:''};
}
function evRender(){
 const box=$('evBox');if(!box)return;
 const atBottom=box.scrollHeight-box.scrollTop-box.clientHeight<30;
 box.innerHTML=(evDropped?`<div class="ev dim"><span class="et"></span><span class="em">(較早的 ${evDropped} 筆已被新的紀錄覆蓋)</span></div>`:'')+
  (evLines.length?evLines.map(l=>`<div class="ev ${l.c}"><span class="et">${(l.ms/1000).toFixed(1)} 秒</span><span class="em"><b>${esc(l.m)}</b>${l.h?`<span class="eh">${esc(l.h)}</span>`:''}</span></div>`).join(''):'<div class="sub" style="padding:4px 10px">還沒有事件</div>');
 if(atBottom)box.scrollTop=box.scrollHeight;   // 使用者往上捲看舊紀錄時不要跳走
}
async function evSync(s){
 if(evFetching||s.evn===undefined)return;
 if(s.evn<evKnown){evKnown=0;evLines=[];evMotorMs=-1;evDropped=0}   // 板子重開過
 if(s.evn===evKnown&&evLines.length)return;
 evFetching=true;
 try{const r=await poll('/api/events?since='+evKnown);
  if(r.oldest>evKnown)evDropped+=r.oldest-evKnown;
  for(const e of r.ev){const t=evText(e);evLines.push({ms:e[1],c:t.c,m:t.m,h:t.h})}
  evKnown=r.total;evRender();
 }catch(e){}finally{evFetching=false}
}

// --- 飛行狀態列 ---
const END_TEXT=['','降落觸地(衝擊)','降落觸地(靜止)','降落觸地(地面滑行)','降落保險時間到','撞擊斷電','緊急停止','已取消','扭轉機尾取消','角度超過水平限制取消','等安全開關超過上限取消','長按安全開關強制停機','搖擺機尾強制停機'];
let cdMax=0;
function renderFlight(f){
 const bar=$('fbar'),tm=s=>mmss(Math.max(0,Math.floor(s)));
 const pname=i=>VALS?'「'+VALS.names[i]+'」':'';
 const us=p=>VALS?Math.round(VALS.shared.escMinUs+(VALS.shared.escMaxUs-VALS.shared.escMinUs)*p/100)+' µs':'';
 let title='--',detail='',cls='',badge='狀態';
 switch(f.s){
  case 0:badge='開機';title='電變解鎖中';break;
  case 1:badge='待機';title='待機';detail=f.ge?'推一下飛機,或按「開始起飛程序」;放穩後按安全開關開始倒數':(f.au?'要飛請拔掉電池再接上(上電倒數每次通電一次,重開機不算)':'');
   if(f.er===9&&f.ss<15){title='待機(角度超過水平限制,已取消起飛)';detail=(f.ge?'放平後再推一下飛機':'要再飛請重新上電')}
   if(f.er===10)title='待機(等安全開關超過上限,已自動取消起飛)';   // 取消時通常沒人在旁邊,留著到下一次開始
   if(f.gb>0){title='待機(已扭轉機尾取消起飛)';detail=`${f.gb.toFixed(1)} 秒後才接受啟動手勢`}
   // 上電自動倒數在待機等:安全開關還沒按過 → 等安全開關;按過但沒放平 → 等待放平
   if(f.aw){cls='wait';badge=f.al?'等待放平':'等安全開關';title=f.al?'角度超過水平限制,暫不倒數':'等待安全開關';
    detail=f.al?`把飛機放平(機頭與滾轉 ±${VALS?VALS.shared.startLevel:'?'}° 內)並維持 1 秒就開始倒數`:'按下安全開關就開始倒數(飛機要放平)'+(f.awl>=0?`,${mmss(f.awl)} 內沒按自動取消`:'')}
   break;
  case 2:cls='wait';badge='起飛程序';
   if(!f.al&&f.set>=1){title='等待安全開關';detail='飛機已放穩,按下安全開關就開始倒數'}
   else{title='等待放穩';detail=`放穩 ${Math.min(1,f.set).toFixed(1)} / 1.0 秒`+(f.al?'':',放穩後按安全開關開始倒數')}
   if(!f.al&&f.awl>=0)detail+=`,${mmss(f.awl)} 內沒按自動取消`;
   if(f.da&&f.dga>=0&&f.dga<600)detail+=`,外力最大 ${f.dg.toFixed(2)} g,放穩後${f.da===1?'延長秒數(倒數最多 '+((VALS?VALS.shared.countdownSec:0)+10)+' 秒)':'重新倒數'}`;break;
  case 3:cls='count';badge='起飛倒數';title=`倒數 ${f.cd.toFixed(1)} 秒`;detail=`風格${pname(f.fp)}`;break;
 }
 // 手勢起飛的等待放穩/倒數中:提示可以扭轉機尾取消,顯示目前扭轉角度
 if((f.s===2||f.s===3)&&f.ge&&VALS&&VALS.shared.twistCancel>0)detail+=`,扭轉機尾 ${Math.abs(f.tw).toFixed(0)}° / ${VALS.shared.twistCancel}° 取消`;
 switch(f.s){
  case 4:cls='fly';badge='馬達運轉';title=`緩啟動 ${f.out.toFixed(0)}%`;detail=`${tm(f.t)},${us(f.out)}`;break;
  case 5:cls='fly';badge='馬達運轉';title=f.tb?`飛行中 起飛油門 ${tm(f.t)}`:`飛行中 第${f.ph===1?'一':'二'}段 ${tm(f.t)}`;
   detail=`油門 ${f.out.toFixed(0)}%(基本 ${f.base.toFixed(0)} ${f.comp>=0?'+':''}${f.comp.toFixed(0)}),${us(f.out)}`;break;
  case 6:cls='land';badge='馬達運轉';title=`降落中(${f.lc===2?'觸地提早降落':'時間到'})`;detail=(f.lp?'忽高忽低提醒中,':'')+`油門 ${f.out.toFixed(0)}%,${tm(f.t)}`;break;
  case 7:cls=f.er===5?'crash':'done';badge='已結束';title=`已結束:${END_TEXT[f.er]||''}`;
   detail=(f.t>0?`飛行 ${tm(f.t)},`:'')+(f.ge?(f.er===5?'撞擊斷電後推飛機不會啟動;要再飛請按「開始起飛程序」或拔電再接電':'推一下或按「開始起飛程序」可再飛'):'要再飛請重新上電');break;
 }
 if(f.rj&&f.rj!==4&&f.rja>=0&&f.rja<50){detail='拒絕啟動:'+(REJ_TEXT[f.rj]||f.rj)+(detail?','+detail:'');if(!cls||cls==='done'){cls='reject';badge='拒絕啟動'}}
 bar.className='fbar '+cls;$('fBadge').textContent=badge;$('fState').textContent=title;$('fDetail').textContent=detail;
 // 倒數進度條:剩餘比例. 分母取這次倒數看過的最大值(外力延長後會變大)
 if(f.s===3){cdMax=Math.max(cdMax,f.cd,VALS?VALS.shared.countdownSec:0);$('fProgBox').hidden=false;$('fProg').style.width=(100*f.cd/cdMax).toFixed(1)+'%'}
 else{cdMax=0;$('fProgBox').hidden=true}
 $('btnCancel').hidden=!(f.s===2||f.s===3);
 $('btnEstop').hidden=!(f.s>=4&&f.s<=6);
 // 開始起飛程序:手勢開啟時的待機/結束才出現(上電自動倒數模式每次上電只飛一次,不給按)
 const canStart=(f.s===1||f.s===7)&&f.ge&&!f.aw&&!(f.gb>0);
 $('btnStart').hidden=!canStart;if(!canStart)startDisarm();
}
$('btnCancel').onclick=()=>post('/api/cancel').then(()=>tick()).catch(()=>toast('連線失敗.',true));
// 開始起飛程序:按兩下才送出(3 秒內),避免手機放口袋或誤觸就開始倒數
let startArmed=false,startTimer=0;
function startDisarm(){startArmed=false;clearTimeout(startTimer);const b=$('btnStart');b.classList.remove('arm');b.textContent='開始起飛程序'}
$('btnStart').onclick=()=>{const b=$('btnStart');
 if(!startArmed){startArmed=true;b.classList.add('arm');b.textContent='確定開始?再按一下';startTimer=setTimeout(startDisarm,3000);return}
 startDisarm();
 post('/api/start').then(r=>{if(!r.ok)toast(CODES[r.code]||r.code,true);else toast('開始起飛程序:把飛機放穩,按下安全開關開始倒數.');tick()}).catch(()=>toast('連線失敗,沒有開始.',true))};
(function(){
 let taps=0,timer=0;const b=$('btnEstop'),label='緊急停止(連按三下)';
 b.onclick=()=>{clearTimeout(timer);taps++;
  if(taps>=3){taps=0;b.textContent=label;post('/api/estop').then(()=>{toast('已送出緊急停止.');tick()}).catch(()=>toast('緊急停止送出失敗,請再連按三下!',true));return}
  b.textContent=`再按 ${3-taps} 下停止`;timer=setTimeout(()=>{taps=0;b.textContent=label},1500)};
})();

// --- 電變頁:手動輸出與校正精靈 ---
// 手動輸出:解鎖後每 0.2 秒送一次目前滑桿值當心跳,韌體 0.5 秒沒收到就回最低油門並結束.
let manOn=false,manTimer=0,manSending=false;
function escRange(){const s=VALS?VALS.shared:{escMinUs:1000,escMaxUs:2000};return [s.escMinUs,s.escMaxUs]}
const escIdle=s=>!!s&&(s.f.s===1||s.f.s===7);
async function manBeat(){
 if(!manOn||manSending)return;manSending=true;
 try{const r=await post('/api/manual',{us:$('manSlider').value});if(!r.ok){toast(CODES[r.code]||r.code,true);manLock(false)}}
 catch(e){}   // 單次失敗不處理:韌體逾時會自己回最低油門
 finally{manSending=false}
}
function manUnlock(){
 const [mn,mx]=escRange(),sl=$('manSlider');
 sl.min=mn;sl.max=mx;sl.value=mn;   // 一律從最低油門開始
 manOn=true;manBeat();manTimer=setInterval(manBeat,200);manUi();
}
function manLock(send){
 const was=manOn;manOn=false;clearInterval(manTimer);manTimer=0;
 $('manSlider').value=escRange()[0];
 if(was||send)post('/api/manual/stop').catch(()=>{});
 manUi();
}
function manUi(){
 $('manSlider').disabled=!manOn;
 document.querySelectorAll('.man-btns .b').forEach(b=>b.disabled=!manOn);
 $('btnManUnlock').hidden=manOn;$('btnManLock').hidden=!manOn;
 $('btnManUnlock').disabled=!$('manProp').checked||!escIdle(STATUS);
}
$('manProp').onchange=()=>{if(!$('manProp').checked&&manOn)manLock(true);manUi()};
$('btnManUnlock').onclick=manUnlock;
$('btnManLock').onclick=()=>manLock(true);
$('manSlider').oninput=()=>{manBeat();escRender(STATUS)};   // 拖動時立即送,不等下一次心跳
document.querySelectorAll('.man-btns .b').forEach(b=>b.onclick=()=>{
 const [mn,mx]=escRange(),sl=$('manSlider'),d=b.dataset.d;
 sl.value=d==='min'?mn:d==='max'?mx:clamp(Number(sl.value)+Number(d),mn,mx);manBeat();escRender(STATUS)});
// 切到別的 App,關分頁,手機鎖螢幕:立即上鎖(韌體那邊也會在 0.5 秒後逾時)
document.addEventListener('visibilitychange',()=>{if(document.hidden)manLock(false)});
window.addEventListener('pagehide',()=>manLock(false));
async function calSet(on){
 try{const r=await post('/api/calib',{on:on?1:0});toast(CODES[r.code]||r.code,!r.ok)}catch(e){toast('連線失敗,請再試一次.',true)}
 tick();
}
$('btnCalOn').onclick=()=>calSet(true);$('btnCalOff').onclick=()=>calSet(false);
$('calProp').onchange=()=>escRender(STATUS);
function escRender(s){
 if(pane!=='esc'||!s)return;
 const [mn,mx]=escRange(),us=s.esc,pct=mx>mn?(us-mn)*100/(mx-mn):0,idle=escIdle(s);
 // 輸出協定:開機套用中的 vs 設定裡的
 const PN=['PWM','DShot150','DShot300'],want=VALS?VALS.shared.escProtocol:s.proto,dsh=s.proto!==0;
 if($('protoPill')){
  const label=(p,hz)=>p===0?`PWM ${hz}Hz`:PN[p],wantHz=VALS?VALS.shared.escPwmHz:s.hz;
  pill('protoPill',dsh?'ok':'','目前輸出 '+label(s.proto,s.hz));
  const wantRpm=VALS?(VALS.shared.escRpm&&want===2?1:0):s.rpm[0];
  const pending=want!==s.proto||(want===0&&wantHz!==s.hz)||wantRpm!==s.rpm[0];
  $('protoText').textContent=!pending?'':(s.dirty?`已改成 ${label(want,wantHz)},請先按上方的儲存,再重新開機.`:`已儲存為 ${label(want,wantHz)},重新開機後生效.`);
  for(const w of WIDGETS){
   if(w.key==='escPwmHz')w.el.hidden=want!==0;                          // DShot 不用 PWM 頻率
   if(w.key==='escRpm')w.el.hidden=want!==2;                            // 轉速回傳只有 DShot300
   if(w.key==='motorPoles')w.el.hidden=want!==2||!(VALS&&VALS.shared.escRpm);
  }
  rpmRender(s);
  $('btnProtoReboot').hidden=!pending||!!s.dirty||!idle;
 }
 $('manOut').textContent=dsh?(s.dsh===0?'DShot 停止(0)':`DShot ${s.dsh}`):us+' µs';
 $('manPct').textContent=`油門 ${Math.max(0,pct).toFixed(0)}%`+(manOn&&Number($('manSlider').value)!==us?`(滑桿 ${$('manSlider').value} µs)`:'');
 if(manOn&&!idle){manLock(false);toast(CODES.manualstate,true)}
 if(s.man)pill('manPill','warn','手動輸出中');
 else if(manOn)pill('manPill','bad','等待板子回應');
 else pill('manPill',idle?'':'bad',idle?'已上鎖':'現在不能用(不在待機)');
 manUi();
 // 校正精靈狀態
 const [cs,rem,pend,pon,expire]=s.cal;
 if(cs===1){pill('calPill','warn','校正中');$('calText').textContent=`輸出最高油門,再 ${rem.toFixed(1)} 秒切到最低`}
 else if(pend){pill('calPill','warn','下次通電校正');$('calText').textContent=expire>=0?`現在拔掉電池再接上!剩 ${Math.ceil(expire)} 秒,沒拔會自動取消.`:'已設定. 拔掉電池再接上就開始校正.'}
 else if(cs===2){pill('calPill','ok','這次開機已完成校正');$('calText').textContent='電變發出確認音就是成功. 要飛請重新通電.'}
 else{pill('calPill','','未設定');$('calText').textContent=''}
 if(want!==0&&!pend){pill('calPill','','不需要');$('calText').textContent='DShot 是數位油門,不需要校正行程.'}
 $('btnCalOn').hidden=!!pend;$('btnCalOff').hidden=!pend;
 $('btnCalOn').disabled=!$('calProp').checked||!idle||want!==0;
}
// --- 轉速回傳 ---
// 狀態 rpm:[啟用,送框,收到,成功,失敗,沒回傳,週期µs(65535 = 停止),距上次成功 ms]. 成功率用兩次輪詢的差算.
let rpmPrev=null;
function rpmText(s){
 const r=s.rpm;if(!r||!r[0])return null;
 const poles=VALS?Math.max(2,VALS.shared.motorPoles||14):14;
 if(r[7]<0||r[7]>1000)return {ok:false,rpm:null};
 const rpm=r[6]===65535?0:Math.round(60e6/r[6]*2/poles);
 return {ok:true,rpm};
}
function rpmRender(s){
 const box=$('rpmLive');if(!box)return;
 const r=s.rpm;box.hidden=!r||!r[0];if(box.hidden){rpmPrev=null;return}
 let rate=null;
 if(rpmPrev&&r[1]>rpmPrev[1])rate=(r[3]-rpmPrev[3])*100/(r[1]-rpmPrev[1]);
 rpmPrev=r.slice();
 const t=rpmText(s);
 $('rpmVal').textContent=t.ok?`${t.rpm} RPM`:'-- RPM';
 if(!t.ok){pill('rpmPill','bad','收不到回傳');$('rpmText').textContent='電變沒有回傳轉速:確認電變韌體支援雙向 DShot 並已接電池;不支援就把轉速回傳關閉.'}
 else if(rate!==null&&rate<90){pill('rpmPill','warn','回傳不穩');$('rpmText').textContent=`成功率 ${rate.toFixed(1)}%. 檢查訊號線長度與接地.`}
 else{pill('rpmPill','ok','回傳正常');$('rpmText').textContent=rate===null?'':`成功率 ${rate.toFixed(1)}%`}
}

// --- 各廠牌校正說明(依 docs/電變校正說明查證_2026-09-13.md;a:ok=自動精靈可用,man=建議手動輸出,no=不需要或不要做) ---
const ESC_BRANDS=[
 {n:'好盈 Skywalker V2 / FlyFun V5',a:'ok',t:'自動精靈:保持 3~6 秒',need:'需要(第一次使用或換發射機). 預設行程 1100~1940µs.',
  s:['油門最高,接電池,響「♪123」','兩聲短嗶 = 最高點接受(上電約 2 秒)','兩聲短嗶後 5 秒內拉到最低,1 秒後接受','嗶聲 = 電池節數','長嗶一聲 = 完成'],
  w:'上電約 7 秒還在最高會響「56712」進程式設定模式.',c:'已查證',src:[['Skywalker V2','https://www.hobbywing.com/en/uploads/file/20230321/69381b562c41439ee4451c7152905f10.pdf'],['FlyFun V5','https://www.hobbywing.com/en/uploads/file/20221015/12f49cbe05185401b0773cfe8f019dce.pdf']]},
 {n:'好盈 Skywalker V1(舊款)',a:'ok',t:'自動精靈:保持 3~6 秒',need:'需要,換發射機要重做.',
  s:['油門最高,接電池,等約 2 秒','「Beep-Beep-」= 最高點確認','拉到最低,幾聲短嗶 = 電池節數','長嗶一聲 = 完成'],w:'',c:'已查證',src:[['SkyWalker ESC 說明書','https://support.hobbywingdirect.com/hc/en-us/article_attachments/29009668219155']]},
 {n:'好盈 Platinum V4',a:'ok',t:'自動精靈:保持 6~7 秒',need:'需要. 預設行程 1100~1940µs.',
  s:['油門最高,接電池,響「123」','上電 5 秒後兩聲短嗶 = 最高點接受','60A/80A/120A:3 秒內拉到最低(25A/40A 沒寫時限)','1 秒後接受,節數嗶聲,長嗶完成'],
  w:'時序和 Skywalker 不同:嗶聲比較晚,拉低時限比較短. 行程小於發射機全行程 50% 會響「B-B-B-B-B-」要重做.',c:'已查證',src:[['60A V4','https://support.hobbywingdirect.com/hc/en-us/article_attachments/17873440273683'],['80A/120A V4','https://support.hobbywingdirect.com/hc/en-us/article_attachments/17873440353811'],['25A/40A V4','https://support.hobbywingdirect.com/hc/en-us/article_attachments/17873431456787']]},
 {n:'好盈 Platinum V5',a:'man',t:'建議手動輸出',need:'需要. 預設行程 1100~1940µs.',
  s:['油門 100%,接電池,響「123」','「beep-beep」= 最高點成功','5 秒內拉到最低,等 1 秒','節數嗶聲,再一聲 = 可起飛'],w:'說明書沒寫上電後多久響 beep-beep,自動精靈的秒數推算不出來.',c:'已查證',src:[['80A V5','https://www.hobbywing.com/en/uploads/file/20240426/f2e8dad2a4854c8d5fead05690184769.pdf']]},
 {n:'T-Motor AT 系列(20A~115A)/ AT195A HV',a:'ok',t:'自動精靈:保持 3~6 秒',need:'需要. AT195A HV 預設 1100~1940µs(小型號沒寫).',
  s:['油門最高,接電池(AT195A 響「123」)','約 2 秒「Beep-Beep-」= 最高點確認','5 秒內拉到最低,等 1 秒','節數音,「Beep-Beep-」或長嗶 = 完成'],w:'AT 系列說明書:嗶嗶後再 5 秒響「56712」進程式設定.',c:'已查證',src:[['AT 系列說明書','https://img.staticdj.com/5106ba23460d7ee576357a9590362452.pdf'],['AT195A HV','https://store.tmotor.com/images/file/202308/081691475558761064.pdf']]},
 {n:'ZTW Mantis G2 / Mantis Slim G2',a:'ok',t:'自動精靈:保持 3~4 秒',need:'需要(第一次使用或換遙控器). 有節數音但馬達不轉 = 沒設行程.',
  s:['油門最高,接電池,等約 2 秒','「滴-滴」兩聲短音 = 最高點確認','馬上拉到最低(中文版寫 3 秒內)','N 聲短音 = 鋰電節數','「Beep——Beep」= 完成'],w:'兩聲短音後繼續停最高約 3 秒會響「123」進設定模式. Gecko,舊 Mantis 步驟相似(經銷商轉載,非官方).',c:'已查證(Gecko/舊款為部分查證)',src:[['Mantis G2','https://cdn.shopify.com/s/files/1/0729/3737/4010/files/ZTW_Mantis_G2_User_Manual.pdf'],['Gecko(轉載)','https://badasspower.com/downloads/ZTW-Gecko-Series-ESC-Manual.pdf']]},
 {n:'Turnigy Plush-32',a:'man',t:'建議手動輸出',need:'需要(第一次使用). 預設行程 900~2400µs.',
  s:['油門最高,電調上電,「♪♪」= 最高點','拉到最低,「♪♪」= 最低點','再「♪♪」= 完成'],w:'說明書沒寫秒數. 上電時油門在中間會進入煞車設定,平常上電要在最低.',c:'已查證',src:[['Plush-32 說明書','https://cdn-global-hk.hobbyking.com/media/file/p/l/plush_-32_series_esc_user_manual_1__4.pdf']]},
 {n:'Turnigy Plush(舊款)',a:'ok',t:'自動精靈:保持 3~6 秒',need:'強烈建議,換遙控器要重做.',
  s:['油門最高,接電池,等約 2 秒','「Beep-Beep-」= 最高點確認','拉到最低,數聲 = 節數','長「Beep-」= 完成'],w:'「Beep-Beep-」後再 5 秒響「56712」進設定模式.',c:'部分查證',src:[['說明書','https://cdn-global-hk.hobbyking.com/media/file/379223810X777308X18.pdf']]},
 {n:'HobbyKing YEP',a:'man',t:'建議手動輸出',need:'需要(Basic-Setup).',
  s:['油門最高,接電池,持續嗶聲','不要煞車拉到最低(要煞車停在離最低約 1/5)','一高一低兩聲 = 位置記住','不要動,等下一組兩聲 = 完成'],w:'持續嗶約 20 聲後可能進進階設定. 英譯說明書文字含糊.',c:'部分查證',src:[['YEP 說明書','https://cdn-global-hk.hobbyking.com/media/file/m/a/manual_yep_series_of_esc.pdf']]},
 {n:'Spektrum Avian(Smart)',a:'man',t:'建議手動輸出',need:'支援.',
  s:['油門最高,接電池,三聲上升音','兩聲短音 = 最高點接受','5 秒內拉到最低','數聲 = 節數','一聲長音 = 完成'],w:'超過 5 秒沒拉下會進搖桿設定模式. 說明書沒寫兩聲短音出現的時間(160/200A HV 寫 5 秒後).',c:'已查證',src:[['Avian 手冊 第 7 頁','https://www.horizonhobby.com/on/demandware.static/-/Sites-horizon-master/default/Manuals/Avian-Manual-EN.pdf']]},
 {n:'E-flite Pro(舊款 40A/60A)',a:'no',t:'不需要,不要做',need:'沒有校正功能,行程固定 1.2~1.8ms(設定選單可改 1.1~1.9ms).',
  s:['油門最低上電超過 1 秒就待命,不必校正'],w:'最高油門上電等 5 秒會進設定模式,<b>不要</b>對這款做「最高上電」. 輸出 1000~2000µs 時,1000~1200 是死區,1800 以上全油門;可把本頁脈寬改成 1200/1800 對齊.',c:'已查證',src:[['60A V2','https://www.towerhobbies.com/on/demandware.static/-/Sites-horizon-master/default/dw59e97199/Manuals/EFLA1060B_Manual.pdf']]},
 {n:'Castle Phoenix Edge / Edge Lite',a:'no',t:'不走校正,不要最高上電',need:'出廠自動校正行程(Auto-Calibrate),機種 Airplane.',
  s:['油門最低接電,開機音 + 節數嗶聲','拉到最低響解鎖音即可運轉'],w:'最高油門上電會進搖桿設定模式,全油門停 6 秒會清除資料記錄. 要固定行程需用 Castle Link 軟體. 舊款 Phoenix 說明書寫每次解鎖後推全油門 4 秒學最高點(Edge 未重述).',c:'部分查證',src:[['Edge 快速入門','https://www.castlecreations.com/img/product/description/documents/edge_qsg.pdf'],['Phoenix Edge User Guide','https://www.horizonhobby.com/on/demandware.static/-/Sites-horizon-master/default/dw08fb08af/Manuals/CSE_Edge_ESC_guide.pdf']]},
 {n:'Kontronik JIVE Pro / KOLIBRI / KOSMIK',a:'man',t:'要動手,用手動輸出',need:'需要,油門行程在「模式設定」時學習. 飛機用模式 3「Motor flight」.',
  s:['油門<b>最低</b>,接電池:上升三音,節數音','JIVE Pro 拔跳線 / KOLIBRI,KOSMIK 按一下按鈕:下降三音','報模式:1 聲 = 模式 1 …','第 3 組單音(模式 3)一響完,推到最高','上升三音 + 3 聲單音 = 完成,確認音結束前不可拔電'],w:'順序和一般電變相反,而且要動手拔跳線或按按鈕,自動精靈做不到.',c:'已查證',src:[['JIVE Pro','https://kontronik.com/wp-content/uploads/2023/03/JIVE_Pro.pdf'],['KOLIBRI','https://kontronik.com/wp-content/uploads/2023/03/Anleitung_KOLIBRI.pdf']]},
 {n:'YGE LVT / HVT / Aureus',a:'man',t:'邊聽邊操作,用手動輸出',need:'需要,油門行程在模式設定時學習. 飛機選模式 5(無煞車).',
  s:['油門最高,接電池','間隔提示音響滿 20 聲進入設定,♪♪ 確認','拉到最低,輪流報模式(5 聲 = 模式 5 飛機)','聽到模式 5 時推到最高,♪♪ 確認','再拉到最低,♪♪ 確認,節數音,解鎖'],w:'要在正確的模式音出現時推油門.',c:'已查證',src:[['35/65/95 LVT','https://cdn.prod.website-files.com/6a58a0f83dddc506de2f5a78/6a79aadc5a756bafa87632cb_YGE-35-95LVT-eng.pdf']]},
 {n:'Scorpion Tribunus II / Commander V',a:'man',t:'限時拉低,用手動輸出',need:'需要. Tribunus II 預設 1.07~1.93ms,出廠直升機模式.',
  s:['油門最高,接電池','Tribunus II:數秒後 1 聲,3 秒內拉到最低 → 2 聲 + 開機音 = 完成','Commander V:數秒後 2 聲,10 秒內拉到最低 → 4 聲 = 完成並解鎖'],w:'Commander V 最高油門停超過 10 秒會回出廠設定. Tribunus II 停太久可能切換模式,聽到第一聲就拉低. Tribunus II 也可用 Sproto 軟體直接輸入 1.00/2.00ms.',c:'已查證',src:[['Tribunus II','https://www.scorpionsystem.com/files/download/Tribunus%20II%20Instructions%20-%20220922.pdf'],['Commander V OPTO','https://www.scorpionsystem.com/files/Commander%20V%20OPTO%20Series%20V6-v1_1%207in1(1).pdf']]},
 {n:'BLHeli_32',a:'ok',t:'PWM:自動精靈保持 5~6 秒;DShot 不需要',need:'建議. 預設行程 1040~1960µs. 用 DShot 時校正停用.',
  s:['油門最高上電:3 聲開機音,偵測到訊號一聲低音','油門保持中點以上,單聲嗶持續 3 秒後上升音階 = 最高值已存','拉到最低,雙聲嗶持續 3 秒後下降音階 = 最低值已存'],w:'晶片越快能接受的最低 PWM 頻率越高(48MHz 約 40Hz),50Hz 不動時把 PWM 頻率調高或改 DShot.',c:'已查證',src:[['BLHeli_32 manual','https://github.com/bitdump/BLHeli/blob/master/BLHeli_32%20ARM/BLHeli_32%20manual%20ARM%20Rev32.x.pdf']]},
 {n:'BLHeli_S',a:'ok',t:'PWM:自動精靈保持 5~6 秒;DShot 不需要',need:'建議(預設 1148~1832µs,送 1000~2000 頭尾會被截). 用 DShot 時校正停用.',
  s:['油門最高上電:3 聲,偵測到訊號低音','保持中點以上 3 秒,上升音階 = 最高值已存','拉到最低保持 3 秒,下降音階 = 最低值已存'],w:'L 型(24MHz)晶片官方建議 DShot150. 「Programming by TX」關閉時不能校正.',c:'已查證(預設行程為部分查證)',src:[['BLHeli_S manual','https://github.com/bitdump/BLHeli/blob/master/BLHeli_S%20SiLabs/BLHeli_S%20manual%20SiLabs%20Rev16.x.pdf']]},
 {n:'Bluejay',a:'no',t:'只收 DShot',need:'不支援 PWM,請把輸出協定改成 DShot150 或 DShot300. DShot 不需要校正.',s:['上電後連續收到停止指令約 0.3 秒解鎖(開機解鎖時間已涵蓋)'],w:'BB1 板子不支援 DShot600(本控制器只做 150/300,不受影響).',c:'已查證(解鎖時間為部分查證)',src:[['Bluejay FAQ','https://github.com/bird-sanctuary/bluejay/wiki/FAQ']]},
 {n:'AM32',a:'ok',t:'預設可直接用',need:'預設行程 1006~2006µs,送 1000~2000µs 可直接用. DShot 不需要校正.',
  s:['(要校正時)上電後油門保持高位到提示音','繼續保持最高到響一聲','拉到 1250µs 以下,響「設定已變更」音'],w:'校正步驟只見於原始碼,官方文件沒寫;每次上電只能校正一次.',c:'預設值已查證,步驟為部分查證',src:[['AM32 GitHub','https://github.com/am32-firmware/AM32']]}
];
function buildBrands(){
 const box=$('brandList');if(!box||box.childElementCount)return;
 box.innerHTML=ESC_BRANDS.map(b=>`<details class="brand"><summary>${b.n}<span class="tag ${b.a}">${b.t}</span></summary><div class="bd">`+
  `<div class="kv"><b>需要校正?</b>${b.need}</div><ol class="steps">${b.s.map(x=>`<li>${x}</li>`).join('')}</ol>`+
  (b.w?`<div class="kv"><b>注意:</b>${b.w}</div>`:'')+
  `<div class="conf">查證:${b.c} · 出處:${b.src.map(([l,u])=>`<a href="${u}" target="_blank" rel="noopener">${l}</a>`).join(' · ')}</div></div></details>`).join('');
}
buildBrands();
document.addEventListener('click',e=>{
 if(!e.target||e.target.id!=='btnProtoReboot')return;
 manLock(false);
 post('/api/reboot').then(r=>toast(CODES[r.code]||r.code,!r.ok)).catch(()=>toast('連線失敗,請再試一次.',true));
});

// --- 共用小工具 ---
const PHASE_NAMES=['直接跳','直接跳(有過渡)','平均分攤在第一段'];
function axisVec(i){const v=[0,0,0];v[Math.floor(i/2)]=i%2?-1:1;return v}
function cross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]}
function axisName(v){const i=v.findIndex(x=>x!==0);return i<0?'--':'晶片 '+(v[i]>0?'+':'−')+'XYZ'[i]}

// --- 安裝方位圖(側視/後視) ---
// 機身座標:側視機頭在左(-x),機背朝上(-y);後視左翼在左. 圖跟著感測器轉,箭頭標目前選的晶片軸.
// 文字不跟著轉(算出箭頭端點位置再放文字),倒飛時字才不會上下顛倒.
const INS_COL={nose:'#dc2626',up:'#16a34a',left:'#d97706'};
function insArrow(x1,y1,x2,y2,col,label){
 const a=Math.atan2(y2-y1,x2-x1),c=Math.cos(a),s=Math.sin(a),h=11,w=6;
 const bx=x2-h*c,by=y2-h*s;
 // 接近水平的箭頭把字放在箭頭上方(放在尖端外側會超出圖框);其他放在尖端外側
 const flat=Math.abs(c)>0.7,lx=flat?x2-18*c:x2+16*c,ly=flat?y2-14:y2+16*s+5;
 const anchor=flat?'middle':c>0.35?'start':c<-0.35?'end':'middle';
 return `<line x1="${x1}" y1="${y1}" x2="${bx}" y2="${by}" stroke="${col}" stroke-width="3.5" stroke-linecap="round"/>`+
  `<path d="M${x2},${y2} L${bx+w*s},${by-w*c} L${bx-w*s},${by+w*c} Z" fill="${col}"/>`+
  `<text x="${lx}" y="${ly}" text-anchor="${anchor}" class="ins-t" fill="${col}">${label}</text>`;
}
// 垂直紙面的軸:⊙ 朝向你,⊗ 遠離你
function insOut(x,y,toward,col,label,dx,dy){
 return `<circle cx="${x}" cy="${y}" r="9" fill="var(--bg)" stroke="${col}" stroke-width="3"/>`+
  (toward?`<circle cx="${x}" cy="${y}" r="3.2" fill="${col}"/>`:`<path d="M${x-5},${y-5} L${x+5},${y+5} M${x+5},${y-5} L${x-5},${y+5}" stroke="${col}" stroke-width="2.6"/>`)+
  `<text x="${x+dx}" y="${y+dy}" text-anchor="${dx<0?'end':'start'}" class="ins-t" fill="${col}">${label}</text>`;
}
function instDraw(s){
 const sv=$('instSide'),rv=$('instRear');if(!sv||!VALS||$('inst').hidden)return;
 const sh=VALS.shared,nose=AXES[sh.noseAxis],up=AXES[sh.upAxis],left=axisName(cross(axisVec(sh.upAxis),axisVec(sh.noseAxis)));
 const ok=!!(s&&s.imu===1),P=ok?s.p:0,R=ok?s.r:0,inv=ok&&inverted;
 // 側視:和監看頁同一套倒飛畫法(機頭換邊且上下顛倒);左翼翻到另一面變成遠離你
 const k=inv?-1:1,ang=(inv?-P:P)*Math.PI/180,ca=Math.cos(ang),sa=Math.sin(ang);
 const T=(x,y)=>[+(x*k*ca-y*k*sa).toFixed(1),+(x*k*sa+y*k*ca).toFixed(1)];
 const ch=T(-8,0),nt=T(-78,0),ut=T(-8,-58);
 let h=`<line x1="-160" y1="0" x2="160" y2="0" class="ins-hz"/>`+
  `<g transform="rotate(${(inv?-P:P).toFixed(1)}) scale(${k},${k})" class="ins-body">`+
  `<path d="M-92,0 Q-90,-9 -72,-10 L58,-5 L96,-3 L96,3 L58,5 L-72,10 Q-90,9 -92,0 Z"/><path d="M68,-4 L90,-30 L100,-30 L97,-3 Z"/>`+
  `<rect x="-97" y="-28" width="3" height="56"/><line x1="-44" y1="9" x2="-54" y2="30" stroke="var(--plane)" stroke-width="3"/><circle cx="-54" cy="32" r="6"/></g>`+
  `<g transform="translate(${ch[0]},${ch[1]}) rotate(${(inv?-P:P).toFixed(1)})"><rect x="-13" y="-8" width="26" height="16" rx="2" class="ins-chip"/></g>`+
  insArrow(ch[0],ch[1],nt[0],nt[1],INS_COL.nose,'機頭 '+nose)+insArrow(ch[0],ch[1],ut[0],ut[1],INS_COL.up,'機背 '+up)+
  insOut(ch[0],ch[1],!inv,INS_COL.left,'左翼 '+left,14,30)+
  `<text x="152" y="-82" text-anchor="end" class="ins-s">機頭朝上 = 正角度</text>`+
  `<text x="152" y="92" text-anchor="end" class="ins-v">${ok?'機頭 '+sgn(P,1)+'°':'感測器未就緒'}</text>`;
 sv.innerHTML=h;
 // 後視:左翼在左,機頭朝紙面裡面;左翼抬起為正滾轉(畫面上是順時針)
 // SVG 的 y 朝下:左翼(x<0)抬起要 y'=x·sinθ<0,所以轉 +R(r15 初版寫成 −R,左翼抬起圖卻往下,GG 以為 Y 軸反了)
 const rb=R*Math.PI/180,cb=Math.cos(rb),sb=Math.sin(rb),Q=(x,y)=>[+(x*cb-y*sb).toFixed(1),+(x*sb+y*cb).toFixed(1)];
 const lt=Q(-72,0),rt=Q(0,-60);
 h=`<line x1="-160" y1="0" x2="160" y2="0" class="ins-hz"/>`+
  `<g transform="rotate(${R.toFixed(1)})" class="ins-body">`+
  `<rect x="-128" y="-3" width="256" height="6" rx="3"/><circle r="15"/><rect x="-2.5" y="-50" width="5" height="36"/><rect x="-42" y="-38" width="84" height="4" rx="2"/>`+
  `<line x1="-8" y1="12" x2="-30" y2="40" stroke="var(--plane)" stroke-width="3"/><line x1="8" y1="12" x2="30" y2="40" stroke="var(--plane)" stroke-width="3"/>`+
  `<circle cx="-30" cy="43" r="6"/><circle cx="30" cy="43" r="6"/>`+
  `<line x1="-128" y1="-1" x2="-160" y2="-6" stroke="var(--plane)" stroke-width="1.2"/><line x1="-128" y1="1" x2="-160" y2="6" stroke="var(--plane)" stroke-width="1.2"/></g>`+
  `<g transform="rotate(${R.toFixed(1)})"><rect x="-13" y="-8" width="26" height="16" rx="2" class="ins-chip"/></g>`+
  insArrow(0,0,lt[0],lt[1],INS_COL.left,'左翼 '+left)+insArrow(0,0,rt[0],rt[1],INS_COL.up,'機背 '+up)+
  insOut(0,0,false,INS_COL.nose,'機頭 '+nose+'(朝裡)',16,34)+
  `<text x="-152" y="-82" class="ins-s">← 引線,往操控手</text>`+
  `<text x="152" y="-82" text-anchor="end" class="ins-s">左翼抬起 = 正</text>`+
  `<text x="152" y="92" text-anchor="end" class="ins-v">${ok?'滾轉 '+sgn(R,0)+'°':''}</text>`;
 rv.innerHTML=h;
 const isDef=sh.noseAxis===0&&sh.upAxis===4&&Math.abs(sh.pitchTrim)<0.05;
 $('instDefState').innerHTML=isDef?'<span style="color:var(--ok)">出廠預設</span>':'<span style="color:var(--warn)">和出廠預設不同</span>';
}

// --- 紀錄圖表 ---
const LOGK=['pitch','thr','acc','vib','spike','push','state','flags'];
const LOG={next:0,ms:100};LOGK.forEach(k=>LOG[k]=[]);
let logWinS=180,logPaused=false,logEnd=0,logCursor=-1,logBusy=false;
function logReset(start){LOGK.forEach(k=>LOG[k]=[]);LOG.next=start}
async function logFetch(force){
 if(logBusy||(logPaused&&!force))return;logBusy=true;
 try{
  const c=new AbortController(),tm=setTimeout(()=>c.abort(),8000);
  const r=await fetch('/api/log?since='+LOG.next,{signal:c.signal,cache:'no-store'});
  const buf=await r.arrayBuffer();clearTimeout(tm);
  const dv=new DataView(buf),start=dv.getUint32(0,true),count=dv.getUint32(4,true),size=dv.getUint16(10,true);
  LOG.ms=dv.getUint16(8,true);
  if(start!==LOG.next)logReset(start);   // 板子重開過或舊資料已被覆寫:整份重建
  for(let i=0;i<count&&12+(i+1)*size<=buf.byteLength;i++){const o=12+i*size;
   LOG.pitch.push(dv.getInt8(o));LOG.thr.push(dv.getUint8(o+1));LOG.acc.push(dv.getUint8(o+2)/10);
   LOG.vib.push(dv.getUint8(o+3)*0.02);LOG.spike.push(dv.getUint8(o+4)/10);LOG.push.push(dv.getInt8(o+5)/10);
   LOG.state.push(dv.getUint8(o+6));LOG.flags.push(dv.getUint8(o+7))}
  LOG.next=start+count;
  const extra=LOG.pitch.length-6000;if(extra>0){LOGK.forEach(k=>LOG[k].splice(0,extra));if(logPaused)logEnd=Math.max(0,logEnd-extra)}
  drawLog();
 }catch(e){}finally{logBusy=false}
}
function fmtT(s){const m=Math.floor(Math.abs(s)/60),ss=Math.round(Math.abs(s)%60);return (s<0?'−':'')+m+':'+String(ss).padStart(2,'0')}
function drawLog(){
 const cv=$('logCanvas');if($('log').hidden)return;
 const dpr=window.devicePixelRatio||1,W=cv.clientWidth,H=cv.clientHeight;if(!W)return;
 cv.width=Math.round(W*dpr);cv.height=Math.round(H*dpr);
 const g=cv.getContext('2d');g.setTransform(dpr,0,0,dpr,0,0);g.clearRect(0,0,W,H);
 const css=getComputedStyle(document.documentElement),cv_=n=>css.getPropertyValue(n).trim();
 const INK=cv_('--ink'),MUTE=cv_('--mute'),LINE=cv_('--line');
 const N=LOG.pitch.length,winN=Math.max(10,Math.round(logWinS*1000/LOG.ms));
 const end=logPaused?Math.min(logEnd,N):N,begin=Math.max(0,end-winN);
 const Lm=38,Rm=38,plotW=W-Lm-Rm,xOf=i=>Lm+(i-(end-winN))/(winN-1)*plotW;
 const sh=VALS?VALS.shared:{gestureG:2,touchdownG:3,earlyLandVib:0.8};
 const range=(arr)=>{let m=0;for(let i=begin;i<end;i++)if(arr[i]>m)m=arr[i];return m};
 const gMax=Math.max(4,Math.ceil(Math.max(range(LOG.acc),range(LOG.spike),sh.gestureG,sh.touchdownG)+0.5));
 const vMax=Math.max(1.5,Math.ceil(Math.max(range(LOG.vib),sh.earlyLandVib*1.3)*2)/2);
 const top0=4,axisH=18,gap=10,ph=(H-top0-axisH-gap*2)/3;
 const panels=[{y:top0,t:'機頭角度(紅,°)/ 油門(橘,%)'},{y:top0+ph+gap,t:`G 力:總 G(灰)/ 短尖峰(紅)/ 手勢推力(綠),0~${gMax} g`},{y:top0+2*(ph+gap),t:`Z 軸抖動(棕),0~${vMax} g;綠底=正飛水平,橘條=抖動持續達標`}];
 g.font='11px system-ui,sans-serif';g.lineJoin='round';
 for(const p of panels){g.strokeStyle=LINE;g.lineWidth=1;g.strokeRect(Lm+.5,p.y+.5,plotW,ph);g.fillStyle=MUTE;g.fillText(p.t,Lm+4,p.y+12)}
 const yOf=(p,v,lo,hi)=>p.y+ph-(Math.min(hi,Math.max(lo,v))-lo)/(hi-lo)*ph;
 const hline=(p,v,lo,hi,color,label,right)=>{const y=yOf(p,v,lo,hi);g.save();g.setLineDash([5,4]);g.strokeStyle=color;g.beginPath();g.moveTo(Lm,y);g.lineTo(Lm+plotW,y);g.stroke();g.restore();
  if(label){g.fillStyle=color;g.textAlign=right?'left':'right';g.fillText(label,right?Lm+plotW+3:Lm-3,y+4);g.textAlign='left'}};
 const series=(p,arr,lo,hi,color,w)=>{g.strokeStyle=color;g.lineWidth=w||1.5;g.beginPath();let first=true;
  for(let i=begin;i<end;i++){const x=xOf(i),y=yOf(p,arr[i],lo,hi);if(first){g.moveTo(x,y);first=false}else g.lineTo(x,y)}g.stroke()};
 // 面板 1:角度與油門
 const p1=panels[0];
 for(const d of [-90,-45,0,45,90]){const y=yOf(p1,d,-90,90);g.strokeStyle=LINE;g.beginPath();g.moveTo(Lm,y);g.lineTo(Lm+plotW,y);g.stroke();g.fillStyle=MUTE;g.textAlign='right';g.fillText(d,Lm-3,y+4);g.textAlign='left'}
 for(const v of [0,50,100]){g.fillStyle='#d97706';g.fillText(v+'%',Lm+plotW+3,yOf(p1,v,0,100)+4)}
 series(p1,LOG.thr,0,100,'#f59e0b',1.5);series(p1,LOG.pitch,-90,90,'#dc2626',1.8);
 // 面板 2:G 力
 const p2=panels[1];
 for(let v=0;v<=gMax;v+=gMax>8?4:2){g.fillStyle=MUTE;g.textAlign='right';g.fillText(v,Lm-3,yOf(p2,v,0,gMax)+4);g.textAlign='left'}
 series(p2,LOG.acc,0,gMax,'#64748b',1.2);
 g.strokeStyle='#ef4444';g.lineWidth=2;
 for(let i=begin;i<end;i++)if(LOG.spike[i]>0){const x=xOf(i);g.beginPath();g.moveTo(x,p2.y+ph);g.lineTo(x,yOf(p2,LOG.spike[i],0,gMax));g.stroke()}
 series(p2,LOG.push.map(v=>Math.max(0,v)),0,gMax,'#22c55e',1.5);
 hline(p2,sh.gestureG,0,gMax,'#16a34a','手勢',true);hline(p2,sh.touchdownG,0,gMax,'#dc2626','觸地',true);
 // 面板 3:Z 抖動
 const p3=panels[2];
 // 連續的區段合併成一塊畫:逐筆畫半透明方塊會互相重疊,顏色疊成實心
 const band=(bit,color,y,h)=>{g.fillStyle=color;let s=-1;
  for(let i=begin;i<=end;i++){const on=i<end&&(LOG.flags[i]&bit);
   if(on&&s<0)s=i;else if(!on&&s>=0){const x0=xOf(s),x1=xOf(i-1)+plotW/winN;g.fillRect(x0,y,Math.max(1,x1-x0),h);s=-1}}};
 band(1,'rgba(34,197,94,.14)',p3.y,ph);band(2,'rgba(245,158,11,.9)',p3.y+1,5);
 for(let v=0;v<=vMax;v+=vMax>3?1:0.5){g.fillStyle=MUTE;g.textAlign='right';g.fillText(v,Lm-3,yOf(p3,v,0,vMax)+4);g.textAlign='left'}
 series(p3,LOG.vib,0,vMax,'#a855f7',1.6);
 hline(p3,sh.earlyLandVib,0,vMax,'#d97706','門檻',true);
 // 時間軸
 const step=logWinS<=60?10:(logWinS<=180?30:60),yAxis=H-axisH+12;
 g.fillStyle=MUTE;g.textAlign='center';
 for(let s=0;s<=logWinS;s+=step){const i=end-1-Math.round(s*1000/LOG.ms);const x=xOf(i);if(x<Lm-1)break;g.fillText(s?fmtT(-s):'最新',x,yAxis)}
 g.textAlign='left';
 // 游標
 if(logCursor>=begin&&logCursor<end){const x=xOf(logCursor),i=logCursor;
  g.strokeStyle=INK;g.lineWidth=1;g.beginPath();g.moveTo(x,top0);g.lineTo(x,H-axisH);g.stroke();
  const ago=(N-1-i)*LOG.ms/1000;
  $('logCursor').innerHTML=`<b>${fmtT(-ago)}</b> 角度 ${LOG.pitch[i]}°,油門 ${LOG.thr[i]}%,總 G ${LOG.acc[i].toFixed(1)},短尖峰 ${LOG.spike[i]?LOG.spike[i].toFixed(1)+' g':'無'},推力 ${Math.max(0,LOG.push[i]).toFixed(1)} g,抖動 ${LOG.vib[i].toFixed(2)} g${LOG.flags[i]&1?'(正飛水平)':''}${LOG.flags[i]&2?',抖動持續達標':''}`;
 }else $('logCursor').textContent='點或拖曳圖表查看某一時刻的數值.';
 // 統計(目前視窗)
 let aM=0,sM=0,vM=0,vL=0,pM=0;
 for(let i=begin;i<end;i++){aM=Math.max(aM,LOG.acc[i]);sM=Math.max(sM,LOG.spike[i]);vM=Math.max(vM,LOG.vib[i]);if(LOG.flags[i]&1)vL=Math.max(vL,LOG.vib[i]);pM=Math.max(pM,LOG.push[i])}
 const tile=(k,v)=>`<div class="stat"><div class="k">${k}</div><div class="v">${v}</div></div>`;
 $('logStats').innerHTML=tile('最大總 G',aM.toFixed(1)+' g')+tile('最大短尖峰',sM?sM.toFixed(1)+' g':'無')+tile('最大手勢推力',Math.max(0,pM).toFixed(1)+' g')+tile('最大 Z 抖動',vM.toFixed(2)+' g')+tile('水平時最大抖動',vL.toFixed(2)+' g');
 $('logInfo').textContent=`板上共 ${fmtT(N*LOG.ms/1000).replace('−','')} 紀錄`+(logPaused?',已暫停':'');
}
(function(){
 const cv=$('logCanvas');
 const pick=e=>{const r=cv.getBoundingClientRect(),N=LOG.pitch.length,winN=Math.max(10,Math.round(logWinS*1000/LOG.ms)),end=logPaused?Math.min(logEnd,N):N;
  const plotW=r.width-76,i=Math.round((e.clientX-r.left-38)/plotW*(winN-1)+(end-winN));logCursor=Math.min(end-1,Math.max(Math.max(0,end-winN),i));drawLog()};
 cv.addEventListener('pointerdown',e=>{pick(e);cv.setPointerCapture(e.pointerId)});
 cv.addEventListener('pointermove',e=>{if(e.buttons)pick(e)});
 document.querySelectorAll('#logWin button').forEach(b=>b.onclick=()=>{logWinS=Number(b.dataset.s);
  document.querySelectorAll('#logWin button').forEach(x=>x.classList.toggle('on',x===b));drawLog()});
 $('btnLogPause').onclick=()=>{logPaused=!logPaused;logEnd=LOG.pitch.length;$('btnLogPause').textContent=logPaused?'繼續更新':'暫停更新';if(!logPaused)logFetch(true);else drawLog()};
 window.addEventListener('resize',drawLog);
 setInterval(()=>{if(pane==='log')logFetch(false)},1000);
})();

// --- 風格操作 ---
$('btnSelect').onclick=async()=>{try{const r=await post('/api/select',{p:editP});toast(CODES[r.code]||r.code,!r.ok)}catch(e){}loadVals()};
$('btnName').onclick=async()=>{try{const r=await post('/api/name',{p:editP,name:$('fName').value});if(!r.ok)toast(CODES[r.code]||r.code,true)}catch(e){}loadVals()};
$('btnCopy').onclick=async()=>{const to=$('copyTo').value;if(to==='')return;
 try{const r=await post('/api/copy',{from:editP,to:to});toast(CODES[r.code]||r.code,!r.ok)}catch(e){}loadVals()};
function confirmTwice(btn,label,action){
 let armed=false,timer=0;
 btn.onclick=()=>{if(!armed){armed=true;btn.textContent='再按一次確認';timer=setTimeout(()=>{armed=false;btn.textContent=label},3000);return}
  clearTimeout(timer);armed=false;btn.textContent=label;action()};
}
confirmTwice($('btnProfDef'),'這組回預設',async()=>{try{const r=await post('/api/defaults',{p:editP});toast(CODES[r.code]||r.code,!r.ok)}catch(e){}loadVals()});
confirmTwice($('btnSharedDef'),'共用設定回預設',async()=>{try{const r=await post('/api/defaults',{p:'s'});toast(CODES[r.code]||r.code,!r.ok)}catch(e){}loadVals()});
$('btnSave').onclick=async()=>{try{const r=await post('/api/save');toast(CODES[r.code]||r.code,!r.ok)}catch(e){toast('連線失敗.',true)}loadVals()};
$('btnRevert').onclick=async()=>{try{const r=await post('/api/revert');toast(CODES[r.code]||r.code,!r.ok)}catch(e){}loadVals()};

// --- 設定備份碼(GG 2026-09-14,設計見 docs/設定備份碼設計_2026-09-14.md) ---
// 有未儲存變更時整張卡不能用. 貼上當下就送板子檢查;不是 LP 開頭或檢查碼錯就提示並清空.
const BK_NAMES={noseAxis:'朝機頭的軸',upAxis:'朝機背的軸',noseRight:'圖示機頭方向',escProtocol:'輸出協定',gestureEnable:'啟動手勢',
 earlyLand:'觸地提早降落',escRpm:'轉速回傳',gearEnable:'機輪收腳',gearReverse:'舵機反轉',buzzerLow:'蜂鳴器類型',armSwitchOff:'停用安全開關',phaseMode:'換段方式',landingMode:'減力方式',landingBuzz:'降落蜂鳴器提醒',upN:'補速曲線點數',dnN:'減速曲線點數'};
const BK_SHARED_ERR=['axis','escrange','pwmhz','twistdeg','gearrange','wagdeg'];
function bkLabel(item){
 if(item==='act')return '飛行使用的風格';
 const i=item.indexOf(':'),sc=item.slice(0,i),key=item.slice(i+1);
 const m=/^(up|dn)(\d)([ap])$/.exec(key);
 const name=(L[key]||[])[0]||BK_NAMES[key]||(m?`${m[1]==='up'?'補速':'減速'}曲線第 ${m[2]} 點${m[3]==='a'?'角度':'補償'}`:key);
 return sc==='s'?name:`第 ${Number(sc)+1} 組風格的${name}`;
}
function bkShow(ok,text,id){const e=$(id||'bkMsg');e.className='msg '+(ok?'ok':'bad');e.textContent=text}
// 選擇(GG 2026-09-15:備份獨立分頁,全部可選):風格 bit i = 第 i 組;分區 bit 與韌體 BACKUP_SEC_* 相同.
// 預設只選「測試」組;只記在這個網頁,重新整理回預設
const BK_ALL=63,BK_SEC_SHARED=7;
const BK_SECS=[
 {bit:1,t:'起飛降落與安全',pg:'設定頁',d:'啟動手勢,安全開關,起飛倒數秒數,外力介入,觸地提早降落,降落觸地判斷,撞擊斷電.'},
 {bit:2,t:'安裝',pg:'安裝頁',d:'感測器方位,角度修正,線長與單圈秒數,機輪收腳,蜂鳴器.',ad:'每台飛機裝法不同,分享給別人通常不要勾.',ap:'每台飛機裝法不同,別人的安裝設定通常不要套用.'},
 {bit:4,t:'電變',pg:'電變頁',d:'輸出協定,PWM 頻率,油門 0% / 100% 脈寬,校正保持秒數,轉速回傳,馬達極數.',ad:'電變不同通常不要勾.',ap:'電變不同通常不要套用.'},
 {bit:8,t:'WiFi',pg:'系統頁',d:'家用 WiFi 名稱與密碼,熱點名稱與密碼,裝置名稱,等待秒數,一律用熱點,發射功率.',w:'⚠ 含密碼,不要傳給別人. 套用後要重新開機才生效.',
  wp:'⚠ 會換成碼裡的 WiFi 與密碼,通常不要套用. 套用當下就存起來,重新開機才生效.'}
];
let bkSelMask=1<<PROFILE_TEST_INDEX,bkSecMask=0;
// 套用前的取消勾選(GG 2026-09-15:對方多複製了不要的項目):檢查通過後列出碼裡有的,預設全部套用
let bkPick=null;   // {text,mask,sec,names,selMask,selSec}
function bkMaskNames(mask,names){const out=[];for(let i=0;i<6;i++)if(mask>>i&1)out.push(names&&names[i]?names[i]:i===PROFILE_TEST_INDEX?'測試':(VALS?VALS.names[i]:`第 ${i+1} 組`));return out.join(',')}
// 內容說明:「風格 測試,A;安裝,WiFi」
function bkDescribe(mask,sec,names){
 const parts=[];
 if(mask)parts.push(mask===BK_ALL?'六組風格':'風格 '+bkMaskNames(mask,names));
 for(const s of BK_SECS)if(sec&s.bit)parts.push(s.t);
 return parts.join(',')||'(沒有內容)';
}
// 其他設定的小方塊:名稱(點一下勾選/取消)+ ⓘ(點一下展開說明,不影響勾選). pick = 套用時的取消勾選
function bkSecHtml(s,on,pick){
 const hint=`在${s.pg}. 包含:${s.d}`+(pick?(s.ap?' '+s.ap:'')+(s.wp?' '+s.wp:''):(s.ad?' '+s.ad:'')+(s.w?' '+s.w:''));
 return `<div class="bks${pick?' pick':''}${on?' on':''}" data-b="${s.bit}"><button class="bkst" type="button"><span class="mk"></span>${s.t}${s.w?'<span class="bkwm">⚠</span>':''}</button>`+
  `<button class="ib" type="button" title="說明">ⓘ</button><div class="bkhint">${hint}</div></div>`;
}
function bkWireSecs(box,onToggle){
 box.querySelectorAll('.bks').forEach(el=>{el.querySelector('.bkst').onclick=()=>onToggle(Number(el.dataset.b));el.querySelector('.ib').onclick=()=>el.classList.toggle('showhint')});
}
for(const id of ['bkProfBox','bkPickProfBox']){const b=$(id);b.querySelector('.ib').onclick=()=>b.classList.toggle('showhint')}
function bkSelChanged(){$('bkOut').hidden=true;$('bkMakeText').textContent='';$('bkMakeMsg').textContent='';bkRender()}
function bkRender(){
 const dirty=!VALS||valsDirty(),lock=!!(STATUS&&STATUS.lock);
 $('bkDirty').hidden=!VALS||!dirty;
 if(VALS){
  const sig=VALS.names.join('|')+'#'+bkSelMask;
  if($('bkSel').dataset.sig!==sig){$('bkSel').dataset.sig=sig;
   $('bkSel').innerHTML=VALS.names.map((n,i)=>`<button data-i="${i}" class="${bkSelMask>>i&1?'on':''}">${esc(n)}</button>`).join('');
   $('bkSel').querySelectorAll('button').forEach(b=>b.onclick=()=>{bkSelMask^=1<<Number(b.dataset.i);bkSelChanged()})}
 }
 const box=$('bkSecs'),ssig='#'+bkSecMask;
 if(box.dataset.sig!==ssig){box.dataset.sig=ssig;
  box.innerHTML=BK_SECS.map(s=>bkSecHtml(s,bkSecMask&s.bit,false)).join('');
  bkWireSecs(box,bit=>{bkSecMask^=bit;bkSelChanged()})}
 const none=!bkSelMask&&!bkSecMask;
 $('btnBkMake').disabled=dirty||none;
 if(none)$('bkMakeText').textContent='請至少勾選一項';
 $('bkIn').disabled=dirty;
 $('btnBkApply').disabled=dirty||lock||!$('bkIn').value.trim()||!!(bkPick&&!bkPick.selMask&&!bkPick.selSec);
 if(dirty)$('bkOut').hidden=true;   // 之前產生的碼已經不是目前的設定
}
// 列出碼裡有的項目,點一下取消/恢復. 只在檢查結果回來或點選時重畫(不跟著狀態輪詢,點擊才不會被吃掉)
function bkPickRender(){
 const P=bkPick;$('bkPick').hidden=!P;if(!P)return;
 const idx=[0,1,2,3,4,5].filter(i=>P.mask>>i&1);
 $('bkPickProfBox').hidden=!idx.length;
 $('bkPickSel').innerHTML=idx.map(i=>`<button data-i="${i}" class="${P.selMask>>i&1?'on':''}">${esc(P.names[i]||(i===PROFILE_TEST_INDEX?'測試':`第 ${i+1} 組`))}</button>`).join('');
 $('bkPickSel').querySelectorAll('button').forEach(b=>b.onclick=()=>{P.selMask^=1<<Number(b.dataset.i);bkPickRender();bkRender()});
 const secs=BK_SECS.filter(s=>P.sec&s.bit);
 $('bkPickST').hidden=$('bkPickSecs').hidden=!secs.length;
 $('bkPickSecs').innerHTML=secs.map(s=>bkSecHtml(s,P.selSec&s.bit,true)).join('');
 bkWireSecs($('bkPickSecs'),bit=>{P.selSec^=bit;bkPickRender();bkRender()});
 $('bkPickNote').textContent=!P.selMask&&!P.selSec?'全部都取消了,沒有東西可以套用.':
  P.selMask===BK_ALL?'六組風格全部套用:會一併切換「飛行使用哪一組」.':P.mask?'沒有六組風格全部套用:不切換「飛行使用哪一組」.':'';
}
// http 網頁(不是 https)瀏覽器會擋剪貼簿 API,改用選取文字後 execCommand('copy')
async function bkCopy(el){
 try{if(window.isSecureContext&&navigator.clipboard){await navigator.clipboard.writeText(el.value);return true}}catch(e){}
 try{el.readOnly=false;el.focus();el.select();el.setSelectionRange(0,el.value.length);
  const ok=document.execCommand('copy');el.readOnly=true;el.blur();return ok}
 catch(e){el.readOnly=true;return false}
}
function bkResult(r,applied){
 if(r.ok){
  const mask=r.mask===undefined?BK_ALL:r.mask,sec=r.sec===undefined?BK_SEC_SHARED:r.sec,names=r.names||[];
  let t;
  if(applied){
   const am=r.amask===undefined?mask:r.amask,as=r.asec===undefined?sec:r.asec;
   const skip=bkDescribe(mask&~am,sec&~as,names);
   t=`已套用:${bkDescribe(am,as,names)}.`+((mask&~am)||(sec&~as)?` 取消沒套用:${skip}.`:'')+
    ` 沒套用的部分保持原樣,${am===BK_ALL?'已一併切換飛行使用哪一組':'沒有切換飛行使用的風格'}.`;
   if(r.wifisaved)t+=' WiFi 設定已經存起來,重新開機後生效;重開後 3 分鐘內要按上方「保持」,沒按會自動改回原本的 WiFi.';
   if(am||as&BK_SEC_SHARED)t+=' 請逐頁檢查設定,尤其感測器方位,角度修正,電變脈寬與收輪行程,確認後按上方的儲存;不要就按放棄.';
  }else{
   t=`備份碼完整,裡面有:${bkDescribe(mask,sec,names)}. 下面點一下可以取消不要的項目,再按「套用」.`;
   bkPick={text:$('bkIn').value,mask,sec,names,selMask:mask,selSec:sec};
   bkPickRender();bkRender();
  }
  if(r.newer)t+=' 這個備份碼來自較新的韌體,這版沒有的功能已略過.';
  if(r.clamp&&r.clamp.length)t+=' 以下超出這版的可調範圍,已調到範圍內:'+r.clamp.map(bkLabel).join(',')+'.';
  bkShow(true,t);
  if(applied)loadVals();
  return;
 }
 const clear=r.code==='bkprefix'||r.code==='bkcrc';
 let t=CODES[r.code]||r.code;
 if(r.scope>=0)t=`第 ${r.scope+1} 組風格:`+t;else if(r.scope===-2)t='WiFi 設定:'+t;else if(BK_SHARED_ERR.includes(r.code))t='共用設定:'+t;
 if(clear){$('bkIn').value='';bkLastLen=0}
 if(!applied){bkPick=null;bkPickRender()}
 bkShow(false,t);bkRender();
}
let bkLastLen=0;
$('btnBkMake').onclick=async()=>{
 try{const r=await poll(`/api/backup?sel=${bkSelMask}&sec=${bkSecMask}`);
  if(!r.ok){bkShow(false,CODES[r.code]||r.code,'bkMakeMsg');return}
  const o=$('bkOut');o.value=r.text;o.hidden=false;
  const ok=await bkCopy(o);
  $('bkMakeText').textContent=`${r.text.length} 字`;
  bkShow(ok,(ok?'已複製,可以貼到 LINE 或記事本保存.':'這支手機不能自動複製:請長按下面的備份碼,全選後複製.')+` 內容:${bkDescribe(bkSelMask,bkSecMask)}.`+
   (bkSecMask&8?' ⚠ 這個碼含 WiFi 密碼,不要傳給別人.':''),'bkMakeMsg');
 }catch(e){bkShow(false,'連線失敗,請再試一次.','bkMakeMsg')}
};
$('bkIn').addEventListener('input',()=>{
 const v=$('bkIn').value,jump=v.length-bkLastLen;bkLastLen=v.length;
 if(bkPick&&bkPick.text!==v){bkPick=null;bkPickRender()}   // 內容改了,之前的勾選不算數
 bkRender();
 if(!v.trim()){$('bkMsg').textContent='';return}
 // 一次多出很多字 = 貼上(含輸入法的剪貼簿建議),馬上檢查;手打的等按套用時由板子檢查
 if(jump>=10)post('/api/backup/check',{text:v}).then(r=>{if($('bkIn').value===v)bkResult(r,false)}).catch(()=>bkShow(false,'連線失敗,請再試一次.'));
});
$('btnBkApply').onclick=async()=>{
 const v=$('bkIn').value,d={text:v};
 if(bkPick&&bkPick.text===v){d.sel=bkPick.selMask;d.sec=bkPick.selSec}   // 使用者取消的項目不套用
 try{const r=await post('/api/backup/apply',d);bkResult(r,true)}catch(e){bkShow(false,'連線失敗,請再試一次.')}
};
$('btnBkClear').onclick=()=>{$('bkIn').value='';bkLastLen=0;$('bkMsg').textContent='';bkPick=null;bkPickRender();bkRender()};
$('bkSelAll').onclick=e=>{e.preventDefault();bkSelMask=BK_ALL;bkSecMask=15;bkSelChanged()};
$('bkSelTest').onclick=e=>{e.preventDefault();bkSelMask=1<<PROFILE_TEST_INDEX;bkSecMask=0;bkSelChanged()};
$('bkSelNone').onclick=e=>{e.preventDefault();bkSelMask=0;bkSecMask=0;bkSelChanged()};

// --- 系統頁 ---
async function loadWifi(){
 try{const w=await poll('/api/wifi');
  $('fSsid').value=w.ssid;$('fPw').value=w.pw;$('fHost').value=w.host;$('fTmo').value=w.tmo;
  $('fTmo').min=w.tmomin;$('fTmo').max=w.tmomax;$('fForce').checked=!!w.forceap;
  $('fTxp').min=w.txmin;$('fTxp').max=w.txmax;$('fTxp').value=w.txp;txpShow();
  $('apName').textContent=w.apnow;$('netHost').textContent=w.host+'.local';$('build').textContent=w.build;
  $('apPrefix').textContent=w.apprefix;$('fApSfx').value=w.apsfx;AP_SFX_MAX=w.apsfxmax;apPreview();
  $('fApPw').value=w.appw||'';WIFI_APPW=w.appw||'';
 }catch(e){}
}
let AP_SFX_MAX=14;
function apPreview(){const v=$('fApSfx').value,n=new TextEncoder().encode(v).length,over=n>AP_SFX_MAX;
 $('apHint').className='sub'+(over?' bad':'');
 $('apHint').textContent=`→ ${$('apPrefix').textContent}${v}(後面 ${n}/${AP_SFX_MAX}${over?',太長':''})`}
$('fApSfx').oninput=apPreview;
$('btnPwShow').onclick=()=>{const f=$('fPw');f.type=f.type==='password'?'text':'password';$('btnPwShow').textContent=f.type==='password'?'顯示':'隱藏'};
$('btnApPwShow').onclick=()=>{const f=$('fApPw');f.type=f.type==='password'?'text':'password';$('btnApPwShow').textContent=f.type==='password'?'顯示':'隱藏'};
let WIFI_APPW='';   // 板上目前存的熱點密碼(儲存時比對有沒有改)
// 發射功率超過 7 dBm:數值與拉桿下的警告變紅(GG 2026-09-16)
function txpShow(){const v=+$('fTxp').value,hi=v>7;$('txpVal').textContent=v+' dBm';
 $('txpVal').className=hi?'txphi':'';$('txpWarn').className='sub'+(hi?' txphi':'')}
$('fTxp').oninput=txpShow;
$('fTxp').onchange=()=>post('/api/txpower',{txp:$('fTxp').value}).then(r=>{if(!r.ok){toast(CODES[r.code]||r.code,true);loadWifi()}}).catch(()=>{});
$('btnWifiSave').onclick=async()=>{
 try{const r=await post('/api/wifi',{ssid:$('fSsid').value,pw:$('fPw').value,host:$('fHost').value.trim(),
  tmo:$('fTmo').value,forceap:$('fForce').checked?1:0,txp:$('fTxp').value,apsfx:$('fApSfx').value,appw:$('fApPw').value});
  const pwChanged=$('fApPw').value!==WIFI_APPW;
  msg('wifiMsg',r.ok,r.ok?'WiFi 設定已儲存,重新開機後生效. 重開後連上網頁要按上方的「保持」,3 分鐘內沒按會自動改回上一次的設定. 熱點名稱改了的話,手機要重新連新的名稱.'+
   (pwChanged?` 熱點密碼改成「${$('fApPw').value}」,請記下來;手機要先刪除(忘記)舊的熱點再用新密碼連.`:''):r.code);if(r.ok)loadWifi()}
 catch(e){msg('wifiMsg',false,'savefail')}
};
$('btnReboot').onclick=async()=>{try{const r=await post('/api/reboot');msg('wifiMsg',r.ok,r.code)}catch(e){}};
$('btnTiming').onclick=()=>post('/api/timing/reset').catch(()=>{});
// 選好檔案先在瀏覽器找韌體身分標記(板子上傳時也會再檢查一次):不是這個控制器的韌體就不讓上傳,是的話顯示版本新舊.
// 比對字串拆開寫:網頁本身也在韌體裡,整段連在一起會被當成標記的開頭(板子掃描會因為後面不是版本號而略過,拆開更單純).
const FW_ID_PREFIX='LPFWID1:'+'ESP32C3-lineplane|';
let fwFileVer=null;   // null = 還沒檢查,'' = 找不到標記
function fwVerCmp(a,b){const x=a.split('.').map(Number),y=b.split('.').map(Number);
 for(let i=0;i<Math.max(x.length,y.length);i++){const d=(x[i]||0)-(y[i]||0);if(d)return d>0?1:-1}return 0}
$('fwFile').onchange=async()=>{
 const f=$('fwFile').files[0];fwFileVer=null;$('fwMsg').textContent='';if(!f)return;
 try{
  const b=new Uint8Array(await f.arrayBuffer()),p=[...FW_ID_PREFIX].map(c=>c.charCodeAt(0));let ver='';
  for(let i=b.indexOf(p[0]);i>=0&&!ver;i=b.indexOf(p[0],i+1)){
   let k=1;while(k<p.length&&b[i+k]===p[k])k++;if(k<p.length)continue;
   let j=i+p.length,v='';while(j<b.length&&v.length<23&&((b[j]>=48&&b[j]<=57)||b[j]===46))v+=String.fromCharCode(b[j++]);
   if(v&&b[j]===124)ver=v;
  }
  fwFileVer=ver;
  if(!ver){msg('fwMsg',false,'fwnotours');return}
  const cur=$('fwVer').textContent,c=fwVerCmp(ver,cur);
  $('fwMsg').className='msg '+(c<0?'bad':'ok');
  $('fwMsg').textContent=c>0?`檔案版本 ${ver},比目前的 ${cur} 新,可以上傳更新.`:c===0?`檔案版本 ${ver},和目前相同.`:`檔案版本 ${ver},比目前的 ${cur} 舊:上傳後會退回舊版.`;
 }catch(e){fwFileVer=null}
};
$('btnFw').onclick=()=>{
 const f=$('fwFile').files[0];if(!f){msg('fwMsg',false,'請先選擇檔案.');return}
 if(fwFileVer===''){msg('fwMsg',false,'fwnotours');return}
 const fd=new FormData();fd.append('firmware',f,f.name);
 const x=new XMLHttpRequest(),pg=$('fwProg');pg.hidden=false;pg.value=0;$('btnFw').disabled=true;
 x.upload.onprogress=e=>{if(e.lengthComputable)pg.value=e.loaded*100/e.total};
 x.onload=()=>{let r={};try{r=JSON.parse(x.responseText)}catch(e){}
  if(r.ok&&r.ver)msg('fwMsg',true,`更新為 ${r.ver}${r.older?'(退回舊版)':''}完成,重新開機中…`);else msg('fwMsg',!!r.ok,r.code||'updatefail');
  $('btnFw').disabled=false};
 x.onerror=()=>{msg('fwMsg',false,'上傳中斷.');$('btnFw').disabled=false};
 x.open('POST','/update');x.send(fd);
};

function showPane(p){if(!$(p))p='mon';pane=p;
 // 重新整理時停在同一頁. 網址用 #tab-xxx 而不是 #xxx:後者等於分頁區塊的 id,瀏覽器會自動捲過去,標題列蓋住卡片上半部.
 if(location.hash!=='#tab-'+p)history.replaceState(null,'','#tab-'+p);
 document.querySelectorAll('main>section').forEach(s=>s.hidden=s.id!==p);
 document.querySelectorAll('nav button').forEach(b=>b.classList.toggle('on',b.dataset.pane===p));
 if(p==='sys'){loadWifi();fwLoad()}
 if(p!=='esc')manLock(false);   // 離開電變頁自動上鎖手動輸出
 if(p==='prof'||p==='set'||p==='comp'||p==='inst'||p==='esc'||p==='bak')loadVals();
 if(p==='log')logFetch(true);
 tick();
}
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>showPane(b.dataset.pane));

(async function init(){
 for(let i=0;i<5&&!META;i++){try{META=await poll('/api/meta')}catch(e){await new Promise(r=>setTimeout(r,800))}}
 if(!META){toast('讀不到設定,請重新整理.',true);return}
 try{VALS=await poll('/api/settings');editP=VALS.active}catch(e){}
 buildProfile();buildShared();wireNotes(document);
 await loadVals();
 showPane(location.hash.replace(/^#(tab-)?/,'')||'mon');window.scrollTo(0,0);loadWifi();
})();
</script></body></html>)HTML";
