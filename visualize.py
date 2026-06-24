"""
이전상장(거래소 이동) 시각화 대시보드 생성.

transfers_detail.csv 를 단일 소스로 사용해 4개 패널을 하나의
인터랙티브 HTML(transfers_dashboard.html)로 출력한다.

  1) Sankey   - 거래소 간 전체 이동 흐름
  2) 누적 영역 - 연도별 방향별 건수 추이
  3) 막대      - NYSE<->NASDAQ 연도별 순이동(net)
  4) 라인      - NYSE<->NASDAQ 누적 순이동

사용: python visualize.py
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

DETAIL_CSV = "transfers_detail.csv"
OUT_HTML = "transfers_dashboard.html"

# 거래소별 고정 색상
EXCH_COLORS = {"NYSE": "#1f77b4", "NASDAQ": "#e8590c", "AMEX": "#2ca02c"}
DIR_COLORS = {
    "NYSE -> NASDAQ": "#e8590c",
    "NASDAQ -> NYSE": "#1f77b4",
    "NYSE -> AMEX": "#74c0fc",
    "AMEX -> NYSE": "#1864ab",
    "NASDAQ -> AMEX": "#ffa94d",
    "AMEX -> NASDAQ": "#d9480f",
}


def _sankey_trace(sub: pd.DataFrame, nodes: list, idx: dict, visible: bool):
    flow = sub.groupby(["from", "to"]).size().reset_index(name="n")
    return go.Sankey(
        visible=visible,
        arrangement="snap",
        node=dict(
            label=nodes,
            color=[EXCH_COLORS.get(n, "#888") for n in nodes],
            pad=25,
            thickness=24,
            line=dict(color="rgba(0,0,0,0.3)", width=0.5),
        ),
        link=dict(
            source=[idx[s] for s in flow["from"]],
            target=[idx[t] for t in flow["to"]],
            value=list(flow["n"]),
            color=["rgba(255,255,255,0.18)" for _ in range(len(flow))],
            hovertemplate="%{source.label} → %{target.label}<br>"
            "<b>%{value}건</b><extra></extra>",
        ),
    )


def fig_sankey(df: pd.DataFrame) -> go.Figure:
    """기간(10년) 슬라이더로 거래소 간 흐름을 넘겨보는 Sankey."""
    nodes = sorted(set(df["from"]) | set(df["to"]))
    idx = {name: i for i, name in enumerate(nodes)}

    df = df.copy()
    df["decade"] = (df["year"] // 10) * 10
    decades = sorted(df["decade"].unique())

    # 슬라이더 스텝: [전체] + 각 10년 구간
    periods = [("전체", df)] + [
        (f"{d}s", df[df["decade"] == d]) for d in decades
    ]
    traces = [
        _sankey_trace(sub, nodes, idx, visible=(i == 0))
        for i, (_, sub) in enumerate(periods)
    ]

    fig = go.Figure(data=traces)

    steps = []
    for i, (label, sub) in enumerate(periods):
        vis = [j == i for j in range(len(periods))]
        steps.append(
            dict(
                method="update",
                args=[
                    {"visible": vis},
                    {"title.text": f"<b>거래소 간 이전상장 흐름</b> · {label} "
                     f"({len(sub):,}건)"},
                ],
                label=label,
            )
        )

    fig.update_layout(
        title=f"<b>거래소 간 이전상장 흐름</b> · 전체 ({len(df):,}건)",
        font=dict(size=14),
        sliders=[
            dict(
                active=0,
                currentvalue={"prefix": "◀ 기간: ", "font": {"size": 16}},
                pad={"t": 50, "b": 10},
                steps=steps,
            )
        ],
    )
    return fig


def fig_yearly_area(df: pd.DataFrame) -> go.Figure:
    by_year = (
        df.groupby(["year", "direction"]).size().reset_index(name="n")
    )
    fig = px.area(
        by_year,
        x="year",
        y="n",
        color="direction",
        color_discrete_map=DIR_COLORS,
        category_orders={"direction": list(DIR_COLORS.keys())},
    )
    fig.update_traces(line=dict(width=0.5))
    fig.update_layout(
        title="<b>연도별 이전상장 건수</b> (방향별 누적 영역)",
        xaxis_title="연도",
        yaxis_title="건수",
        legend_title="이동 방향",
        hovermode="x unified",
    )
    return fig


def _ny_nasdaq_net(df: pd.DataFrame) -> pd.DataFrame:
    sub = df[df["direction"].isin(["NYSE -> NASDAQ", "NASDAQ -> NYSE"])]
    piv = (
        sub.groupby(["year", "direction"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=["NYSE -> NASDAQ", "NASDAQ -> NYSE"], fill_value=0)
        .sort_index()
    )
    # 양수 = NASDAQ로 순유입, 음수 = NYSE로 순유입
    piv["net_to_nasdaq"] = piv["NYSE -> NASDAQ"] - piv["NASDAQ -> NYSE"]
    piv["cum_net_to_nasdaq"] = piv["net_to_nasdaq"].cumsum()
    return piv.reset_index()


def fig_net_bar(net: pd.DataFrame) -> go.Figure:
    colors = ["#e8590c" if v >= 0 else "#1f77b4" for v in net["net_to_nasdaq"]]
    fig = go.Figure(
        go.Bar(
            x=net["year"],
            y=net["net_to_nasdaq"],
            marker_color=colors,
            hovertemplate="%{x}년: <b>%{y:+}</b>건<extra></extra>",
        )
    )
    fig.update_layout(
        title="<b>NYSE ↔ NASDAQ 연도별 순이동</b> "
        "(＋ NASDAQ 순유입 / － NYSE 순유입)",
        xaxis_title="연도",
        yaxis_title="순이동 (건)",
    )
    fig.add_hline(y=0, line_color="rgba(255,255,255,0.4)")
    fig.add_vline(x=2010, line_dash="dot", line_color="#ffd43b", line_width=1.5)
    fig.add_annotation(
        x=2010,
        yref="paper",
        y=0.95,
        text="2010년대<br>방향 역전",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#ffd43b",
        font=dict(color="#ffd43b", size=12),
        bgcolor="rgba(0,0,0,0.4)",
    )
    return fig


def fig_cum_line(net: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Scatter(
            x=net["year"],
            y=net["cum_net_to_nasdaq"],
            mode="lines",
            line=dict(color="#ffd43b", width=3),
            fill="tozeroy",
            fillcolor="rgba(255,212,59,0.15)",
            hovertemplate="%{x}년 누적: <b>%{y:+}</b>건<extra></extra>",
        )
    )
    fig.update_layout(
        title="<b>NYSE → NASDAQ 누적 순이동</b> (우상향 = NASDAQ 쪽으로 순유입)",
        xaxis_title="연도",
        yaxis_title="누적 순이동 (건)",
    )
    fig.add_hline(y=0, line_color="rgba(255,255,255,0.4)")
    return fig


def _esc(v) -> str:
    return (
        str(v)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_table(df: pd.DataFrame) -> str:
    """외부 라이브러리 없이 순수 HTML로 만든 목록 표.

    각 행에 data-period 속성을 넣어 슬라이더 연동 필터에 사용한다.
    """
    df = df.copy()
    df["period"] = ((df["year"] // 10) * 10).astype(int).astype(str) + "s"
    df = df.sort_values("change_date", ascending=False)

    headers = ["변경일", "회사명", "티커", "From", "To", "방향", "PERMNO"]
    cols = ["change_date", "comnam", "ticker", "from", "to", "direction", "permno"]

    head = "".join(
        f'<th onclick="sortTable({i})">{h} <span class="arr"></span></th>'
        for i, h in enumerate(headers)
    )
    rows = []
    for _, r in df.iterrows():
        cells = "".join(f"<td>{_esc(r[c])}</td>" for c in cols)
        rows.append(f'<tr data-period="{_esc(r["period"])}">{cells}</tr>')

    return (
        '<input id="tx-search" type="text" placeholder="🔍 검색 (회사명·티커·방향...)">'
        '<div class="tx-scroll"><table id="tx">'
        f"<thead><tr>{head}</tr></thead>"
        f'<tbody>{"".join(rows)}</tbody>'
        "</table></div>"
        '<div id="tx-count" class="sub"></div>'
    )


def main():
    df = pd.read_csv(DETAIL_CSV)
    df["year"] = df["year"].astype(int)

    net = _ny_nasdaq_net(df)
    figs = [
        fig_sankey(df),
        fig_yearly_area(df),
        fig_net_bar(net),
        fig_cum_line(net),
    ]
    for i, f in enumerate(figs):
        f.update_layout(
            template="plotly_dark",
            paper_bgcolor="#11151c",
            plot_bgcolor="#11151c",
            margin=dict(l=60, r=40, t=70, b=50),
            height=540 if i == 0 else 460,  # Sankey는 슬라이더 공간 확보
        )

    total = len(df)
    span = f"{df['year'].min()}–{df['year'].max()}"
    blocks = []
    for i, f in enumerate(figs):
        blocks.append(
            f.to_html(
                full_html=False,
                include_plotlyjs=True if i == 0 else False,  # 인라인(오프라인/사내망 대응)
                config={"displaylogo": False},
                div_id="sankey" if i == 0 else None,  # 슬라이더 연동용 고정 ID
            )
        )

    table_html = build_table(df)

    html = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<title>이전상장 대시보드</title>
<style>
  body {{ background:#0b0e13; color:#e6edf3; font-family:'Segoe UI',sans-serif;
         margin:0; padding:24px 32px; }}
  h1 {{ font-size:26px; margin:0 0 4px; }}
  .sub {{ color:#9aa7b4; margin-bottom:20px; }}
  .card {{ background:#11151c; border:1px solid #1f2630; border-radius:14px;
          padding:8px 12px; margin-bottom:22px; box-shadow:0 4px 24px rgba(0,0,0,.4); }}
  h2 {{ font-size:18px; margin:6px 4px 12px; }}
  /* 목록 표 (순수 CSS, 외부 의존 없음) */
  #tx-search {{ width:320px; max-width:90%; margin:4px 4px 12px; padding:8px 12px;
      background:#0b0e13; color:#e6edf3; border:1px solid #2b3543; border-radius:8px;
      font-size:14px; }}
  .tx-scroll {{ max-height:520px; overflow:auto; border:1px solid #1f2630;
      border-radius:10px; }}
  #tx {{ width:100%; color:#e6edf3; border-collapse:collapse; font-size:13.5px; }}
  #tx thead th {{ position:sticky; top:0; background:#161c25; color:#ffd43b;
      text-align:left; padding:9px 12px; cursor:pointer; user-select:none;
      border-bottom:1px solid #2b3543; white-space:nowrap; }}
  #tx thead th:hover {{ background:#1c2530; }}
  #tx tbody td {{ border-bottom:1px solid #1a212b; padding:6px 12px; }}
  #tx tbody tr:hover {{ background:#19222e; }}
  #tx-count {{ margin:10px 4px 2px; }}
  .arr {{ color:#ffd43b; font-size:11px; }}
</style></head><body>
  <h1>🗽 미국 거래소 이전상장 대시보드</h1>
  <div class="sub">CRSP 기반 · 총 <b>{total:,}</b>건 · 기간 {span} · NYSE / NASDAQ / AMEX</div>
  {''.join(f'<div class="card">{b}</div>' for b in blocks)}
  <div class="card">
    <h2>📋 이전상장 목록 — <span id="period-label" style="color:#ffd43b">전체</span>
        <span class="sub" style="font-size:13px">(위 슬라이더와 연동 · 검색·헤더클릭 정렬)</span></h2>
    {table_html}
  </div>
  <script>
    (function() {{
      var tbody = document.querySelector('#tx tbody');
      var allRows = Array.prototype.slice.call(tbody.querySelectorAll('tr'));
      var search = document.getElementById('tx-search');
      var countEl = document.getElementById('tx-count');
      var periodFilter = null;          // null = 전체
      var sortCol = 0, sortDir = -1;    // 기본: 변경일 내림차순

      function visibleByFilter(tr) {{
        var q = search.value.trim().toLowerCase();
        if (periodFilter && tr.getAttribute('data-period') !== periodFilter) return false;
        if (q && tr.textContent.toLowerCase().indexOf(q) === -1) return false;
        return true;
      }}

      function render() {{
        var shown = 0;
        allRows.forEach(function(tr) {{
          var ok = visibleByFilter(tr);
          tr.style.display = ok ? '' : 'none';
          if (ok) shown++;
        }});
        countEl.textContent = shown.toLocaleString() + '건 표시 중 (전체 ' +
          allRows.length.toLocaleString() + '건)';
      }}

      function sortTable(col) {{
        if (col === sortCol) sortDir = -sortDir; else {{ sortCol = col; sortDir = 1; }}
        var rows = allRows.slice().sort(function(a, b) {{
          var x = a.children[col].textContent, y = b.children[col].textContent;
          var nx = parseFloat(x), ny = parseFloat(y);
          var cmp = (!isNaN(nx) && !isNaN(ny)) ? nx - ny : x.localeCompare(y);
          return cmp * sortDir;
        }});
        rows.forEach(function(tr) {{ tbody.appendChild(tr); }});
        document.querySelectorAll('#tx thead .arr').forEach(function(s) {{ s.textContent = ''; }});
        document.querySelectorAll('#tx thead th')[col]
          .querySelector('.arr').textContent = sortDir > 0 ? '▲' : '▼';
      }}
      window.sortTable = sortTable;

      search.addEventListener('input', render);

      // Sankey 기간 슬라이더 → 목록 필터 연동
      var gd = document.getElementById('sankey');
      if (gd && gd.on) {{
        gd.on('plotly_sliderchange', function(e) {{
          var label = (e && e.step) ? e.step.label : null;
          if (!label) return;
          document.getElementById('period-label').textContent = label;
          periodFilter = (label === '전체') ? null : label;
          render();
        }});
      }}

      render();
    }})();
  </script>
</body></html>"""

    with open(OUT_HTML, "w", encoding="utf-8") as fh:
        fh.write(html)

    print(f"생성 완료: {OUT_HTML}  (총 {total:,}건)")


if __name__ == "__main__":
    main()
