from pytubefix import YouTube
import subprocess
import os
import re
import sys

# --- CONFIGURATION (CẤU HÌNH) ---
OUTPUT_DIR = "subtitles_output"
MODEL_SIZE = "small"  # Đổi lên "medium" để tăng độ chính xác (base -> medium)
LYRICS_FILE_NAME = "ifonly.txt" # Tên file lyrics
HALLU_DIR = "WhisperHallu"
SYNC_DIR = "WhisperTimeSync"
SYNC_VENV_PYTHON = os.path.join(SYNC_DIR, "venv", "bin", "python")  # Python trong venv của WhisperTimeSync

# Thông tin về model size và RAM requirements
MODEL_RAM_INFO = {
    "tiny": "~1GB RAM, tốc độ nhanh, độ chính xác thấp",
    "base": "~1GB RAM, tốc độ nhanh, độ chính xác khá",
    "small": "~2GB RAM, tốc độ trung bình, độ chính xác tốt",
    "medium": "~5GB RAM, tốc độ chậm, độ chính xác rất tốt",
    "large": "~10GB RAM, tốc độ rất chậm, độ chính xác xuất sắc"
}

# --- UTILITIES (HÀM TIỆN ÍCH) ---
def clean_filename(name: str) -> str:
    cleanedName = re.sub(r'[\\/:*?"<>|]', '', name)
    return cleanedName.strip()[:100]


def download_audio(url: str, output_path: str) -> tuple[str, str]:
    try:
        yt = YouTube(url) 
        
        video_title = clean_filename(yt.title)
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        
        if not audio_stream:
            raise Exception("Không tìm thấy luồng audio khả dụng.")
            
        downloaded_file = audio_stream.download(
            output_path=output_path, 
            filename=f"{video_title}.{audio_stream.subtype}"
        )
        print(f"✅ Tải xuống hoàn tất: {os.path.basename(downloaded_file)}")
        
        return downloaded_file, video_title
        
    except Exception as e:
        print(f"❌ Lỗi khi tải xuống (PyTubeFix): {e}")
        sys.exit(1)

def run_alignment_process(audio_path, lyrics_path, video_title):
    print("\n=======================================================")
    print(" BẮT ĐẦU QUY TRÌNH FORCED ALIGNMENT CHUYÊN SÂU")
    print("=======================================================")
    print(f"⚙️  Model size: {MODEL_SIZE} ({MODEL_RAM_INFO.get(MODEL_SIZE, 'Unknown')})")
    
    # 1. Tên file output trung gian
    audio_stem = os.path.splitext(os.path.basename(audio_path))[0]
    
    # Tên file SRT cuối cùng (dùng văn bản từ lyrics_path)
    final_srt_name = f"{video_title}_aligned.srt"
    final_srt_path = os.path.join(OUTPUT_DIR, final_srt_name)
    
    # ----------------------------------------------
    # GIAI ĐOẠN 1 & 2: TẠO DẤU THỜI GIAN NHUYỄN (WHISPERHALLU)
    # ----------------------------------------------
    hallu_output_path = os.path.join(OUTPUT_DIR, f"{audio_stem}_hallu_timing.srt")
    
    try:
        print("\nĐang chạy WhisperHallu để tạo Timing Source...")
        
        # đoạn này là chuẩn bị để chạy Hallu
        hallu_command = [
            sys.executable,  # Đảm bảo dùng đúng phiên bản python
            os.path.join(HALLU_DIR, "transcribeHallu.py"), 
            "--input", audio_path, 
            "--output", OUTPUT_DIR,
            "--model", MODEL_SIZE,
            "--language", "en" 
        ]
        
        # Chạy nè
        subprocess.run(hallu_command, check=True, capture_output=True, text=True)
        print("✅  Đã tạo Timing Source (cấp độ từ).")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi chạy WhisperHallu (Giai đoạn 1/2). Kiểm tra file log/cấu hình tool!")
        print(f"Chi tiết lỗi:\n{e.stderr}")
        return
        
    # ----------------------------------------------
    # GIAI ĐOẠN 3: TRANSCRIBE VỚI WHISPER
    # ----------------------------------------------
    
    try:
        print("\n[GIAI ĐOẠN 3] Đang chạy WhisperTimeSync để align lyrics với audio...")
        print(f"💡 Đang sử dụng model '{MODEL_SIZE}' - {MODEL_RAM_INFO.get(MODEL_SIZE, '')}")
        print(f"📝 Lyrics file: {lyrics_path}")
        
        # Gọi transcribe.py với đúng tham số: <audio_file> <lyrics_file> <model_size>
        sync_command = [
            SYNC_VENV_PYTHON,  # Dùng Python từ venv của WhisperTimeSync
            os.path.join(SYNC_DIR, "transcribe.py"), 
            audio_path,      # Tham số 1: file audio
            lyrics_path,     # Tham số 2: file lyrics chuẩn
            MODEL_SIZE       # Tham số 3: kích thước model
        ]

        result = subprocess.run(sync_command, check=True, capture_output=True, text=True)
        print(result.stdout)  # In output từ transcribe.py
        print("✅ Giai đoạn 3 hoàn tất. Đã tạo file SRT với lyrics chuẩn + timestamps.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi chạy WhisperTimeSync (Giai đoạn 3).")
        print(f"Chi tiết lỗi:\n{e.stderr}")
        print(f"\n💡 GỢI Ý: Nếu bị lỗi RAM, hãy thử model nhỏ hơn:")
        print(f"   - Sửa MODEL_SIZE = 'tiny' hoặc 'base' trong main.py")
        return

    print("\n--- ✅ QUY TRÌNH ALIGNMENT HOÀN TẤT ---")
    print(f"⭐ File SRT chính xác của bạn nằm ở: {final_srt_path}")
    print("------------------------------------------")



# --- MAIN LOGIC (Điều phối Quy trình Alignment) ---
def main():
    print("--- Pure Forced Alignment Project ---")
    url = input("Vui lòng nhập Link YouTube (URL): ").strip()
    
    if not url:
        print("URL must not be empty!")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    audio_file_path = ""
    try:
        # B1: Tải file audio
        print("\n⏳ Đang tải audio từ YouTube...")
        audio_result_tuple = download_audio(url, OUTPUT_DIR) 
        print("✅ Audio đã được tải xuống thành công.")
        audio_file_path = audio_result_tuple[0] 
        video_title = audio_result_tuple[1]

        # B2: KIỂM TRA FILE LYRICS (Bước mới quan trọng)
        lyrics_path = os.path.join(OUTPUT_DIR, LYRICS_FILE_NAME)
        if not os.path.exists(lyrics_path):
            print("\n=======================================================")
            print(f"🛑 BƯỚC QUAN TRỌNG: Vui lòng tạo file Lyrics.")
            print(f"   Tạo file: {lyrics_path}")
            print("   Điền lời bài hát chính xác vào đó (mỗi câu/đoạn một dòng mới).")
            print("   Sau đó, chạy lại chương trình.")
            print("=======================================================")
            return
        
        print(f"✅ Đã tìm thấy file Lyrics tại: {LYRICS_FILE_NAME}")
        
        # B3: TRIỂN KHAI LOGIC FORCED ALIGNMENT TẠI ĐÂY
        
        print("\n⏳ Quá trình Alignment chuyên sâu sẽ bắt đầu...")
        run_alignment_process(audio_file_path, lyrics_path, video_title)

    except Exception as e:
        print(f"❌ Đã xảy ra lỗi: {e}")
    
    finally:
        # Giữ lại logic xóa file tạm
        if audio_file_path and os.path.exists(audio_file_path):
            os.remove(audio_file_path)
            print(f"✅ Đã xóa file audio tạm: {os.path.basename(audio_file_path)}")


if __name__ == "__main__":
    main()