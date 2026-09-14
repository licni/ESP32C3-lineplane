# 測試與工具

這裡的腳本在電腦上執行,透過板子的**網頁 API** 與 **USB 序列埠指令**做實機測試. 板子放在桌上即可,不接馬達與螺旋槳.

## 使用前

- Python 用 PlatformIO 內建的:`%USERPROFILE%\.platformio\penv\Scripts\python.exe`(已含 `pyserial`;瀏覽器測試需要 `websockets`,同一個環境內建).
- 板子接 USB(預設 `COM20`,可用環境變數 `LP_PORT` 改),網路位址用參數或環境變數 `LP_HOST`(例如 `lineplane.local` 或 IP).
- 瀏覽器測試用 Windows 內建的 Microsoft Edge(無頭模式,Chrome DevTools Protocol).
- **序列埠一律用 `dtr=False, rts=False` 開啟,而且只開一次**:ESP32-C3 原生 USB 會把 DTR/RTS 切換當成重置.
- 會改設定的測試,開始前確認板子待機且沒有未儲存變更,備份板上設定,結束後還原並逐項比對.

## 測試用序列指令(只能從 USB 開啟,存在記憶體,不影響飛行)

| 指令 | 用途 |
|---|---|
| `sim att <機頭°> <滾轉°>` / `sim pulse <x|y|z> <g> <毫秒> [延遲]` / `sim vib` / `sim fail 1` / `sim off` | 感測器模擬:姿態,推力或撞擊脈衝,抖動,讀取失敗 |
| `armsw 0\|1\|off` | 安全開關覆寫(開發板沒接 GPIO21 開關時用;軟體重開保留,拔電清除) |
| `pwmcap on` / `pwm` | GPIO5 量測電變脈寬(GPIO5 跳線接 GPIO4) |
| `powerontest` | 下一次軟體重開當作上電(測上電後直接倒數) |
| `fwwin <秒>` / `fwurl <https 資料夾>` | 縮短新韌體確認時限 / 暫時改讀測試用更新來源 |
| `calexp <秒>` | 縮短電變校正旗標時效 |
| `gesture` `cancel` `estop` `tilt` `twist` `disturb` | 模擬手勢,取消,緊急停止,傾斜,扭轉,外力 |

## 共用工具

| 檔案 | 用途 |
|---|---|
| `lp_test.py` | 測試共用:HTTP,序列埠(只開一次),檢查項目與紀錄,測試前備份與結束還原 |
| `board_backup.py` | 板上設定備份 / 還原 / 比對(`python board_backup.py save 檔名.json 位址`) |
| `restore_unsaved.py` | 燒錄後把燒錄前未儲存的值放回 |
| `recover.py` | 測試中斷時救援:緊急停止,關閉模擬,用備份還原 |
| `run_regression.py` | 批次跑回歸測試 |
| `publish_firmware.py` | 發布韌體到公開更新專案(每天只留最新一版,說明合併) |
| `pio_strip_paths.py` | PlatformIO 建置前腳本:編進韌體的原始檔路徑換成短前綴,發布的韌體不帶電腦使用者名稱 |
| `readme_shots.py` | 產生首頁 README 的網頁截圖 |
| `shot_page.py` | 網頁截圖工具(指定分頁與元素) |

## 全功能測試(t0 ~ t9)

| 檔案 | 內容 |
|---|---|
| `t0_hooks_sanity.py` | 測試掛勾健全性 |
| `t1_start_safety.py` | 起飛安全:手勢,放穩,倒數,外力,扭轉取消,水平限制,感測器故障 |
| `t2_flight_throttle.py` | 飛行油門時間軸,補償曲線,上下限,實測脈寬 |
| `t3_landing_stop.py` | 降落與停止:觸地衝擊,靜止,滑行抖動,保險時間,撞擊斷電,緊急停止,飛行中感測器故障 |
| `t4_led_log_lock.py` | 燈號,飛行紀錄,設定鎖定 |
| `t5_esc_service.py` | 電變手動輸出,心跳逾時,校正旗標,PWM 頻率 |
| `t6_dshot_flight.py` | DShot300 + 轉速回傳的完整飛行 |
| `t7_web_buttons.py` | 網頁取消倒數與緊急停止按鈕 |
| `t8_imu_recover_observe.py` | 感測器故障鎖定到重新上電 |
| `t9_gear_flight.py` | 機輪收腳時機與限制 |

## 功能專測

| 檔案 | 內容 |
|---|---|
| `arm_switch_test.py` | GPIO21 安全開關,撞擊斷電連續 2 拍 |
| `safety2_test.py` | 撞擊後不接受推力手勢,校正旗標時效,油門下限 10%,飛行中鎖住 WiFi 寫入 |
| `flight_sm_test.py` | 飛行狀態機(含軟體重開不自動倒數) |
| `start_level_test.py` | 起飛前水平限制 |
| `twist_cancel_test.py` / `extend_cap_test.py` / `event_log_test.py` | 扭轉取消 / 外力延長上限 / 事件紀錄 |
| `fw_update_test.py` / `fw_paths_test.py` / `fw_fail_test.py` | 韌體下載更新與退回 / 三種更新方式 / 下載失敗與寫入途中擋起飛 |
| `wifi_protect_test.py` / `wifi_apname_test.py` | WiFi 設定保護與救援 / 熱點名稱 |
| `settings_api_test.py` / `input_robustness_test.py` | 設定 API / 錯誤輸入 |
| `dshot_test.py` / `rpm_telemetry_test.py` / `rpm_emulator_test.py` / `esc_service_test.py` | DShot 輸出與轉速回傳 / 電變維護 API |
| `gear_test_nosettings.py` | 機輪收腳舵機 |
| `curve_ui_test.py` / `limits_move_test.py` / `step_button_test.py` / `ui_input_touch_test.py` / `pinch_touch_test.py` / `web_start_test.py` / `earlyland_hide_check.py` | 網頁介面(瀏覽器實際操作) |
| `web_load_test.py` | 網頁負載下的控制迴圈計時 |

## 模擬(不需要板子)

| 檔案 | 內容 |
|---|---|
| `sim_attitude.py` | 線控飛行姿態估算模擬,驗證向心力補償 Mahony |
| `sim_impact.py` | 觸地衝擊與地面滑行抖動判斷,濾波常數掃描 |

## 一次性工具

`gear_flash_verify.py`,`set_gear_travel.py`,`wifi_restore_confirmed.py`,`wifi_revert_probe.py`:特定開發階段用過的檢查與還原腳本,保留供參考.
