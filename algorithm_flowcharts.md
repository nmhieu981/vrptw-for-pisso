# Lưu đồ Thuật toán (Flowcharts) - Preference-Based iNSSSO

Dưới đây là sơ đồ chi tiết luồng hoạt động tổng quan của thuật toán iNSSSO và các thuật toán thành phần bên trong. Các sơ đồ sử dụng standard Mermaid.js hỗ trợ hiển thị trực tiếp. Đã khắc phục lỗi cú pháp bằng cách sử dụng `""` chặt chẽ cho syntax của Mermaid.

---

## 1. Lưu đồ Tổng quan iNSSSO (Main Loop)

Đây là luồng thực thi chính của toàn bộ hệ thống từ khi bắt đầu chạy cho đến khi trả về kết quả cuối cùng (Pareto front).

```mermaid
flowchart TD
    Start(["Bắt đầu iNSSSO"]) --> InitPop["Khởi tạo Quần thể ban đầu<br/>N_sol lời giải"]
    InitPop --> AutoCal["Tính tự động Reference Point g<br/>(Auto-calibration)"]
    AutoCal --> InitArchive["Thêm quần thể vào External Archive"]
    
    InitArchive --> CheckGen{"Đạt giới hạn<br/>thời gian?"}
    
    CheckGen -- Có --> Finalize["Cập nhật Rank cuối cùng<br/>Trích xuất Pareto Front"]
    Finalize --> End(["Kết thúc"])
    
    CheckGen -- Không --> RankPop["Fast Non-dominated Sort<br/>& Crowding Distance"]
    RankPop --> AdaptParam["Điều chỉnh tham số thích nghi<br/>N_abs, mutation_rate"]
    AdaptParam --> Offspring["Bắt đầu tạo Thế hệ con<br/>Offspring = rỗng"]
    
    Offspring --> LoopPop["Lặp qua từng cá thể i trong Quần thể"]
    
    LoopPop --> CheckProb{"Hệ số Random < N_abs?"}
    
    CheckProb -- Có --> DoABS["Thực hiện ABS Search<br/>(Tìm kiếm lân cận cục bộ)"]
    CheckProb -- Không --> SelGBest["Chọn gBest bằng ASF<br/>(Binary Tournament)"]
    SelGBest --> DoSSO["Cập nhật vị trí bằng SSO<br/>(Squirrel Search)"]
    DoSSO --> CheckStag{"Có đang bị Stagnation?"}
    CheckStag -- Có --> DoMut["Đột biến Đa thức<br/>(Polynomial Mutation)"]
    DoMut --> EvalMut["Đánh giá lại hàm mục tiêu"]
    CheckStag -- Không --> EvalMut
    
    DoABS --> CheckValid["Decode và Đánh giá"]
    EvalMut --> CheckValid
    
    CheckValid --> CheckLocal{"Là Rank 0<br/>& Random < LS_Prob?"}
    CheckLocal -- Có --> DoLocal["Thực hiện Local Search<br/>(2-opt + Smart Merge)"]
    DoLocal --> EvalLocal["Đánh giá lại"]
    CheckLocal -- Không --> SaveOffspring["Đưa vào tập Offspring"]
    EvalLocal --> SaveOffspring
    
    SaveOffspring --> CheckLoopEnd{"Đã duyệt hết<br/>cá thể?"}
    CheckLoopEnd -- Chưa --> LoopPop
    
    CheckLoopEnd -- Rồi --> UpdateArchive["Cập nhật External Archive<br/>(Ɛ-dominance + ASF)"]
    UpdateArchive --> Inject["Chèn ngẫu nhiên 1 cá thể<br/>từ Archive vào Offspring"]
    Inject --> MergePop["Gộp Population cũ và Offspring<br/>(Kích thước = 2 * N_sol)"]
    MergePop --> RankMerged["Rank và Crowding tập gộp"]
    RankMerged --> SelectBest["Select Best (Env Selection)<br/>Ưu tiên: 1. Số xe nhỏ, 2. No Duplicate, 3. Rank, 4. CD"]
    SelectBest --> UpdatePop["Cập nhật Population mới<br/>(Kích thước = N_sol)"]
    UpdatePop --> CheckGen

    classDef main fill:#f9f,stroke:#333,stroke-width:2px;
    classDef decision fill:#ff9,stroke:#333,stroke-width:2px;
    class CheckGen,CheckProb,CheckStag,CheckValid,CheckLocal,CheckLoopEnd decision;
```

---

## 2. Lưu đồ Khởi tạo (Best Initialization & Smart Merge)

Bước tạo ra seed ban đầu để thuật toán xoay vòng. Giai đoạn này rất quan trọng để có được số lượng xe tối ưu.

```mermaid
flowchart TD
    Start(["Bắt đầu Khởi tạo"]) --> SetSeeds["Kích hoạt các chiến lược tạo Seed:<br/>1. Insertion (6 sort keys)<br/>2. Clarke-Wright<br/>3. Nearest-Neighbour"]
    
    SetSeeds --> GenCandidates["Tạo các nhóm ứng viên kết hợp<br/>Ruin-and-Recreate với noise"]
    
    GenCandidates --> FullLS["Đưa top 2 kandidat tốt nhất<br/>qua Full Local Search"]
    
    FullLS --> GetBest["Chọn candidate có Distance nhỏ nhất"]
    
    GetBest --> CheckUtil{"Tỷ lệ lấp đầy tải<br/>(Capacity Util) < 60%?"}
    
    CheckUtil -- Có --> DoMerge["Thực hiện Smart Route Merge<br/>(Cố gắng giảm số xe)"]
    CheckUtil -- Không --> SkipMerge["Bỏ qua bước gộp"]
    
    DoMerge --> Output(["Trả về Candidate tối ưu"])
    SkipMerge --> Output
    
    subgraph "Route Merging Process"
        M1["Xếp hạng xe theo số lượng khách<br/>(chọn xe ít khách nhất)"] --> M2["Cố gắng lấy khách từ xe này<br/>chèn qua các xe khác"]
        M2 --> M3{"Tất cả khách đều chèn<br/>được thành công?"}
        M3 -- Có --> M4["Xóa bỏ chiếc xe cũ<br/>2-opt lại các xe bị ảnh hưởng"]
        M4 --> M5{"Tổng Distance<br/>tăng <= 5%?"}
        M5 -- Có --> M6["Xác nhận Gộp thành công<br/>(giảm 1 xe)"]
        M5 -- Không --> M7["Hủy thao tác Gộp"]
        M3 -- Không --> M7
    end

    classDef decision fill:#ff9,stroke:#333,stroke-width:2px;
    class CheckUtil,M3,M5 decision;
```

---

## 3. Lưu đồ Chọn gBest và Chọn lọc Cá thể (Selection mechanism)

Bước quyết định xu hướng tiến hóa của thuật toán — ép giảm số lượng tuyến xe trước, sau đó rẽ theo ưu tiên của người dùng.

```mermaid
flowchart TD
    subgraph "Select gBest"
        StartG(["Bắt đầu chọn gBest"]) --> Pick2["Chọn ngẫu nhiên 2 cá thể<br/>từ Pareto Front rank 0"]
        Pick2 --> CmpRoutes{"Số tuyến xe<br/>có khác nhau?"}
        CmpRoutes -- Có --> RetLess["Trả về cá thể<br/>có cấu hình ÍT XE HƠN"]
        CmpRoutes -- Không --> CalcASF["Tính ASF Score<br/>(Dựa trên w và g)"]
        CalcASF --> RetMinASF["Trả về cá thể<br/>có ASF NHỎ HƠN"]
    end
    
    subgraph "Select Best (Môi trường)"
        StartSel(["Bắt đầu Environment Selection"]) --> Merge["Tính Rank và Crowding Distance<br/>cho tập N_sol * 2"]
        Merge --> IdentifyDups["Xác định các cá thể trùng lặp<br/>(Duplicate Penalty)"]
        IdentifyDups --> CustomSort["Sort toàn bộ cá thể theo thứ tự:<br/>1. Số route nhỏ hơn<br/>2. Flag Không trùng lặp<br/>3. Rank nhỏ hơn<br/>4. -Crowding Distance (CD lớn)"]
        CustomSort --> Cut["Cắt chóp N_sol cá thể đầu tiên"]
    end

    classDef decision fill:#ff9,stroke:#333,stroke-width:2px;
    class CmpRoutes decision;
```

---

## 4. Lưu đồ Toán tử SSO (Squirrel Search Update)

Thao tác mô phỏng chú Sóc đang bay nhảy, giúp thuật toán khám phá và khai thác không gian lời giải.

```mermaid
flowchart TD
    Start(["SSO Update"]) --> LoopNodes["Duyệt qua từng node<br/>trên cá thể hiện tại"]
    
    LoopNodes --> GenRand["Sinh biến số ngẫu nhiên<br/>Rho trong khoảng (0, 1)"]
    
    GenRand --> CheckCg{"Rho <= C_g<br/>(VD: 0.95)?"}
    
    CheckCg -- Có --> CopyGBest["Trực tiếp COPY node tương ứng<br/>từ cá thể gBest"]
    
    CheckCg -- Không --> CheckCw{"Rho <= C_w<br/>(VD: 0.99)?"}
    
    CheckCw -- Có --> Keep["Giữ NGUYÊN trạng thái node<br/>không thay đổi"]
    
    CheckCw -- Không --> Random["Tạo node MỚI<br/>khởi tạo Random toàn phần"]
    
    CopyGBest --> NextNode["Chuyển qua node tiếp"]
    Keep --> NextNode
    Random --> NextNode
    
    NextNode --> CheckLoopEnd{"Duyệt xong?"}
    
    CheckLoopEnd -- Chưa --> LoopNodes
    CheckLoopEnd -- Rồi --> Decode["Tiến hành giải mã (Decode)<br/>chuỗi Continuous -> các Routes"]
    Decode --> End(["Trả về giải pháp Con"])

    classDef decision fill:#ff9,stroke:#333,stroke-width:2px;
    class CheckCg,CheckCw,CheckLoopEnd decision;
```

---

## 5. Lưu đồ ABS Search (A*-Based / Destroy & Rebuild)

Toán tử phá hủy một phần chiếc xe và xây lại để sửa dần các khiếm khuyết trong vùng lân cận. Đây là vùng có gắn Preference để đẩy xe theo tham số Weight Vector.

```mermaid
flowchart TD
    Start(["Bắt đầu ABS"]) --> Destroy["Chọn Chiến lược Phá hủy<br/>(Destroy)"]
    
    Destroy --> D1{"Hệ số Random < 0.4?"}
    D1 -- Có --> WorstRem["Worst Removal:<br/>Phá các cụm có cost tệ nhất"]
    D1 -- Không --> RouteRem["Route Removal:<br/>Phá toàn bộ 1 tuyến có ít khách"]
    
    WorstRem --> Pool["Danh sách khách hàng mồ côi<br/>(Unassigned pool)"]
    RouteRem --> Pool
    
    Pool --> Rebuild["Xây dựng lại các xe bị hỏng"]
    Rebuild --> CalcCost["Tính hàm điểm số<br/>(Composite Score f)"]
    CalcCost --> Heuristic["f = w1*Khoảng cách<br/>+ w2*Thời gian chờ kẹt chốt<br/>+ w3*Độ chênh lệch"]
    Heuristic --> BestInsert["Tiến hành Insert Node<br/>vào vị trí làm điểm f Tăng ít nhất"]
    
    BestInsert --> RemPool{"Còn khách mồ côi?"}
    RemPool -- Có --> Rebuild
    
    RemPool -- Không --> Smooth["Đẩy nhẹ 2-opt vào các route<br/>vừa sinh ra để làm mịn mượt"]
    Smooth --> Encode["Mã hóa lại<br/>từ Routes -> Continuous Key"]
    Encode --> End(["Trả về cá thể ABS"])

    classDef decision fill:#ff9,stroke:#333,stroke-width:2px;
    class D1,RemPool decision;
```

---

## 6. Lưu đồ Cập nhật Archive (Epsilon-dominance)

Để giới hạn kho lưu trữ không bị phình to (tốn RAM) mà vẫn đảm bảo tính bao phủ (Diversity), Epsilon-dominance được sử dụng kết hợp với ASF.

```mermaid
flowchart TD
    Start(["Cập nhật Archive"]) --> BoxMem["Chiếu tất cả cá thể có sẵn<br/>trong lưới không gian Epsilon"]
    
    BoxMem --> LoopCand["Duyệt qua từng Candidate<br/>từ Offspring"]
    LoopCand --> GetCandBox["Chiếu Candidate vào<br/>thùng (Ɛ-box) tương ứng"]
    
    GetCandBox --> CompMem{"Thùng Ɛ-box đã<br/>có sẵn cá thể?"}
    
    CompMem -- Có --> CmpASF{"Candidate ASF < Lời giải cũ?"}
    CmpASF -- Có --> Replace["XÓA lời giải cũ<br/>thêm Candidate mới"]
    CmpASF -- Không --> Skip["Vứt bỏ Candidate"]
    
    CompMem -- Không (Thùng trống) --> StrictDom{"Có bị Dominate toàn phần<br/>bởi cá thể nào khác?"}
    
    StrictDom -- Có --> Skip
    StrictDom -- Không --> ClearWorse["Thêm Candidate.<br/>Xóa tất cả cá thể cũ bị<br/>Candidate mới Dominate"]
    
    Replace --> NextCand["Cá thể tiếp"]
    Skip --> NextCand
    ClearWorse --> NextCand
    
    NextCand --> EndCand{"Hết Candidate?"}
    EndCand -- Chưa --> LoopCand
    
    EndCand -- Rồi --> CheckSize{"Số lượng Archive<br/>> Max_size?"}
    CheckSize -- Có --> Prune["Cắt ngọn Archive (Pruning)<br/>Giữ lại Max_size cá thể có ASF nhỏ nhất"]
    CheckSize -- Không --> End(["Hoàn tất cập nhật"])
    Prune --> End

    classDef decision fill:#ff9,stroke:#333,stroke-width:2px;
    class CompMem,CmpASF,StrictDom,EndCand,CheckSize decision;
```
