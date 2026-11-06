# Tài liệu tham khảo đã tải (ngày tải: 2026-10-01)

File PDF/zip nằm trong `.gitignore`; tải lại bằng các link dưới đây.

## Đã tải và kiểm tra (PDF đủ, có `%%EOF`)
| File | Nguồn |
|---|---|
| papers/01_mongardini_mei_midsummer_meme_2026.pdf | https://www.usenix.org/system/files/usenixsecurity26-mongardini.pdf |
| papers/02_victor_weintraud_wash_trading_dex_2021.pdf | https://arxiv.org/pdf/2102.07001 |
| papers/03_la_morgia_game_of_nfts_2023.pdf | https://arxiv.org/pdf/2212.01225 |
| papers/04_xu_livshits_pump_dump_anatomy_2019.pdf | https://arxiv.org/pdf/1811.10109 |
| papers/05_cernera_token_spammers_rug_pulls_2023.pdf | https://arxiv.org/pdf/2206.08202 |
| papers/06_mazorra_do_not_rug_on_me_2022.pdf | https://arxiv.org/pdf/2201.07220 (bản arXiv; bản tạp chí: https://doi.org/10.3390/math10060949) |
| papers/08_zhou_stop_pulling_my_rug_2024.pdf | http://www.wingtecher.com/themes/WingTecherResearch/assets/papers/Tokeer_CameraReady.pdf |
| papers/10_uniswap_v2_whitepaper.pdf | https://uniswap.org/whitepaper.pdf |
| papers/11_uniswap_v3_whitepaper.pdf | https://uniswap.org/whitepaper-v3.pdf |
| dataset/meme_coin-main.zip (đã giải nén ra `meme_coin_anon-main/`) | https://zenodo.org/records/17830944/files/meme_coin-main.zip?download=1 (CC-BY-4.0, DOI 10.5281/zenodo.17830943) |

## Chưa tải được, cần tải tay
| Paper | Lý do | Link |
|---|---|---|
| 07 Kamps & Kleinberg, *To the Moon* (2018) | Springer/UCL chặn tải tự động | https://link.springer.com/article/10.1186/s40163-018-0093-5 (open access, bấm "Download PDF") |
| 09 Le Pennec, Fiedler & Ante (2021) | SSRN không kết nối được | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3815093 |

## Bản Markdown (để Codex / Claude Code đọc)
- Nằm ở `docs/references/markdown/`, cùng tên với PDF. Tạo lại: `.venv/bin/python scripts/pdf_to_md.py`.
- Bộ chuyển chính: pymupdf4llm (paper 2 cột đọc tốt). Dự phòng: markitdown của Microsoft (nhanh nhưng dính chữ ở paper 2 cột).
- Công thức toán và bảng phức tạp có thể lỗi. **Con số/ngưỡng dùng trong code hoặc báo cáo phải đối chiếu PDF gốc** và ghi trang.
- Cài môi trường: `uv venv --python 3.11 .venv && uv pip install --python .venv/bin/python 'markitdown[pdf]' pymupdf4llm`
