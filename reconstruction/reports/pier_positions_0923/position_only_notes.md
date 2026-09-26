# 柱位校對 2026-09-23

本輪依使用者指示只處理平面柱位，柱高與高架接段暫停。

## 復興路西側柱位
- 以兩個2025年街景視點目視對準同一根路側圓柱，使用公開相機位置與方向交會，暫對應舊模型 UNVERIFIED_Pier_642。
- 模型候選中心 (3315.97, 386.76)，取代舊中心 (3305.73,379.14) 的比較顯示。這是帶有定位誤差的估算，不是測量成果。
- 用2020年歷史影像另行核對，射線與候選中心約差1.95m。相機座標、影像方向、柱心判讀及物件對應皆仍有誤差。
- 3m顯示圈只供複核，不代表統計信賴區間。
- 既有道路／分隔島模型檢查：柱腳侵入道路且在分隔島外的面積由3.1056m²降至0。此結果依賴舊地面模型，不證明實際道路完全無衝突。
- 僅平移一根柱，未移動同組另一根柱及柱帽；後續必須重新核對它們的對應關係。
- 柱高仍為原值約4.8m。逐頂點比對Z完全一致、網格局部座標未變。
- 新場景 CIVIC_PIER_XY_REVIEW_20260923；展示場景保留。沒有載入或採用先前改柱高的比較版。
- 全線柱位校準未完成。本輪新增實測確認數為0，新增街景估算候選為1。

## 來源
- [西側視點，2025年4月](https://www.google.com/maps/@?api=1&map_action=pano&pano=GNaYshgbXGqT6PZXF7RvSw&heading=67.7&pitch=0)
- [東側視點，2025年1月](https://www.google.com/maps/@?api=1&map_action=pano&pano=4NKKDkj7LTh70nLelXcPqw&heading=279.2&pitch=0)
- [歷史第三視點，2020年10月](https://www.google.com/maps/@?api=1&map_action=pano&pano=2OrSAImf04uhBzzFvkc8jg&heading=59.8&pitch=0)

## 重現
triangulate_fuxing_pier.py OUTPUT_JSON 需要pyproj；check_fuxing_position.py FOOTPRINTS_JSON TRIANGULATION_JSON OUTPUT_JSON 需要shapely。
將結果存為blend同層 PierPositions_20260923/fuxing_642_position_review.json，再於Blender執行apply_fuxing_xy_comparison.py。
腳本在新場景不存在時執行；不重跑產生重複模型。腳本與公開來源紀錄備份到GitHub，blend與原始網格僅存本機。
