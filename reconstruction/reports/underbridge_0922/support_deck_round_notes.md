# 柱位／柱高／橋面連接比較版 2026-09-22

目前場景 CIVIC_SUPPORT_ALIGNMENT_EST_0922 是估算比較版。原 CIVIC_UNDERBRIDGE_MASSING_20260916 保留。本輪沒有新增實測高程，也没有完成全線街景位置修正。

- 以柱組共同平移搜尋：步長0.5m，距離上限12m；完整柱腳加0.1m餘量須在估算分隔島與橋面範圍內。
- 初始42組有平面候選；386組被街景形態疑點攔下，518組維持迴轉口疑點；43組無可行位置。
- 41組候選還須接到地面和梁體。最後只建3組、5根柱：642/643、730/731、460。其餘未採用。
- 柱高約4.42m，是現有模型地面約0.18m至柱帽底約4.60m的差值；支承厚0.20m仍是先前選定的工作假設，不是實測。
- 原始支承模型已保留；比較版3組柱位仍未經街景座標確認。
- 30段平面橋面在相同估算Z=8m下做幾何聯集，清理公差1mm，生成一個連通封閉殼體；Blender邊檢查沒有非流形邊或零面積面。
- 此聯集僅為橋面殼體。梁體、護欄接縫、真實匝道縱坡及不同高程交會並未藉此重建。不能把此比較版當作真實全線接橋完成。
- 原跨段高度標記對比較版已過時，於比較版隱藏。原場景仍可查原始取樣。

## 街景觀察
[光復路東側，2025年1月，向南](https://www.google.com/maps/@?api=1&map_action=pano&pano=-mhyRldoDgcRnniHnvmIoQ&heading=180&pitch=0)
可見島上大矩形橋墩、護欄、植栽及梁體。這不足以支持386組模型僅平移1.12m就是正確柱位，因此該組未採用。

## 重現順序
輸入支柱／分隔島／橋面網格另存 support_search_input.json（本機）。執行 search_support_alignment.py input.json output.json；街景排除紀錄存 support_alignment_candidates.json。
在原場景執行 build_support_alignment_comparison.py，再執行 fit_supports_at_cap_girder_contacts.py。
使用 union_deck_shells.py input.json continuous_deck_input.json 產生比較殼體，再執行 install_continuous_deck_comparison.py。
原始輸入、大型網格及blend保留本機；GitHub備份腳本和摘要。比較場景目前使用局部檢視方便查柱，數字鍵盤 / 可切回全景。
