"""Generate er_diagram.svg — wide canvas, no overlapping tables."""
import os, base64

# Canvas: 1400 wide x 580 tall
# Table 1 (Movie)       : x=20,  width=340  → right edge=360
# Table 2 (MovieGenre)  : x=530, width=320  → right edge=850
# Table 3 (Genre)       : x=1020,width=360  → right edge=1380
# Gap between tables: ~170px each — plenty of room for connector lines

svg = """\
<svg viewBox="0 0 1400 580" width="1400" height="580"
     xmlns="http://www.w3.org/2000/svg"
     style="background:#F1F5F9;border-radius:12px;font-family:Segoe UI,Roboto,Arial,sans-serif;">

  <!-- Background gradient panels -->
  <defs>
    <marker id="arr-b" viewBox="0 0 10 10" refX="8" refY="5"
            markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,1 L10,5 L0,9 Z" fill="#2563EB"/>
    </marker>
    <marker id="arr-g" viewBox="0 0 10 10" refX="8" refY="5"
            markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,1 L10,5 L0,9 Z" fill="#059669"/>
    </marker>
  </defs>

  <!-- ══════════════════════════════════════════
       TABLE 1 — Movie   (x=20)
       ══════════════════════════════════════════ -->
  <g transform="translate(20,30)">
    <!-- Card shadow -->
    <rect x="4" y="4" width="340" height="460" rx="10" fill="#CBD5E1" opacity="0.5"/>
    <!-- Card body -->
    <rect width="340" height="460" rx="10" fill="#FFFFFF" stroke="#0284C7" stroke-width="2.5"/>
    <!-- Header -->
    <rect width="340" height="46" rx="10" fill="#0284C7"/>
    <rect y="20" width="340" height="26" fill="#0284C7"/>
    <text x="16" y="30" fill="#FFFFFF" font-weight="700" font-size="17">Movie</text>
    <text x="225" y="30" fill="#BAE6FD" font-size="12">[Primary Entity]</text>

    <!-- Column rows -->
    <rect x="1" y="46" width="338" height="30" fill="#FFF7ED"/>
    <text x="16" y="67" font-size="13" font-weight="700" fill="#92400E">tmdb_id</text>
    <text x="145" y="67" font-size="11" fill="#6B7280">INT</text>
    <text x="230" y="67" font-size="11" fill="#DC2626" font-weight="600">PK · NOT NULL</text>

    <line x1="1" y1="76" x2="339" y2="76" stroke="#E2E8F0"/>
    <text x="16" y="97" font-size="12" fill="#1E293B">title</text>
    <text x="145" y="97" font-size="11" fill="#6B7280">VARCHAR(255)</text>
    <text x="280" y="97" font-size="11" fill="#374151">NOT NULL</text>

    <line x1="1" y1="106" x2="339" y2="106" stroke="#E2E8F0"/>
    <text x="16" y="127" font-size="12" fill="#1E293B">release_date</text>
    <text x="145" y="127" font-size="11" fill="#6B7280">DATE</text>
    <text x="280" y="127" font-size="11" fill="#374151">NULL</text>

    <line x1="1" y1="136" x2="339" y2="136" stroke="#E2E8F0"/>
    <text x="16" y="157" font-size="12" fill="#1E293B">budget</text>
    <text x="145" y="157" font-size="11" fill="#6B7280">BIGINT</text>
    <text x="280" y="157" font-size="11" fill="#374151">NULL</text>

    <line x1="1" y1="166" x2="339" y2="166" stroke="#E2E8F0"/>
    <text x="16" y="187" font-size="12" fill="#1E293B">revenue</text>
    <text x="145" y="187" font-size="11" fill="#6B7280">BIGINT</text>
    <text x="280" y="187" font-size="11" fill="#374151">NULL</text>

    <line x1="1" y1="196" x2="339" y2="196" stroke="#E2E8F0"/>
    <text x="16" y="217" font-size="12" fill="#1E293B">runtime</text>
    <text x="145" y="217" font-size="11" fill="#6B7280">DECIMAL(6,2)</text>
    <text x="280" y="217" font-size="11" fill="#374151">NULL</text>

    <line x1="1" y1="226" x2="339" y2="226" stroke="#E2E8F0"/>
    <text x="16" y="247" font-size="12" fill="#1E293B">vote_average</text>
    <text x="145" y="247" font-size="11" fill="#6B7280">DECIMAL(3,1)</text>
    <text x="280" y="247" font-size="11" fill="#374151">NULL</text>

    <line x1="1" y1="256" x2="339" y2="256" stroke="#E2E8F0"/>
    <text x="16" y="277" font-size="12" fill="#1E293B">vote_count</text>
    <text x="145" y="277" font-size="11" fill="#6B7280">INT</text>
    <text x="280" y="277" font-size="11" fill="#374151">NULL</text>

    <line x1="1" y1="286" x2="339" y2="286" stroke="#E2E8F0"/>
    <text x="16" y="307" font-size="12" fill="#1E293B">popularity</text>
    <text x="145" y="307" font-size="11" fill="#6B7280">DECIMAL(10,4)</text>
    <text x="280" y="307" font-size="11" fill="#374151">NULL</text>

    <line x1="1" y1="316" x2="339" y2="316" stroke="#E2E8F0"/>
    <text x="16" y="337" font-size="12" fill="#1E293B">overview</text>
    <text x="145" y="337" font-size="11" fill="#6B7280">TEXT</text>
    <text x="280" y="337" font-size="11" fill="#374151">NULL</text>

    <line x1="1" y1="346" x2="339" y2="346" stroke="#E2E8F0"/>
    <text x="16" y="367" font-size="12" fill="#1E293B">created_at</text>
    <text x="145" y="367" font-size="11" fill="#6B7280">TIMESTAMP</text>
    <text x="280" y="367" font-size="11" fill="#374151">DEFAULT NOW()</text>

    <line x1="1" y1="376" x2="339" y2="376" stroke="#E2E8F0"/>
    <!-- Footer note -->
    <rect x="1" y="430" width="338" height="29" rx="0" fill="#EFF6FF"/>
    <rect x="1" y="430" width="338" height="29" rx="0" fill="#EFF6FF"/>
    <text x="16" y="449" font-size="11" fill="#1D4ED8">10 columns  ·  3NF compliant  ·  InnoDB</text>
  </g>

  <!-- ══════════════════════════════════════════
       TABLE 2 — MovieGenre Bridge (x=530)
       ══════════════════════════════════════════ -->
  <g transform="translate(530,110)">
    <rect x="4" y="4" width="320" height="300" rx="10" fill="#CBD5E1" opacity="0.5"/>
    <rect width="320" height="300" rx="10" fill="#FFFFFF" stroke="#4F46E5" stroke-width="2.5"/>
    <rect width="320" height="46" rx="10" fill="#4F46E5"/>
    <rect y="20" width="320" height="26" fill="#4F46E5"/>
    <text x="16" y="30" fill="#FFFFFF" font-weight="700" font-size="17">MovieGenre</text>
    <text x="195" y="30" fill="#C7D2FE" font-size="12">[Bridge / Junction]</text>

    <!-- tmdb_id FK -->
    <rect x="1" y="46" width="318" height="30" fill="#FFF7ED"/>
    <text x="16" y="67" font-size="13" font-weight="700" fill="#0369A1">tmdb_id</text>
    <text x="130" y="67" font-size="11" fill="#6B7280">INT</text>
    <text x="195" y="67" font-size="11" fill="#DC2626" font-weight="600">PK · FK → Movie</text>

    <line x1="1" y1="76" x2="319" y2="76" stroke="#E2E8F0"/>
    <!-- genre_id FK -->
    <rect x="1" y="76" width="318" height="30" fill="#F0FDF4"/>
    <text x="16" y="97" font-size="13" font-weight="700" fill="#0369A1">genre_id</text>
    <text x="130" y="97" font-size="11" fill="#6B7280">INT</text>
    <text x="195" y="97" font-size="11" fill="#DC2626" font-weight="600">PK · FK → Genre</text>

    <line x1="1" y1="106" x2="319" y2="106" stroke="#E2E8F0"/>

    <!-- Constraint notes -->
    <text x="16" y="135" font-size="12" fill="#374151" font-weight="600">Constraints:</text>
    <text x="16" y="158" font-size="11" fill="#475569">PRIMARY KEY (tmdb_id, genre_id)</text>
    <text x="16" y="178" font-size="11" fill="#475569">FK1: tmdb_id → Movie(tmdb_id)</text>
    <text x="16" y="198" font-size="11" fill="#6B7280">       ON DELETE CASCADE</text>
    <text x="16" y="218" font-size="11" fill="#475569">FK2: genre_id → Genre(genre_id)</text>
    <text x="16" y="238" font-size="11" fill="#6B7280">       ON DELETE CASCADE</text>

    <line x1="1" y1="250" x2="319" y2="250" stroke="#E2E8F0"/>
    <rect x="1" y="270" width="318" height="29" fill="#EEF2FF"/>
    <text x="16" y="289" font-size="11" fill="#4338CA">2 columns  ·  Composite PK  ·  Resolves M:N</text>
  </g>

  <!-- ══════════════════════════════════════════
       TABLE 3 — Genre (x=1020)
       ══════════════════════════════════════════ -->
  <g transform="translate(1010,80)">
    <rect x="4" y="4" width="360" height="290" rx="10" fill="#CBD5E1" opacity="0.5"/>
    <rect width="360" height="290" rx="10" fill="#FFFFFF" stroke="#059669" stroke-width="2.5"/>
    <rect width="360" height="46" rx="10" fill="#059669"/>
    <rect y="20" width="360" height="26" fill="#059669"/>
    <text x="16" y="30" fill="#FFFFFF" font-weight="700" font-size="17">Genre</text>
    <text x="100" y="30" fill="#A7F3D0" font-size="12">[Lookup / Master Entity]</text>

    <rect x="1" y="46" width="358" height="30" fill="#FFF7ED"/>
    <text x="16" y="67" font-size="13" font-weight="700" fill="#92400E">genre_id</text>
    <text x="160" y="67" font-size="11" fill="#6B7280">INT</text>
    <text x="225" y="67" font-size="11" fill="#DC2626" font-weight="600">PK · AUTO_INCREMENT</text>

    <line x1="1" y1="76" x2="359" y2="76" stroke="#E2E8F0"/>
    <text x="16" y="97" font-size="12" fill="#1E293B">genre_name</text>
    <text x="160" y="97" font-size="11" fill="#6B7280">VARCHAR(100)</text>
    <text x="285" y="97" font-size="11" fill="#374151">UNIQUE · NOT NULL</text>

    <line x1="1" y1="106" x2="359" y2="106" stroke="#E2E8F0"/>
    <text x="16" y="127" font-size="12" fill="#1E293B">created_at</text>
    <text x="160" y="127" font-size="11" fill="#6B7280">TIMESTAMP</text>
    <text x="285" y="127" font-size="11" fill="#374151">DEFAULT NOW()</text>

    <line x1="1" y1="136" x2="359" y2="136" stroke="#E2E8F0"/>

    <text x="16" y="165" font-size="12" fill="#374151" font-weight="600">Constraints:</text>
    <text x="16" y="188" font-size="11" fill="#475569">UNIQUE (genre_name)</text>
    <text x="16" y="208" font-size="11" fill="#475569">CHECK genre_name != ""</text>
    <text x="16" y="228" font-size="11" fill="#6B7280">Stores 17+ unique genre categories</text>

    <line x1="1" y1="250" x2="359" y2="250" stroke="#E2E8F0"/>
    <rect x="1" y="260" width="358" height="29" fill="#ECFDF5"/>
    <text x="16" y="279" font-size="11" fill="#065F46">3 columns  ·  Master lookup table  ·  InnoDB</text>
  </g>

  <!-- ══════════════════════════════════════════
       RELATIONSHIP ARROWS
       Movie(360,490) → MovieGenre(530,260)
       Genre(1010,225) → MovieGenre(850,225)
       ══════════════════════════════════════════ -->

  <!-- Movie → MovieGenre  (1 to M) -->
  <!-- Exit right edge of Movie table at y=270 (mid-height of card at y=30+460/2=260) -->
  <path d="M 362,290  H 460,290  V 258  H 528,258"
        fill="none" stroke="#2563EB" stroke-width="2.5"
        stroke-dasharray="6,3"
        marker-end="url(#arr-b)"/>
  <!-- Cardinality labels -->
  <rect x="362" y="278" width="22" height="20" rx="4" fill="#DBEAFE"/>
  <text x="373" y="292" text-anchor="middle" font-size="13" font-weight="700" fill="#1D4ED8">1</text>
  <rect x="500" y="244" width="24" height="20" rx="4" fill="#DBEAFE"/>
  <text x="512" y="258" text-anchor="middle" font-size="13" font-weight="700" fill="#1D4ED8">M</text>

  <!-- Genre → MovieGenre  (1 to M) -->
  <!-- Exit left edge of Genre table at y=225 -->
  <path d="M 1008,225  H 900,225  V 225  H 852,225"
        fill="none" stroke="#059669" stroke-width="2.5"
        stroke-dasharray="6,3"
        marker-end="url(#arr-g)"/>
  <rect x="975" y="212" width="22" height="20" rx="4" fill="#D1FAE5"/>
  <text x="986" y="226" text-anchor="middle" font-size="13" font-weight="700" fill="#065F46">1</text>
  <rect x="855" y="212" width="24" height="20" rx="4" fill="#D1FAE5"/>
  <text x="867" y="226" text-anchor="middle" font-size="13" font-weight="700" fill="#065F46">M</text>

  <!-- ══════════════════════════════════════════
       LEGEND  (bottom-left)
       ══════════════════════════════════════════ -->
  <g transform="translate(20,520)">
    <rect width="560" height="45" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/>
    <!-- PK -->
    <rect x="12" y="10" width="34" height="22" rx="4" fill="#FFF7ED" stroke="#D97706" stroke-width="1"/>
    <text x="29" y="26" text-anchor="middle" font-size="11" font-weight="700" fill="#92400E">PK</text>
    <text x="52" y="26" font-size="11" fill="#374151">= Primary Key</text>
    <!-- FK -->
    <rect x="168" y="10" width="34" height="22" rx="4" fill="#EFF6FF" stroke="#2563EB" stroke-width="1"/>
    <text x="185" y="26" text-anchor="middle" font-size="11" font-weight="700" fill="#1D4ED8">FK</text>
    <text x="208" y="26" font-size="11" fill="#374151">= Foreign Key</text>
    <!-- UK -->
    <rect x="330" y="10" width="34" height="22" rx="4" fill="#F0FDF4" stroke="#059669" stroke-width="1"/>
    <text x="347" y="26" text-anchor="middle" font-size="11" font-weight="700" fill="#065F46">UK</text>
    <text x="370" y="26" font-size="11" fill="#374151">= Unique Key</text>
    <!-- Arrow -->
    <line x1="460" y1="21" x2="490" y2="21" stroke="#2563EB" stroke-width="2" stroke-dasharray="5,2" marker-end="url(#arr-b)"/>
    <text x="498" y="26" font-size="11" fill="#374151">= Relationship</text>
  </g>

  <!-- Title -->
  <text x="700" y="22" text-anchor="middle" font-size="15" font-weight="700" fill="#1E293B">
    Entity-Relationship Diagram — MovieAnalytics Database (3NF)
  </text>
</svg>
"""

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "er_diagram.svg")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(svg)

with open(out_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")

print(f"Written: {out_path}")
print(f"Base64 length: {len(b64)} chars — OK")
