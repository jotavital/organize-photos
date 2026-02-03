import sys
import os
from os.path import join, splitext, exists, getmtime, getctime, abspath
import platform
from datetime import datetime
import subprocess
import json
import time
from PIL import Image as PilImage
import piexif
from pillow_heif import register_heif_opener

register_heif_opener()


def get_bundled_resource_path(filename):
    if hasattr(sys, "_MEIPASS"):
        return join(sys._MEIPASS, filename)
    else:
        return join(abspath("."), filename)


class PhotoOrganizerCore:
    def __init__(self):
        self.image_extensions = [
            ".JPG",
            ".JPEG",
            ".HEIC",
            ".PNG",
            ".JFIF",
            ".DNG",
            ".WEBP",
        ]
        self.video_extensions = [".MOV", ".MP4", ".M4V", ".AVI", ".GIF", ".MKV"]
        self.all_extensions = self.image_extensions + self.video_extensions

    def get_resource_path(self, filename):
        return get_bundled_resource_path(filename)

    def scan_directory(self, path, selected_extensions):
        files_found = []
        if not path or not exists(path):
            return []

        for root, dirs, file_list in os.walk(path):
            for f in file_list:
                if f.upper().endswith(tuple(selected_extensions)):
                    files_found.append(join(root, f))
        return files_found

    def get_date_from_ffprobe(self, file_path):
        try:
            ffprobe_path = get_bundled_resource_path(join("bin", "ffprobe.exe"))

            cmd = [
                ffprobe_path,
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                file_path,
            ]

            startupinfo = None
            if platform.system() == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            result = subprocess.run(
                cmd, capture_output=True, text=True, startupinfo=startupinfo
            )
            data = json.loads(result.stdout)

            date_str = None

            if "format" in data and "tags" in data["format"]:
                tags = data["format"]["tags"]
                if "creation_time" in tags:
                    date_str = tags["creation_time"]
                elif "date" in tags:
                    date_str = tags["date"]

            if not date_str and "streams" in data:
                for stream in data["streams"]:
                    if "tags" in stream and "creation_time" in stream["tags"]:
                        date_str = stream["tags"]["creation_time"]
                        break

            if date_str:
                try:
                    return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except ValueError:
                    formats = [
                        "%Y-%m-%d %H:%M:%S",
                        "%Y-%m-%dT%H:%M:%S.%f",
                        "%Y-%m-%dT%H:%M:%S",
                    ]
                    for fmt in formats:
                        try:
                            return datetime.strptime(
                                date_str.split(".")[0], fmt.split(".")[0]
                            )
                        except ValueError:
                            continue
            return None
        except Exception:
            return None

    def get_smart_date(self, file_path):
        file_extension = splitext(file_path)[1].upper()
        date_taken = None

        if file_extension in self.video_extensions:
            date_taken = self.get_date_from_ffprobe(file_path)

        if not date_taken and file_extension in self.image_extensions:
            try:
                img = PilImage.open(file_path)
                if "exif" in img.info:
                    exif_dict = piexif.load(img.info["exif"])
                    tags_to_check = [
                        ("Exif", 36867),
                        ("Exif", 36868),
                        ("Exif", 306),
                        ("0th", 306),
                    ]
                    for group, tag_id in tags_to_check:
                        if tag_id in exif_dict.get(group, {}):
                            try:
                                val = exif_dict[group][tag_id].decode("utf-8")
                                if val and val != "0000:00:00 00:00:00":
                                    date_taken = datetime.strptime(
                                        val, "%Y:%m:%d %H:%M:%S"
                                    )
                                    break
                            except:
                                continue
            except Exception:
                pass

        if date_taken:
            return date_taken

        mtime = getmtime(file_path)
        timestamp = mtime
        if platform.system() == "Windows":
            try:
                ctime = getctime(file_path)
                timestamp = min(ctime, mtime)
            except:
                pass

        return datetime.fromtimestamp(timestamp)

    def process_renaming(
        self, files, base_path, organize_by_year, progress_callback, stop_event
    ):
        if not exists("logs"):
            os.makedirs("logs")

        log_file = open(
            f"./logs/log-{datetime.now().strftime('%Y-%m-%d')}.txt",
            "a",
            encoding="utf-8",
        )
        files_renamed = 0
        total_files = len(files)
        start_time = time.time()

        for index, file_path in enumerate(files):
            if stop_event.is_set():
                break

            try:
                file_extension = splitext(file_path)[1]
                file_name_original = (
                    splitext(file_path)[0].split(os.sep)[-1] + file_extension
                )

                elapsed_time = time.time() - start_time
                items_processed = index + 1
                avg_time_per_item = elapsed_time / items_processed
                remaining_items = total_files - items_processed
                est_time_remaining = avg_time_per_item * remaining_items

                progress_callback(
                    index + 1,
                    total_files,
                    file_name_original,
                    elapsed_time,
                    est_time_remaining,
                )

                dt_obj = self.get_smart_date(file_path)

                if dt_obj:
                    formatted_date = dt_obj.strftime("%Y-%m-%d %H-%M-%S")
                    year = dt_obj.year

                    target_folder = base_path
                    if organize_by_year:
                        target_folder = join(base_path, str(year))
                        if not exists(target_folder):
                            os.makedirs(target_folder)

                    final_name = f"{formatted_date}{file_extension}"
                    final_path = join(target_folder, final_name)

                    if (
                        os.path.normpath(file_path).lower()
                        != os.path.normpath(final_path).lower()
                    ):
                        count = 0
                        while True:
                            if not exists(final_path):
                                os.rename(file_path, final_path)
                                files_renamed += 1
                                break
                            elif os.path.samefile(file_path, final_path):
                                break
                            else:
                                count += 1
                                final_name = (
                                    f"{formatted_date} ({count}){file_extension}"
                                )
                                final_path = join(target_folder, final_name)
            except Exception as e:
                log_file.write(f"Error {file_path}: {e}\n")

        log_file.close()
        return files_renamed
