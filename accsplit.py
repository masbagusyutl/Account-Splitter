import os
import shutil
import math
from pathlib import Path
from colorama import Fore, Style, init

# Inisialisasi colorama
init(autoreset=True)

def print_welcome_message():
    print(Fore.WHITE + r"""
_  _ _   _ ____ ____ _    ____ _ ____ ___  ____ ____ ___ 
|\ |  \_/  |__| |__/ |    |__| | |__/ |  \ |__/ |  | |__]
| \|   |   |  | |  \ |    |  | | |  \ |__/ |  \ |__| |         
          """)
    print(Fore.GREEN + Style.BRIGHT + "Account Splitter")
    print(Fore.YELLOW + Style.BRIGHT + "Telegram: https://t.me/nyariairdrop")

def list_items(folder_path):
    """Membagi isi folder menjadi daftar file dan folder."""
    folder = Path(folder_path)
    files = [f.name for f in folder.iterdir() if f.is_file()]
    folders = [d.name for d in folder.iterdir() if d.is_dir()]
    return files, folders

def get_valid_input(prompt, input_type=int, condition=lambda x: True, error_msg="Input tidak valid."):
    """Meminta input dari pengguna dengan validasi."""
    while True:
        try:
            value = input_type(input(Fore.YELLOW + prompt))
            if condition(value):
                return value
            else:
                print(Fore.RED + error_msg)
        except ValueError:
            print(Fore.RED + error_msg)

def choose_items_to_copy(script_folder, folders, files, main_data_file):
    """
    Memilih file atau folder tambahan untuk disalin, dengan opsi menyalin semua item tambahan
    hanya dengan mengetik angka 0.
    """
    # Eksklusi file data utama dari daftar
    filtered_files = [file for file in files if file != main_data_file]
    all_items = folders + filtered_files

    print(Fore.CYAN + "\nItem tambahan yang tersedia untuk disalin (kecuali file data utama):")
    print(Fore.CYAN + "---------------------------------------")
    print(Fore.CYAN + "| No  | Jenis  | Nama                 |")
    print(Fore.CYAN + "---------------------------------------")
    for idx, folder_name in enumerate(folders, start=1):
        print(Fore.CYAN + f"| {idx:<3} | Folder | {folder_name:<20} |")
    for idx, file_name in enumerate(filtered_files, start=len(folders) + 1):
        print(Fore.CYAN + f"| {idx:<3} | File   | {file_name:<20} |")
    print(Fore.CYAN + "---------------------------------------")
    print(Fore.CYAN + "|  0  | Semua  | Salin semua item     |")
    print(Fore.CYAN + "---------------------------------------")

    print(Fore.YELLOW + "Contoh:")
    print(Fore.YELLOW + "  - Jika ingin menyalin satu item, masukkan: 3")
    print(Fore.YELLOW + "  - Untuk memilih semua item, ketik: 0")
    print(Fore.YELLOW + "  - Untuk memilih beberapa item, masukkan nomor yang dipisahkan dengan koma: 2,3,5")
    print(Fore.YELLOW + "  - Tekan Enter jika tidak ingin menyalin apa pun.")

    while True:
        copy_item_indices = input(Fore.YELLOW + "Pilih nomor file atau folder untuk disalin: ").strip()
        if not copy_item_indices:
            return []  # Tidak ada yang dipilih
        if copy_item_indices == "0":
            # Pilih semua item tambahan
            return list(range(len(all_items)))

        try:
            selected_indices = [int(idx.strip()) - 1 for idx in copy_item_indices.split(",")]

            if any(idx < 0 or idx >= len(all_items) for idx in selected_indices):
                print(Fore.RED + "Satu atau lebih nomor yang dimasukkan tidak valid. Ulangi input.")
                continue

            return selected_indices
        except ValueError:
            print(Fore.RED + "Input tidak valid. Masukkan angka yang dipisahkan dengan koma atau ketik '0'.")

def display_confirmation(data_item_name, total_lines, total_accounts, accounts_per_folder, method, method_value, folders, files, selected_indices):
    """Menampilkan informasi konfirmasi kepada pengguna sebelum proses dimulai."""
    total_folders = math.ceil(total_accounts / accounts_per_folder)
    last_folder_accounts = total_accounts % accounts_per_folder if total_accounts % accounts_per_folder != 0 else accounts_per_folder

    print(Fore.BLUE + "\nRincian yang akan dihasilkan:")
    print(Fore.CYAN + f"- File data utama: {data_item_name}")
    print(Fore.CYAN + f"- Total akun dalam file (sebelum pembagian): {total_accounts}")
    print(Fore.CYAN + f"- Akun per folder (hasil pembagian): {accounts_per_folder}")
    print(Fore.CYAN + f"- Total folder yang akan dibuat: {total_folders}")
    print(Fore.CYAN + f"- Akun di folder terakhir: {last_folder_accounts}")

    if method == 1:
        print(Fore.CYAN + f"- Metode: Pembagian berdasarkan jumlah folder ({method_value} folder)")
    elif method == 2:
        print(Fore.CYAN + f"- Metode: Pembagian berdasarkan waktu maksimal per folder ({method_value} menit)")

    # Eksklusi file data utama dari tampilan konfirmasi
    filtered_files = [file for file in files if file != data_item_name]
    all_items = folders + filtered_files

    if selected_indices:
        print(Fore.CYAN + "\nItem tambahan yang akan disalin:")
        for idx in selected_indices:
            item_type = "Folder" if idx < len(folders) else "File"
            item_name = all_items[idx]
            print(Fore.CYAN + f"- {item_type}: {item_name}")
    else:
        print(Fore.YELLOW + "\nTidak ada file atau folder tambahan yang akan disalin.")

    proceed = input(Fore.YELLOW + "\nApakah Anda ingin melanjutkan? (y/n): ").strip().lower()
    if proceed != 'y':
        print(Fore.RED + "Proses dibatalkan oleh pengguna.")
        return False
    return True

def suggest_valid_inputs(time_per_account, max_time_per_file, total_accounts):
    """
    Memberikan rekomendasi input valid untuk waktu per akun dan waktu maksimal.
    """
    min_time_per_account = 0.5  # Batas minimal waktu per akun
    min_max_time = time_per_account * 2  # Batas minimal waktu maksimal

    if time_per_account < min_time_per_account:
        print(Fore.YELLOW + f"\nWaktu per akun terlalu kecil ({time_per_account:.2f} menit).")
        print(Fore.GREEN + f"Rekomendasi: Gunakan minimal {min_time_per_account} menit per akun.")

    if max_time_per_file <= time_per_account:
        print(Fore.YELLOW + f"\nWaktu maksimal per folder terlalu kecil ({max_time_per_file:.2f} menit).")
        print(Fore.GREEN + f"Rekomendasi: Gunakan waktu maksimal minimal {min_max_time:.2f} menit.")

    # Estimasi hasil logis berdasarkan jumlah akun
    estimated_folders = math.ceil(total_accounts / 10)  # Misal, rata-rata 10 akun per folder
    estimated_accounts_per_folder = max(1, total_accounts // estimated_folders)
    estimated_time_per_folder = estimated_accounts_per_folder * time_per_account

    print(Fore.CYAN + f"\nContoh konfigurasi yang valid:")
    print(Fore.CYAN + f"- Waktu per akun: {max(min_time_per_account, time_per_account):.2f} menit.")
    print(Fore.CYAN + f"- Total waktu per folder: {max(min_max_time, estimated_time_per_folder):.2f} menit.")
    print(Fore.CYAN + f"- Perkiraan jumlah folder: {estimated_folders}.")
    print(Fore.CYAN + f"- Akun per folder: {estimated_accounts_per_folder}.")

def split_data_to_numbered_folders(script_folder):
    print_welcome_message()

    files, folders = list_items(script_folder)

    print(Fore.CYAN + "\nFile yang tersedia di folder:")
    for idx, file_name in enumerate(files, start=1):
        print(Fore.CYAN + f"{idx}. {file_name}")

    data_item_idx = get_valid_input(
        "Pilih nomor file yang akan dibagi: ",
        int,
        lambda x: 0 <= x - 1 < len(files),
        "Nomor tidak valid. Pilih nomor dari daftar di atas."
    ) - 1

    data_item_name = files[data_item_idx]
    data_item_path = os.path.join(script_folder, data_item_name)
    print(Fore.GREEN + f"\nAnda memilih file: {data_item_name}")

    # Input parameter pembagian
    lines_per_account = get_valid_input(
        "Di file data akun ini, aturan 1 akun berapa baris? ",
        int,
        lambda x: x > 0,
        "Input harus angka positif."
    )

    print(Fore.CYAN + "\nPilih metode pembagian:")
    print(Fore.CYAN + "1. Berdasarkan jumlah folder yang diinginkan.")
    print(Fore.CYAN + "2. Berdasarkan waktu maksimal per folder.")
    method = get_valid_input(
        "Masukkan pilihan (1/2): ",
        int,
        lambda x: x in [1, 2],
        "Pilihan tidak valid. Masukkan 1 atau 2."
    )

    with open(data_item_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    total_lines = len(lines)
    accounts = [lines[i:i + lines_per_account] for i in range(0, len(lines), lines_per_account)]
    total_accounts = len(accounts)

    if method == 1:
        num_folders = get_valid_input(
            f"Berapa jumlah folder yang ingin dibuat? (Maksimum {total_accounts} folder): ",
            int,
            lambda x: 0 < x <= total_accounts,
            f"Jumlah folder harus antara 1 hingga {total_accounts}."
        )
        accounts_per_folder = math.ceil(total_accounts / num_folders)
        method_value = num_folders
    else:
        time_per_account = get_valid_input(
            "Perkiraan 1 akun butuh berapa menit untuk selesai di proses? ",
            float,
            lambda x: x > 0,
            "Input harus angka positif."
        )
        max_time_per_file = get_valid_input(
            "Berapa total waktu maksimal per folder yang diinginkan (dalam menit)? ",
            float,
            lambda x: x > 0,
            "Input harus angka positif."
        )

        # Hitung jumlah akun per folder, pastikan tidak nol
        accounts_per_folder = math.floor(max_time_per_file / time_per_account)
        if accounts_per_folder <= 0:
            print(Fore.RED + "\nKonfigurasi waktu tidak valid.")
            suggest_valid_inputs(time_per_account, max_time_per_file, total_accounts)
            return  # Keluar dari fungsi jika konfigurasi tidak valid

        method_value = max_time_per_file

    # Panggilan fungsi choose_items_to_copy dengan argumen tambahan
    selected_indices = choose_items_to_copy(script_folder, folders, files, data_item_name)

    if not display_confirmation(data_item_name, total_lines, total_accounts, accounts_per_folder, method, method_value, folders, files, selected_indices):
        return

    folder_number = 1
    base_folder_name = Path(script_folder).stem  # Gunakan nama folder asli
    created_folders = []
    for i in range(0, total_accounts, accounts_per_folder):
        target_folder = os.path.join(script_folder, f"{base_folder_name}{folder_number}")
        os.makedirs(target_folder, exist_ok=True)
        created_folders.append(target_folder)

        output_file_path = os.path.join(target_folder, data_item_name)
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            for account in accounts[i:i + accounts_per_folder]:
                output_file.writelines(account)

        for idx in selected_indices:
            if idx < len(folders):
                shutil.copytree(os.path.join(script_folder, folders[idx]), os.path.join(target_folder, folders[idx]))
            else:
                filtered_files = [file for file in files if file != data_item_name]
                shutil.copy(os.path.join(script_folder, filtered_files[idx - len(folders)]), target_folder)

        folder_number += 1

    print(Fore.GREEN + f"\nPembagian selesai. Total akun: {total_accounts}.")
    print(Fore.GREEN + f"Data dibagi menjadi {len(created_folders)} folder.")
    for idx, folder in enumerate(created_folders, start=1):
        print(Fore.CYAN + f"{idx}. {folder}")

def main():
    script_folder = input(Fore.YELLOW + "Masukkan alamat folder script yang data akunnya ingin dibagi: ")
    if not os.path.exists(script_folder):
        print(Fore.RED + "Folder tidak ditemukan. Pastikan alamat folder benar.")
        return
    split_data_to_numbered_folders(script_folder)

if __name__ == "__main__":
    main()
