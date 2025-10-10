from pytubefix import YouTube 
import stable_whisper 
import os 
import re 
import sys


OUTPUT_DIR = "subtitles_output"
MODEL_SIZE = "medium"

def clean_filename(name: str) -> str:
    cleanedName = re.sub(r'[\\/:*?"<>|]', '', name)
    return cleanedName.strip()[:100]


# Đảm bảo hàm clean_filename đã được định nghĩa ở trên

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

def transcribe_and_save_srt(audio_path: str, model_size: str, output_dir: str):
    print(f" Using {model_size} to transcribe...")
    
    try:
        model = stable_whisper.load_model(model_size) 
        print("Processing transcription... This may take a while.")
        result = model.transcribe(
                audio_path, 
            language='en',
        ) 
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        srt_output_path_temp = os.path.join(output_dir, f"{base_name}_temp.srt")
        srt_output_path = os.path.join(output_dir, f"{base_name}.srt")
        result.split_by_punctuation(punctuation='.,?!') 
        result.to_srt_vtt(srt_output_path_temp) 

        with open(srt_output_path_temp, 'r', encoding='utf-8') as f:
            srt_content = f.read()

        cleaned_content = re.sub(r'<font[^>]*>|</font>', '', srt_content)
        with open(srt_output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        os.remove(srt_output_path_temp)
        
        print(f"✅ Hoàn thành! File SRT đã lưu tại: {srt_output_path}")

    except RuntimeError as e:
        if "MPS not available" in str(e):
             print(f"⚠️ Lỗi MPS: Không tìm thấy GPU (device='mps'). Hãy đảm bảo đã cài đặt PyTorch đúng.")
             print("Thử chạy lại bằng CPU (xóa device='mps') hoặc tham khảo hướng dẫn cài đặt PyTorch/Apple Silicon.")
        else:
            raise e
    except Exception as e:
        print(f"❌ Lỗi trong quá trình phiên âm: {e}")

def main():
    print("--- Automatic SRT - Making ---")
    url = input("Please enter your URL: ").strip()
    
    if not url:
        print("URL must not be empty!")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    audio_file = ""
    try:
        audio_result_tuple = download_audio(url, OUTPUT_DIR)
        audio_file_path = audio_result_tuple[0]
        transcribe_and_save_srt(audio_file_path, MODEL_SIZE, OUTPUT_DIR)
    except Exception as e:
        print(f"❌ Đã xảy ra lỗi: {e}")
    
    finally:
        if audio_file_path and os.path.exists(audio_file_path):
            os.remove(audio_file_path)
            print(f"✅ Đã xóa file audio tạm: {os.path.basename(audio_file_path)}")


if __name__ == "__main__":
    main()